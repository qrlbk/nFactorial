"""Extended API routes for Editorial OS platform features."""

from __future__ import annotations

from fastapi import APIRouter, File, Header, HTTPException, Query, UploadFile

from app.config import get_settings
from app.graph.builder import run_pipeline
from app.graph.nodes.hooks import generate_hooks_for_draft
from app.i18n import normalize_locale
from app.schemas.api import GenerateRequest, GenerateResponse
from app.schemas.platform import (
    DiscoveryResponse,
    HookRequest,
    HookResponse,
    IngestRequest,
    IngestResponse,
    LaunchDraftCreate,
    LaunchItem,
    LaunchListResponse,
    ResearchRunRequest,
    ThesisAnglesResponse,
    UploadResponse,
    VoiceListResponse,
    VoiceProfileCreate,
    VoiceProfileItem,
)
from app.services.content_fetcher import ingest_url
from app.services.discovery import discover
from app.services.distribution.publisher import create_launch_draft, get_publisher, list_launch_queue
from app.services.document_parser import ingest_upload
from app.services.research_workflow import run_autonomous_research
from app.services.trace_enrichment import build_generate_response
from app.services.voice_profiler import create_voice_profile, delete_voice, get_voice, list_voices

platform_router = APIRouter()


def _locale(accept_language: str | None = None) -> str:
    return normalize_locale(accept_language)


@platform_router.get("/discover", response_model=DiscoveryResponse)
async def discover_content(
    source: str = Query("arxiv"),
    q: str = Query(..., min_length=2),
):
    items, cached = await discover(source, q)  # type: ignore[arg-type]
    return DiscoveryResponse(query=q, source=source, items=items, cached=cached)


@platform_router.post("/discover/ingest", response_model=IngestResponse)
async def discover_ingest(body: IngestRequest):
    try:
        doc = await ingest_url(body.url, title=body.title)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return IngestResponse(**doc)


@platform_router.post("/generate/thesis-angles", response_model=ThesisAnglesResponse)
async def generate_thesis_angles(
    request: GenerateRequest,
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    result = await run_pipeline(
        raw_context=request.context,
        mode=request.mode,
        output_language=request.output_language,
        response_locale=_locale(accept_language),
        output_type=request.output_type,
        source_urls=request.source_urls,
        thesis_only=True,
        generate_thesis_angles=True,
        skip_post_pipeline=True,
    )
    return ThesisAnglesResponse(
        trace_id=result.get("trace_id"),
        candidates=result.get("thesis_candidates") or [],
        distilled_context=result.get("distilled_context") or {},
    )


@platform_router.post("/generate/hooks", response_model=HookResponse)
async def generate_hooks(body: HookRequest):
    hooks = await generate_hooks_for_draft(body.draft, thesis=body.thesis)
    return HookResponse(hooks=hooks)


@platform_router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    result = ingest_upload(file.filename, content)
    return UploadResponse(
        file_id=result["file_id"],
        filename=result["filename"],
        chunk_count=result["chunk_count"],
        preview=result["preview"],
    )


@platform_router.get("/voices", response_model=VoiceListResponse)
async def get_voices():
    return VoiceListResponse(voices=[VoiceProfileItem(**v) for v in list_voices()])


@platform_router.post("/voices", response_model=VoiceProfileItem)
async def post_voice(body: VoiceProfileCreate):
    profile = await create_voice_profile(
        name=body.name,
        description=body.description,
        writing_samples=body.writing_samples,
    )
    return VoiceProfileItem(
        id=profile["id"],
        name=profile["name"],
        description=profile.get("description", ""),
        guidelines=profile.get("guidelines", {}),
        created_at=profile.get("created_at", ""),
    )


@platform_router.get("/voices/{voice_id}", response_model=VoiceProfileItem)
async def get_voice_detail(voice_id: str):
    profile = get_voice(voice_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return VoiceProfileItem(
        id=profile["id"],
        name=profile["name"],
        description=profile.get("description", ""),
        guidelines=profile.get("guidelines", {}),
        created_at=profile.get("created_at", ""),
    )


@platform_router.delete("/voices/{voice_id}")
async def remove_voice(voice_id: str):
    if not delete_voice(voice_id):
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return {"deleted": True, "id": voice_id}


@platform_router.post("/launch", response_model=LaunchItem)
async def create_launch(body: LaunchDraftCreate):
    draft = create_launch_draft(
        output_type=body.output_type,
        content=body.content,
        mode=body.mode,
        trace_id=body.trace_id,
        scheduled_at=body.scheduled_at.isoformat() if body.scheduled_at else None,
    )
    settings = get_settings()
    publisher = get_publisher(settings.x_bearer_token)
    if body.scheduled_at:
        await publisher.schedule(draft, body.scheduled_at)
    else:
        await publisher.publish(draft)
    return LaunchItem(**draft)


@platform_router.get("/launch/queue", response_model=LaunchListResponse)
async def get_launch_queue(limit: int = 50):
    items = list_launch_queue(limit=min(limit, 200))
    return LaunchListResponse(items=[LaunchItem(**item) for item in items])


@platform_router.post("/research/run", response_model=GenerateResponse)
async def research_run(
    body: ResearchRunRequest,
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    result = await run_autonomous_research(
        topic=body.topic,
        mode=body.mode,
        output_type=body.output_type,
        output_language=body.output_language,
        response_locale=_locale(accept_language),
        auto_pick_thesis=body.auto_pick_thesis,
        source_urls=body.source_urls,
    )
    return build_generate_response(result, locale=_locale(accept_language))
