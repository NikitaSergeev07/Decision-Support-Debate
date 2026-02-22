<script setup lang="ts">
import type { AgentStatus } from '../types'
import { useI18n } from '../i18n'

const props = defineProps<{
  proStatus: AgentStatus
  conStatus: AgentStatus
  judgeStatus: AgentStatus
}>()

const { t } = useI18n()

type StatusKey = 'proStatus' | 'conStatus' | 'judgeStatus'

interface AgentConfig {
  key: 'pro' | 'con' | 'judge'
  statusKey: StatusKey
  dot: string
  text: string
  ring: string
  glow: string
}

const agents: AgentConfig[] = [
  {
    key: 'pro',
    statusKey: 'proStatus',
    dot: 'bg-emerald-400',
    text: 'text-emerald-300',
    ring: 'ring-emerald-300/20 border-emerald-300/10',
    glow: 'rgba(48, 203, 151, 0.16)',
  },
  {
    key: 'con',
    statusKey: 'conStatus',
    dot: 'bg-rose-400',
    text: 'text-rose-300',
    ring: 'ring-rose-300/20 border-rose-300/10',
    glow: 'rgba(255, 116, 111, 0.14)',
  },
  {
    key: 'judge',
    statusKey: 'judgeStatus',
    dot: 'bg-amber-300',
    text: 'text-amber-200',
    ring: 'ring-amber-200/20 border-amber-200/10',
    glow: 'rgba(240, 179, 93, 0.16)',
  },
]

function getStatus(key: StatusKey): AgentStatus {
  return props[key]
}

function statusText(status: AgentStatus): string {
  if (status === 'thinking') return t('statusBar.states.thinking')
  if (status === 'done') return t('statusBar.states.done')
  return t('statusBar.states.queued')
}

function statusRank(status: AgentStatus): number {
  if (status === 'done') return 2
  if (status === 'thinking') return 1
  return 0
}

function connectorProgress(index: number): number {
  const current = statusRank(getStatus(agents[index].statusKey))
  const next = statusRank(getStatus(agents[index + 1].statusKey))
  if (current === 2 && next >= 1) return 100
  if (current >= 1) return 45
  return 0
}
</script>

<template>
  <div class="glass rounded-2xl p-4 sm:p-5">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
      <div>
        <div class="eyebrow mb-1">{{ t('statusBar.eyebrow') }}</div>
        <div class="text-sm sm:text-base font-medium text-white">{{ t('statusBar.title') }}</div>
      </div>
      <div class="text-xs text-slate-400 panel-soft rounded-full px-3 py-1.5">
        {{ t('statusBar.streamBadge') }}
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] gap-3 md:gap-2 items-center">
      <template v-for="(agent, index) in agents" :key="agent.key">
        <div
          :class="[
            'relative overflow-hidden rounded-2xl border ring-1 px-4 py-3 transition-all duration-300',
            getStatus(agent.statusKey) === 'idle' ? 'border-white/5 ring-white/5 bg-white/[0.02]' : agent.ring,
          ]"
          :style="getStatus(agent.statusKey) !== 'idle' ? { boxShadow: `inset 0 1px 0 rgba(255,255,255,0.03), 0 0 0 1px rgba(255,255,255,0.01), 0 0 28px ${agent.glow}` } : undefined"
        >
          <div
            class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"
            aria-hidden="true"
          />

          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="relative inline-flex items-center justify-center w-2.5 h-2.5">
                  <span
                    v-if="getStatus(agent.statusKey) === 'thinking'"
                    :class="['absolute inset-0 rounded-full opacity-60 animate-ping', agent.dot]"
                  />
                  <span
                    :class="[
                      'relative block w-2.5 h-2.5 rounded-full transition-colors duration-300',
                      getStatus(agent.statusKey) === 'idle' ? 'bg-white/20' : agent.dot,
                    ]"
                  />
                </span>
                <span :class="['text-xs font-semibold tracking-[0.14em]', getStatus(agent.statusKey) === 'idle' ? 'text-slate-500' : agent.text]">
                  {{ t(`statusBar.agents.${agent.key}.label`) }}
                </span>
              </div>
              <div class="mt-1 text-sm text-slate-100 font-medium">{{ t(`statusBar.agents.${agent.key}.title`) }}</div>
            </div>
            <div class="text-[11px] uppercase tracking-[0.12em] text-slate-400">{{ statusText(getStatus(agent.statusKey)) }}</div>
          </div>
        </div>

        <div v-if="index < agents.length - 1" class="hidden md:flex items-center px-1" aria-hidden="true">
          <div class="w-16 h-1 rounded-full bg-white/5 overflow-hidden border border-white/5">
            <div
              class="h-full rounded-full transition-all duration-700 ease-out"
              :class="connectorProgress(index) >= 100 ? 'bg-gradient-to-r from-[var(--brand-cyan)] to-[var(--brand-blue)]' : connectorProgress(index) > 0 ? 'bg-white/30' : 'bg-transparent'"
              :style="{ width: `${connectorProgress(index)}%` }"
            />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
