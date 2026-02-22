<script setup lang="ts">
import { computed } from 'vue'
import type { DebateState } from '../types'
import AgentStatusBar from './AgentStatusBar.vue'
import ArgumentCard from './ArgumentCard.vue'
import VerdictPanel from './VerdictPanel.vue'
import { useI18n } from '../i18n'

const props = defineProps<{
  state: DebateState
  decision: string
  canRefine?: boolean
}>()

defineEmits<{
  reset: []
  submitClarifications: [payload: { answers: Array<{ question: string; answer: string }> }]
}>()

const { t } = useI18n()

const completedAgents = computed(() =>
  [props.state.proStatus, props.state.conStatus, props.state.judgeStatus].filter((s) => s === 'done').length,
)

const phaseMeta = computed(() => {
  switch (props.state.phase) {
    case 'debating':
      return {
        label: t('debate.phase.liveLabel'),
        hint: t('debate.phase.liveHint'),
        badge: 'bg-cyan-400/10 text-cyan-200 border-cyan-300/20',
      }
    case 'done':
      return {
        label: t('debate.phase.completeLabel'),
        hint: t('debate.phase.completeHint'),
        badge: 'bg-emerald-400/10 text-emerald-200 border-emerald-300/20',
      }
    case 'error':
      return {
        label: t('debate.phase.errorLabel'),
        hint: t('debate.phase.errorHint'),
        badge: 'bg-rose-400/10 text-rose-200 border-rose-300/20',
      }
    default:
      return {
        label: t('debate.phase.idleLabel'),
        hint: t('debate.phase.idleHint'),
        badge: 'bg-white/5 text-slate-300 border-white/10',
      }
  }
})

