export interface Argument {
  claim: string
  reasoning: string
  evidence: string
  risk: string
  confidence: number
}

export interface ScorecardCriterion {
  criterion: string
  weight: number
  pro_score: number
  con_score: number
  rationale: string
}

export interface Verdict {
  decision: 'go' | 'no_go' | 'conditional_go'
  winner: 'pro' | 'con' | 'tie'
  confidence: number
  summary: string
  scorecard: ScorecardCriterion[]
  key_risks: string[]
  assumptions_to_verify: string[]
  next_48h_actions: string[]
  needs_more_info: boolean
  clarifying_questions: string[]
}

export type AgentStatus = 'idle' | 'thinking' | 'done'
export type Phase = 'idle' | 'debating' | 'done' | 'error'

export interface DebateState {
  phase: Phase
  proStatus: AgentStatus
  conStatus: AgentStatus
  judgeStatus: AgentStatus
  proArgs: Argument[]
  conArgs: Argument[]
  verdict: Verdict | null
  error: string | null
}
