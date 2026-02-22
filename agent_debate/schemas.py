from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Argument(StrictModel):
    claim: str
    reasoning: str
    evidence: str  # fact/observation, or starts with "assumption:" if no data
    risk: str
    confidence: float = Field(ge=0.0, le=1.0)


class DebatePosition(StrictModel):
    arguments: list[Argument] = Field(min_length=3, max_length=8)


class ScorecardCriterion(StrictModel):
    criterion: str
    weight: float = Field(gt=0.0, le=1.0)
    pro_score: float = Field(ge=0.0, le=10.0)
    con_score: float = Field(ge=0.0, le=10.0)
    rationale: str


class Verdict(StrictModel):
    decision: Literal["go", "no_go", "conditional_go"]
    winner: Literal["pro", "con", "tie"]
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    scorecard: list[ScorecardCriterion] = Field(min_length=7, max_length=7)
    key_risks: list[str] = Field(min_length=2, max_length=8)
    assumptions_to_verify: list[str] = Field(min_length=1, max_length=8)
    next_48h_actions: list[str] = Field(min_length=2, max_length=8)
    needs_more_info: bool
    clarifying_questions: list[str] = Field(default_factory=list, max_length=5)

    @model_validator(mode="after")
    def validate_clarifying_questions(self) -> "Verdict":
        if self.needs_more_info and not self.clarifying_questions:
            raise ValueError(
                "clarifying_questions must be provided when needs_more_info=true"
            )
        if not self.needs_more_info and self.clarifying_questions:
            raise ValueError(
                "clarifying_questions must be empty when needs_more_info=false"
            )
        return self
