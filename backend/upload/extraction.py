"""Per-format extraction pipeline (section 10.4). Turns a raw uploaded file into
{ products, services, policies } candidates for the owner to review.

The LLM extraction call here is a separate, one-shot structured-output call —
distinct from (and never routed through) the agent engine in agent/engine.py.
"""
import io
import json
import logging
import os

import httpx
import pandas as pd
import pymupdf
from docx import Document

logger = logging.getLogger("bizagent.upload.extraction")

NAME_COLUMNS = {"name", "product", "product_name", "item"}
PRICE_COLUMNS = {"price", "cost", "price_ngn", "unit_price"}
STOCK_COLUMNS = {"stock", "qty", "quantity", "stock_count"}

EXTRACTION_SYSTEM_PROMPT = (
    "Extract products, services, and policies from the given business document text. "
    "Return strict JSON with this exact shape: "
    '{"products": [{"name": str, "price_ngn": number, "stock_count": number, "description": str}], '
    '"services": [{"name": str, "price_ngn": number, "description": str, "availability": str}], '
    '"policies": {"delivery": str, "returns": str}}. '
    "Omit fields you cannot find. If nothing is found for a section, return an empty list/object."
)


def _map_columns(columns: list[str]) -> dict[str, str]:
    mapping = {}
    for col in columns:
        key = col.strip().lower()
        if key in NAME_COLUMNS:
            mapping[col] = "name"
        elif key in PRICE_COLUMNS:
            mapping[col] = "price_ngn"
        elif key in STOCK_COLUMNS:
            mapping[col] = "stock_count"
    return mapping


def extract_from_tabular(raw_bytes: bytes, is_xlsx: bool) -> dict:
    if is_xlsx:
        df = pd.read_excel(io.BytesIO(raw_bytes))
    else:
        df = pd.read_csv(io.BytesIO(raw_bytes))

    mapping = _map_columns(list(df.columns))
    products = []
    for _, row in df.iterrows():
        product = {}
        for col, field in mapping.items():
            value = row[col]
            if pd.isna(value):
                continue
            if field == "price_ngn":
                product[field] = float(value)
            elif field == "stock_count":
                product[field] = int(value)
            else:
                product[field] = str(value)
        if product.get("name"):
            products.append(product)

    raw_text_preview = df.to_string()[:500]
    return {
        "products": products,
        "services": [],
        "policies": {},
        "raw_text_preview": raw_text_preview,
    }


def extract_text_from_pdf(raw_bytes: bytes) -> str:
    doc = pymupdf.open(stream=raw_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_docx(raw_bytes: bytes) -> str:
    doc = Document(io.BytesIO(raw_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


async def extract_via_llm(text: str) -> dict:
    """One-shot structured extraction call. Never tool-calling, never routed through agent.engine."""
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — skipping LLM extraction, returning empty result")
        return {"products": [], "services": [], "policies": {}}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": text[:12000]},
                ],
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