const proShowSkeletons = computed(() => props.state.proStatus === 'thinking' && props.state.proArgs.length === 0)
const conShowSkeletons = computed(() => props.state.conStatus === 'thinking' && props.state.conArgs.length === 0)
const judgeThinking = computed(() => props.state.judgeStatus === 'thinking' && !props.state.verdict)
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6 lg:py-8">
    <section class="panel-strong rounded-3xl p-4 sm:p-6 mb-5 overflow-hidden relative">
      <div class="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" aria-hidden="true" />
      <div class="absolute -right-10 -top-10 w-40 h-40 rounded-full blur-3xl bg-[rgba(68,212,200,0.08)]" aria-hidden="true" />

      <div class="relative flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div class="min-w-0">
          <button
            @click="$emit('reset')"
            class="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors mb-3"
          >
            <span class="inline-flex items-center justify-center w-6 h-6 rounded-full panel-soft">←</span>
            {{ t('debate.header.newDecision') }}
          </button>

          <div class="eyebrow mb-2">{{ t('debate.header.eyebrow') }}</div>
          <h2 class="text-xl sm:text-2xl lg:text-3xl font-semibold tracking-tight leading-tight text-balance max-w-4xl">
            {{ decision }}
          </h2>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 shrink-0 min-w-[18rem] lg:min-w-[22rem]">
          <div class="panel-soft rounded-xl p-3">
            <div class="text-[11px] uppercase tracking-[0.14em] text-slate-500 mb-1">{{ t('debate.meta.phase') }}</div>
            <div :class="['inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium', phaseMeta.badge]">
              {{ phaseMeta.label }}
            </div>
            <div class="mt-1 text-xs text-slate-400">{{ phaseMeta.hint }}</div>
          </div>

          <div class="panel-soft rounded-xl p-3">
            <div class="text-[11px] uppercase tracking-[0.14em] text-slate-500 mb-1">{{ t('debate.meta.agentsDone') }}</div>
            <div class="text-lg font-semibold text-white">{{ completedAgents }}/3</div>
            <div class="mt-1 text-xs text-slate-400">{{ t('debate.meta.agentsDoneHint') }}</div>
          </div>

          <div class="panel-soft rounded-xl p-3 col-span-2 sm:col-span-1">
            <div class="text-[11px] uppercase tracking-[0.14em] text-slate-500 mb-1">{{ t('debate.meta.transport') }}</div>
            <div class="text-sm font-medium text-slate-100">{{ t('debate.meta.transportValue') }}</div>
            <div class="mt-1 text-xs text-slate-400">{{ t('debate.meta.transportHint') }}</div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="state.phase === 'error'" class="glass rounded-2xl p-4 sm:p-5 border border-rose-300/10 ring-1 ring-rose-300/15 mb-5">
      <div class="flex items-start gap-3">
        <div class="w-9 h-9 rounded-xl bg-rose-400/10 border border-rose-300/15 flex items-center justify-center text-rose-200 shrink-0">!</div>
        <div>
          <p class="font-semibold text-rose-100 mb-1">{{ t('debate.error.title') }}</p>
          <p class="text-sm text-rose-100/75 leading-relaxed">{{ state.error }}</p>
        </div>
      </div>
    </div>

    <AgentStatusBar
      :pro-status="state.proStatus"
      :con-status="state.conStatus"
      :judge-status="state.judgeStatus"
    />

    <section class="mt-5 grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div class="glass rounded-2xl p-4 sm:p-5">
        <div class="flex items-center justify-between gap-3 mb-4">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-[var(--pro)] status-dot-pulse" />
            <h3 class="text-sm font-semibold uppercase tracking-[0.14em] text-emerald-200">{{ t('debate.columns.pro') }}</h3>
          </div>
          <div class="text-xs text-slate-400 panel-soft rounded-full px-2.5 py-1">{{ t('debate.columns.items', { count: state.proArgs.length }) }}</div>
        </div>

        <TransitionGroup name="card" tag="div" class="space-y-3">
          <ArgumentCard
            v-for="(arg, i) in state.proArgs"
            :key="`pro-${i}`"
            :arg="arg"
            side="pro"
            :style="{ '--i': i }"
          />
        </TransitionGroup>

        <div v-if="proShowSkeletons" class="space-y-3 mt-1">
          <div
            v-for="i in 3"
            :key="`pro-skeleton-${i}`"
            class="rounded-2xl panel-soft p-4 border border-white/5 skeleton-shimmer"
            :style="{ '--i': i }"
          >
            <div class="h-3 rounded bg-white/6 w-24 mb-3" />
            <div class="h-4 rounded bg-white/8 w-11/12 mb-2" />
            <div class="h-4 rounded bg-white/8 w-8/12 mb-4" />
            <div class="h-2 rounded-full bg-white/6 w-full" />
          </div>
        </div>

        <div v-if="!state.proArgs.length && state.proStatus === 'idle'" class="panel-soft rounded-xl p-4 text-sm text-slate-400">
          {{ t('debate.columns.proIdleHint') }}
        </div>
      </div>

      <div class="glass rounded-2xl p-4 sm:p-5">
        <div class="flex items-center justify-between gap-3 mb-4">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-[var(--con)] status-dot-pulse" />
            <h3 class="text-sm font-semibold uppercase tracking-[0.14em] text-rose-200">{{ t('debate.columns.con') }}</h3>
          </div>
          <div class="text-xs text-slate-400 panel-soft rounded-full px-2.5 py-1">{{ t('debate.columns.items', { count: state.conArgs.length }) }}</div>
        </div>

        <TransitionGroup name="card" tag="div" class="space-y-3">
          <ArgumentCard
            v-for="(arg, i) in state.conArgs"
            :key="`con-${i}`"
            :arg="arg"
            side="con"
            :style="{ '--i': i }"
          />
        </TransitionGroup>

        <div v-if="conShowSkeletons" class="space-y-3 mt-1">
          <div
            v-for="i in 3"
            :key="`con-skeleton-${i}`"
            class="rounded-2xl panel-soft p-4 border border-white/5 skeleton-shimmer"
          >
            <div class="h-3 rounded bg-white/6 w-24 mb-3" />
            <div class="h-4 rounded bg-white/8 w-10/12 mb-2" />
            <div class="h-4 rounded bg-white/8 w-7/12 mb-4" />
            <div class="h-2 rounded-full bg-white/6 w-full" />
          </div>
        </div>

        <div v-if="!state.conArgs.length && state.conStatus === 'idle'" class="panel-soft rounded-xl p-4 text-sm text-slate-400">
          {{ t('debate.columns.conIdleHint') }}
        </div>
      </div>
    </section>

    <div
      v-if="judgeThinking"
      class="mt-5 glass rounded-2xl p-4 sm:p-5 border border-amber-200/10 ring-1 ring-amber-200/15"
    >
      <div class="flex items-center gap-3">
        <div class="relative w-9 h-9 rounded-xl panel-soft flex items-center justify-center shrink-0">
          <span class="absolute inset-2 rounded-full bg-amber-300/15 animate-ping" />
          <span class="relative w-2.5 h-2.5 rounded-full bg-amber-300" />
        </div>
        <div>
          <div class="text-sm font-semibold text-amber-100">{{ t('debate.judgeThinking.title') }}</div>
          <div class="text-sm text-amber-100/70">{{ t('debate.judgeThinking.text') }}</div>
        </div>
      </div>
    </div>

    <Transition name="verdict">
      <VerdictPanel
        v-if="state.verdict"
        :verdict="state.verdict"
        :can-refine="props.canRefine ?? true"
        @submit-clarifications="$emit('submitClarifications', $event)"
      />
    </Transition>
  </div>
</template>
