from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import get_settings, resolve_llm_provider

T = TypeVar("T", bound=BaseModel)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

NODE_TEMPERATURES = {
    "research_distiller": 0.4,
    "thesis_commitment": 0.4,
    "thesis_angles_generator": 0.5,
    "anti_slop_critic": 0.3,
    "narrative_architect": 0.7,
    "high_pressure_rewriter": 0.5,
    "qrt_writer": 0.5,
    "essay_writer": 0.6,
    "hook_generator": 0.7,
    "fact_checker": 0.2,
    "voice_profiler": 0.3,
}


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _format_prompt(template: str, variables: dict[str, Any]) -> str:
    result = template
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2, ensure_ascii=False)
        result = result.replace(placeholder, str(value))
    return result


async def invoke_structured(
    *,
    node_name: str,
    prompt_name: str,
    input_vars: dict[str, Any],
    output_schema: type[T],
) -> T:
    settings = get_settings()
    template = load_prompt(prompt_name)
    prompt = _format_prompt(template, input_vars)
    temperature = NODE_TEMPERATURES.get(node_name, 0.5)
    schema_json = json.dumps(output_schema.model_json_schema(), indent=2)

    full_prompt = (
        f"{prompt}\n\n"
        f"Respond with valid JSON matching this schema exactly:\n{schema_json}\n"
        "Return ONLY the JSON object, no markdown fences."
    )

    provider = resolve_llm_provider(settings)
    if provider == "anthropic":
        raw = await _invoke_anthropic(full_prompt, temperature, settings)
    else:
        raw = await _invoke_openai(full_prompt, temperature, settings)

    data = _parse_json_response(raw)
    return output_schema.model_validate(data)


async def _invoke_anthropic(prompt: str, temperature: float, settings: Any) -> str:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


async def _invoke_openai(prompt: str, temperature: float, settings: Any) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=settings.openai_model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"


def _parse_json_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)
