import { reactive } from 'vue'
import type { DebateState } from '../types'

function processSSEChunk(
  rawChunk: string,
  onEvent: (type: string, data: unknown) => void,
) {
  const lines = rawChunk
    .split('\n')
    .map((line) => line.trimEnd())
    .filter((line) => line.length > 0)

  let eventType = 'message'
  const dataLines: string[] = []

  for (const line of lines) {
    if (line.startsWith('event:')) {
      eventType = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  if (dataLines.length === 0) return

  try {
    onEvent(eventType, JSON.parse(dataLines.join('\n')))
  } catch {
    // ignore malformed events and continue streaming
  }
}

async function readSSE(
  response: Response,
  onEvent: (type: string, data: unknown) => void,
) {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      buffer += decoder.decode()
      break
    }
    buffer += decoder.decode(value, { stream: true })

    // Normalize CRLF and split on empty lines between SSE events.
    buffer = buffer.replace(/\r\n/g, '\n')
    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      processSSEChunk(part, onEvent)
    }
  }

  // Flush a trailing event if the stream closed without a final blank line.
  const tail = buffer.replace(/\r\n/g, '\n').trim()
  if (tail) processSSEChunk(tail, onEvent)
}

export function useDebate() {
  const state = reactive<DebateState>({
    phase: 'idle',
    proStatus: 'idle',
    conStatus: 'idle',
    judgeStatus: 'idle',
    proArgs: [],
    conArgs: [],
    verdict: null,
    error: null,
  })

  function reset() {
    state.phase = 'idle'
    state.proStatus = 'idle'
    state.conStatus = 'idle'
    state.judgeStatus = 'idle'
    state.proArgs = []
    state.conArgs = []
    state.verdict = null
    state.error = null
  }

  async function startDebate(
    decision: string,
    context: string,
    model: string,
    language: 'en' | 'ru' = 'en',
  ) {
    reset()
    state.phase = 'debating'

    try {
      const response = await fetch('/debate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, context, model, language }),
      })

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`)
      }

      await readSSE(response, (type, data: any) => {
        if (type === 'progress') {
          if (data.agent === 'pro') state.proStatus = 'thinking'
          else if (data.agent === 'con') state.conStatus = 'thinking'
          else if (data.agent === 'judge') state.judgeStatus = 'thinking'
        } else if (type === 'result') {
          if (data.agent === 'pro') { state.proArgs = data.data; state.proStatus = 'done' }
          else if (data.agent === 'con') { state.conArgs = data.data; state.conStatus = 'done' }
          else if (data.agent === 'judge') { state.verdict = data.data; state.judgeStatus = 'done' }
        } else if (type === 'done') {
          state.phase = 'done'
        } else if (type === 'error') {
          state.error = data.message
          state.phase = 'error'
        }
      })

      if (state.error === null) state.phase = 'done'
    } catch (err) {
      state.error = err instanceof Error ? err.message : String(err)
      state.phase = 'error'
    }
  }

  return { state, startDebate, reset }
}
