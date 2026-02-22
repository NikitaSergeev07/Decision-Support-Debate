from __future__ import annotations

import json
import random
import time
from typing import Any, Type

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError


def _sanitize_response_schema(value: Any) -> Any:
    """Remove JSON Schema keys unsupported by Gemini response_schema."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        unsupported_keys = {
            "additionalProperties",
            "additional_properties",
            "exclusiveMinimum",
            "exclusive_minimum",
            "exclusiveMaximum",
            "exclusive_maximum",
        }
        for key, item in value.items():
            if key in unsupported_keys:
                continue
            cleaned[key] = _sanitize_response_schema(item)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_response_schema(item) for item in value]
    return value


def _gemini_response_schema(schema: Type[BaseModel]) -> dict[str, Any]:
    """Build a Gemini-compatible schema from a Pydantic model."""
    return _sanitize_response_schema(schema.model_json_schema())


def _parse_jsonish(text: str) -> dict[str, Any]:
    """Parse JSON-ish output, including double-encoded JSON strings."""
    text = text.strip()

    # Attempt 1: direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if not isinstance(parsed, dict):
            raise ValueError("Model output is valid JSON but not a JSON object.")
        return parsed
    except json.JSONDecodeError:
        pass

    # Attempt 2: strip markdown code fences
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first line (``` or ```json) and last line if it's ```
        inner_lines = lines[1:]
        if inner_lines and inner_lines[-1].strip() == "```":
            inner_lines = inner_lines[:-1]
        try:
            parsed = json.loads("\n".join(inner_lines).strip())
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            if not isinstance(parsed, dict):
                raise ValueError("Model output is valid JSON but not a JSON object.")
            return parsed
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Cannot parse JSON from model output: {text[:300]!r}")


def _is_transient_gemini_error(exc: Exception) -> bool:
    """Heuristic check for transient Gemini/API overload or rate-limit errors."""
    text = str(exc).upper()
    transient_markers = (
        "503",
        "UNAVAILABLE",
        "429",
        "RESOURCE_EXHAUSTED",
        "DEADLINE_EXCEEDED",
        "INTERNAL",
    )
    return any(marker in text for marker in transient_markers)


def _is_retryable_output_error(exc: Exception) -> bool:
    """Retry on malformed structured output (often transient or token-limit related)."""
    if isinstance(exc, ValidationError):
        return True
    if isinstance(exc, ValueError):
        text = str(exc)
        markers = (
            "Cannot parse JSON from model output",
            "Model returned no text and no parsed structured output",
        )
        return any(marker in text for marker in markers)
    return False


def _fallback_model_candidates(primary_model: str) -> list[str]:
    """Return ordered unique list of models to try on transient failures."""
    candidates = [
        primary_model,
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    deduped: list[str] = []
    for model in candidates:
        if model and model not in deduped:
            deduped.append(model)
    return deduped


class GeminiLLM:
    def __init__(self, model: str = "gemini-3-flash-preview") -> None:
        self.model = model
        self.client = genai.Client()

    def generate_structured(
        self,
        system: str,
        user: str,
        schema: Type[BaseModel],
        temperature: float = 0.2,
        max_output_tokens: int = 1400,
    ) -> BaseModel:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            # Pydantic's extra='forbid' emits `additionalProperties`, which Gemini
            # currently rejects in response_schema. We still validate strictly after.
            response_schema=_gemini_response_schema(schema),
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        max_attempts_per_model = 3
        tried_models: list[str] = []
        last_error: Exception | None = None

        for model_id in _fallback_model_candidates(self.model):
            tried_models.append(model_id)
            for attempt in range(1, max_attempts_per_model + 1):
                try:
                    response = self.client.models.generate_content(
                        model=model_id,
                        contents=user,
                        config=config,
                    )

                    # Newer SDK versions may expose `.parsed`; validate through our strict model
                    # either way to keep behavior consistent.
                    if hasattr(response, "parsed") and response.parsed is not None:
                        parsed = response.parsed
                        if isinstance(parsed, BaseModel):
                            return schema.model_validate(parsed.model_dump())
                        if isinstance(parsed, dict):
                            return schema.model_validate(parsed)

                    text = getattr(response, "text", None)
                    if not text:
                        raise ValueError(
                            "Model returned no text and no parsed structured output."
                        )

                    data = _parse_jsonish(text)
                    return schema.model_validate(data)
                except Exception as exc:  # noqa: BLE001 - wrapper converts provider errors
                    last_error = exc
                    is_transient = _is_transient_gemini_error(exc)
                    is_retryable_output = _is_retryable_output_error(exc)
                    if not is_transient and not is_retryable_output:
                        raise

                    if attempt < max_attempts_per_model:
                        # Exponential backoff with small jitter for overload spikes.
                        delay = (0.8 * (2 ** (attempt - 1))) + random.uniform(
                            0, 0.35
                        )
                        time.sleep(delay)
                        continue

                    # Final retryable failure for this model:
                    # try next fallback model if available.
                    break

        assert last_error is not None
        if _is_transient_gemini_error(last_error):
            raise RuntimeError(
                f"Gemini models are temporarily unavailable or overloaded after trying: "
                f"{', '.join(tried_models)}. "
                "Please retry in 30-60 seconds."
            ) from last_error
        raise last_error
