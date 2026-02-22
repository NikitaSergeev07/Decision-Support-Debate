from __future__ import annotations

import json
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agent_debate.llm import GeminiLLM
from agent_debate.prompts import CON_SYSTEM, JUDGE_SYSTEM, PRO_SYSTEM
from agent_debate.schemas import DebatePosition, Verdict


class DebateState(TypedDict):
    decision: str
    context: str
    model: str
    pro_arguments: list[dict[str, Any]]
    con_arguments: list[dict[str, Any]]
    verdict: dict[str, Any]


def _user_prompt(decision: str, context: str) -> str:
    parts = [f"Decision under consideration: {decision}"]
    if context:
        parts.append(f"Additional context: {context}")
    return "\n".join(parts)


def _judge_prompt(decision: str, context: str, pro: list[dict], con: list[dict]) -> str:
    return (
        f"Decision: {decision}\n"
        f"Context: {context}\n\n"
        f"PRO arguments:\n{json.dumps(pro, ensure_ascii=False, indent=2)}\n\n"
        f"CON arguments:\n{json.dumps(con, ensure_ascii=False, indent=2)}"
    )


def pro_node(state: DebateState) -> dict[str, Any]:
    llm = GeminiLLM(model=state["model"])
    result: DebatePosition = llm.generate_structured(
        system=PRO_SYSTEM,
        user=_user_prompt(state["decision"], state["context"]),
        schema=DebatePosition,
        max_output_tokens=2200,
    )
    return {"pro_arguments": [a.model_dump() for a in result.arguments]}


def con_node(state: DebateState) -> dict[str, Any]:
    llm = GeminiLLM(model=state["model"])
    result: DebatePosition = llm.generate_structured(
        system=CON_SYSTEM,
        user=_user_prompt(state["decision"], state["context"]),
        schema=DebatePosition,
        max_output_tokens=2200,
    )
    return {"con_arguments": [a.model_dump() for a in result.arguments]}


def judge_node(state: DebateState) -> dict[str, Any]:
    llm = GeminiLLM(model=state["model"])
    result: Verdict = llm.generate_structured(
        system=JUDGE_SYSTEM,
        user=_judge_prompt(
            state["decision"],
            state["context"],
            state["pro_arguments"],
            state["con_arguments"],
        ),
        schema=Verdict,
        max_output_tokens=2800,
    )
    return {"verdict": result.model_dump()}


def build_graph() -> StateGraph:
    graph = StateGraph(DebateState)
    graph.add_node("pro", pro_node)
    graph.add_node("con", con_node)
    graph.add_node("judge", judge_node)

    graph.add_edge(START, "pro")
    graph.add_edge("pro", "con")
    graph.add_edge("con", "judge")
    graph.add_edge("judge", END)

    return graph.compile()
