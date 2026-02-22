from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent_debate.llm import GeminiLLM
from agent_debate.prompts import CON_SYSTEM, JUDGE_SYSTEM, PRO_SYSTEM
from agent_debate.schemas import DebatePosition, Verdict

app = FastAPI(title="Decision Debate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_executor = ThreadPoolExecutor(max_workers=4)


class DebateRequest(BaseModel):
    decision: str
    context: str = ""
    model: str = "gemini-3-flash-preview"
    language: Literal["en", "ru"] = "en"


def _language_suffix(language: Literal["en", "ru"], *, judge: bool = False) -> str:
    if language == "ru":
        if judge:
            return (
                "\n\nLanguage requirements:\n"
                "- Return all natural-language fields in Russian.\n"
                "- Keep enum values exactly as required by schema (go/no_go/conditional_go, pro/con/tie).\n"
                "- Keep rubric criterion names exactly as listed in the rubric.\n"
            )
        return (
            "\n\nLanguage requirements:\n"
            "- Return claim, reasoning, evidence, and risk in Russian.\n"
            '- If data is missing, prefix evidence with "допущение:" (preferred) or "assumption:" for compatibility.\n'
        )
    if judge:
        return (
            "\n\nLanguage requirements:\n"
            "- Return all natural-language fields in English.\n"
            "- Keep enum values exactly as required by schema (go/no_go/conditional_go, pro/con/tie).\n"
            "- Keep rubric criterion names exactly as listed in the rubric.\n"
        )
    return (
        "\n\nLanguage requirements:\n"
        '- Return claim, reasoning, evidence, and risk in English. Use "assumption:" if data is missing.\n'
    )


def _user_prompt(decision: str, context: str, language: Literal["en", "ru"]) -> str:
    if language == "ru":
        parts = [f"Решение для анализа: {decision}"]
        if context:
            parts.append(f"Дополнительный контекст и ограничения: {context}")
        return "\n".join(parts)

    parts = [f"Decision under consideration: {decision}"]
    if context:
        parts.append(f"Additional context: {context}")
    return "\n".join(parts)


def _judge_prompt(
    decision: str,
    context: str,
    pro: list,
    con: list,
    language: Literal["en", "ru"],
) -> str:
    if language == "ru":
        return (
            f"Решение: {decision}\nКонтекст: {context}\n\n"
            f"Аргументы ЗА:\n{json.dumps(pro, ensure_ascii=False, indent=2)}\n\n"
            f"Аргументы ПРОТИВ:\n{json.dumps(con, ensure_ascii=False, indent=2)}"
        )

    return (
        f"Decision: {decision}\nContext: {context}\n\n"
        f"PRO arguments:\n{json.dumps(pro, ensure_ascii=False, indent=2)}\n\n"
        f"CON arguments:\n{json.dumps(con, ensure_ascii=False, indent=2)}"
    )


def _run_pro(
    decision: str, context: str, model: str, language: Literal["en", "ru"]
) -> list[dict[str, Any]]:
    llm = GeminiLLM(model=model)
    result: DebatePosition = llm.generate_structured(
        system=f"{PRO_SYSTEM}{_language_suffix(language)}",
        user=_user_prompt(decision, context, language),
        schema=DebatePosition,
        max_output_tokens=2200,
    )
    return [a.model_dump() for a in result.arguments]


def _run_con(
    decision: str, context: str, model: str, language: Literal["en", "ru"]
) -> list[dict[str, Any]]:
    llm = GeminiLLM(model=model)
    result: DebatePosition = llm.generate_structured(
        system=f"{CON_SYSTEM}{_language_suffix(language)}",
        user=_user_prompt(decision, context, language),
        schema=DebatePosition,
        max_output_tokens=2200,
    )
    return [a.model_dump() for a in result.arguments]


def _run_judge(
    decision: str,
    context: str,
    model: str,
    pro: list,
    con: list,
    language: Literal["en", "ru"],
) -> dict[str, Any]:
    llm = GeminiLLM(model=model)
    result: Verdict = llm.generate_structured(
        system=f"{JUDGE_SYSTEM}{_language_suffix(language, judge=True)}",
        user=_judge_prompt(decision, context, pro, con, language),
        schema=Verdict,
        max_output_tokens=2800,
    )
    return result.model_dump()


@app.post("/debate/stream")
async def stream_debate(req: DebateRequest) -> EventSourceResponse:
    async def generate():
        loop = asyncio.get_event_loop()
        d, c, m, lang = req.decision, req.context, req.model, req.language

        try:
            yield {"event": "progress", "data": json.dumps({"agent": "pro", "status": "thinking"})}
            pro_args = await loop.run_in_executor(_executor, _run_pro, d, c, m, lang)
            yield {"event": "result", "data": json.dumps({"agent": "pro", "data": pro_args})}

            yield {"event": "progress", "data": json.dumps({"agent": "con", "status": "thinking"})}
            con_args = await loop.run_in_executor(_executor, _run_con, d, c, m, lang)
            yield {"event": "result", "data": json.dumps({"agent": "con", "data": con_args})}

            yield {"event": "progress", "data": json.dumps({"agent": "judge", "status": "thinking"})}
            verdict = await loop.run_in_executor(
                _executor, _run_judge, d, c, m, pro_args, con_args, lang
            )
            yield {"event": "result", "data": json.dumps({"agent": "judge", "data": verdict})}

            yield {"event": "done", "data": "{}"}
        except Exception as exc:
            yield {"event": "error", "data": json.dumps({"message": str(exc)})}

    return EventSourceResponse(generate())


def start() -> None:
    import uvicorn
    uvicorn.run("agent_debate.api:app", host="0.0.0.0", port=8000, reload=True)
