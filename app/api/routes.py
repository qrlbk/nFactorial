from fastapi import APIRouter, Header, HTTPException, Query

from app.config import get_settings
from app.graph.builder import run_pipeline
from app.i18n import normalize_locale
from app.schemas.api import (
    GenerateRequest,
    GenerateResponse,
    PublicConfigResponse,
    TemplateCreate,
    TemplateItem,
    TemplateListResponse,
    TraceListItem,
    TraceListResponse,
    TraceResponse,
)
from app.services.local_trace import create_template, delete_template, list_local_traces, list_templates
from app.services.trace_enrichment import build_generate_response, build_public_config, build_trace_response
from app.services.tracing import fetch_trace_summary

router = APIRouter()


def _resolve_locale(
    locale: str | None = None,
    accept_language: str | None = None,
) -> str:
    if locale:
        return normalize_locale(locale)
    return normalize_locale(accept_language)


@router.get("/health")
async def health():
    return {"status": "ok", "service": "adversarial-editorial-engine"}


@router.get("/config", response_model=PublicConfigResponse)
async def get_config(
    locale: str = Query("en"),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    return build_public_config(locale=_resolve_locale(locale, accept_language))


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    response_locale = _resolve_locale(None, accept_language)
    result = await run_pipeline(
        raw_context=request.context,
        mode=request.mode,
        output_language=request.output_language,
        response_locale=response_locale,
        output_type=request.output_type,
        source_urls=request.source_urls,
        selected_thesis_id=request.thesis_id,
        voice_profile_id=request.voice_profile_id,
        quoted_tweet=request.quoted_tweet,
        skip_post_pipeline=request.skip_post_pipeline,
    )
    return build_generate_response(result, locale=response_locale)


@router.get("/trace/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: str,
    locale: str = Query("en"),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    return _build_trace(trace_id, locale=_resolve_locale(locale, accept_language))


@router.get("/traces/{trace_id}", response_model=TraceResponse)
async def get_trace_alias(
    trace_id: str,
    locale: str = Query("en"),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    return _build_trace(trace_id, locale=_resolve_locale(locale, accept_language))


@router.get("/traces", response_model=TraceListResponse)
async def list_traces(limit: int = 50, offset: int = 0):
    items, total = list_local_traces(limit=min(limit, 200), offset=max(offset, 0))
    return TraceListResponse(
        traces=[TraceListItem(**item) for item in items],
        total=total,
    )


@router.get("/templates", response_model=TemplateListResponse)
async def get_templates():
    templates = list_templates()
    return TemplateListResponse(templates=[TemplateItem(**t) for t in templates])


@router.post("/templates", response_model=TemplateItem)
async def post_template(body: TemplateCreate):
    payload = create_template(
        name=body.name,
        description=body.description,
        context=body.context,
        default_mode=body.default_mode,
    )
    return TemplateItem(**payload)


@router.delete("/templates/{template_id}")
async def remove_template(template_id: str):
    if not delete_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"deleted": True, "id": template_id}


def _build_trace(trace_id: str, *, locale: str = "en") -> TraceResponse:
    settings = get_settings()
    summary = fetch_trace_summary(trace_id)

    if summary.get("error") == "Trace not found":
        raise HTTPException(status_code=404, detail="Trace not found")

    langfuse_url = None
    metadata = summary.get("metadata") or {}
    if metadata.get("source") == "langfuse" and settings.langfuse_host:
        host = settings.langfuse_host.rstrip("/")
        langfuse_url = f"{host}/trace/{trace_id}"

    return build_trace_response(trace_id, summary, langfuse_url=langfuse_url, locale=locale)
