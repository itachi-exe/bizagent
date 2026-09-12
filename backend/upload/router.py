"""POST /api/upload/database and /api/upload/confirm (section 10.3)."""
import logging

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from dashboard import sse
from db.connection import get_pool
from db.queries import business as business_queries
from db.queries import uploads as upload_queries
from upload import extraction

logger = logging.getLogger("bizagent.upload.router")

router = APIRouter()

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

ALLOWED_TYPES = {
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# Magic-byte prefixes used to validate content matches the declared MIME type.
_ZIP_MAGIC = b"PK\x03\x04"  # .xlsx and .docx are both zip containers
_PDF_MAGIC = b"%PDF"


def _content_matches_type(raw_bytes: bytes, content_type: str) -> bool:
    if content_type == "application/pdf":
        return raw_bytes.startswith(_PDF_MAGIC)
    if content_type in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ):
        return raw_bytes.startswith(_ZIP_MAGIC)
    if content_type == "text/csv":
        try:
            raw_bytes.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    return False


async def _get_business_id(conn) -> str:
    business = await conn.fetchrow("SELECT id FROM businesses LIMIT 1")
    if business is None:
        raise HTTPException(status_code=500, detail="No business configured")
    return str(business["id"])


@router.post("/api/upload/database")
async def upload_database_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")

    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10MB limit")

    if not _content_matches_type(raw_bytes, file.content_type):
        raise HTTPException(status_code=415, detail="File content does not match declared type")

    if file.content_type == "text/csv":
        extracted = extraction.extract_from_tabular(raw_bytes, is_xlsx=False)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        extracted = extraction.extract_from_tabular(raw_bytes, is_xlsx=True)
    elif file.content_type == "application/pdf":
        text = extraction.extract_text_from_pdf(raw_bytes)
        llm_result = await extraction.extract_via_llm(text)
        extracted = {**llm_result, "raw_text_preview": text[:500]}
    else:  # docx
        text = extraction.extract_text_from_docx(raw_bytes)
        llm_result = await extraction.extract_via_llm(text)
        extracted = {**llm_result, "raw_text_preview": text[:500]}

    raw_text_preview = extracted.pop("raw_text_preview", "")

    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        # Strip filename before storing — display name only, never trusted as a path.
        safe_filename = file.filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1] if file.filename else "upload"
        upload_row = await upload_queries.create_upload(
            conn, business_id, safe_filename, file.content_type, extracted
        )

    return {
        "upload_id": str(upload_row["id"]),
        "filename": upload_row["filename"],
        "extracted": extracted,
        "raw_text_preview": raw_text_preview,
    }


class ConfirmUploadBody(BaseModel):
    upload_id: str
    products: list[dict] = []
    services: list[dict] = []
    policies: dict = {}


@router.post("/api/upload/confirm")
async def confirm_upload(body: ConfirmUploadBody):
    pool = get_pool()
    async with pool.acquire() as conn:
        upload_row = await upload_queries.get_upload(conn, body.upload_id)
        if upload_row is None:
            raise HTTPException(status_code=404, detail="Upload not found")

        business_id = str(upload_row["business_id"])

        products_saved = await business_queries.upsert_products(conn, business_id, body.products)
        services_saved = await business_queries.upsert_services(conn, business_id, body.services)
        policies_updated = await business_queries.update_policies(conn, business_id, body.policies)

        await upload_queries.mark_confirmed(conn, body.upload_id)

    await sse.broadcast(
        "brain_updated",
        f"Business Brain updated: {products_saved} products, {services_saved} services",
        {"products_saved": products_saved, "services_saved": services_saved},
    )

    return {
        "products_saved": products_saved,
        "services_saved": services_saved,
        "policies_updated": policies_updated,
    }
