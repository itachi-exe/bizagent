"""FastAPI app entrypoint. Startup wires the asyncpg pool once; CORS is open for
the Vite dev server only. Run with: uvicorn main:app --port 8000 --reload
"""
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)

from customers.router import router as customers_router
from dashboard.router import router as dashboard_router
from db.connection import close_pool, init_pool
from internal.message_handler import router as message_router
from internal.owner_commands import router as owner_command_router
from internal.voice_handler import router as voice_router
from settings.router import router as settings_router
from upload.router import router as upload_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="BizAgent Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "https://frontend-nine-puce-74.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(message_router)
app.include_router(owner_command_router)
app.include_router(voice_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(upload_router)
app.include_router(customers_router)


@app.get("/health")
async def health():
    from db.connection import get_pool

    db_status = "connected"
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception:
        db_status = "unavailable"

    return {"status": "ok", "db": db_status, "version": "0.1.0"}
