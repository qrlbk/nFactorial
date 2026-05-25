from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.platform_routes import platform_router
from app.api.routes import router
from app.config import get_settings
from app.services.storage_paths import ensure_data_dirs

load_dotenv()
ensure_data_dirs()

_settings = get_settings()
_origins = [
    o.strip()
    for o in _settings.allowed_origins.split(",")
    if o.strip()
] or ["*"]

app = FastAPI(
    title="Adversarial Editorial Engine",
    description="Editorial OS — high-insight X content with discovery, voice, fact-checking, and distribution",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(platform_router)
