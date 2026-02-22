<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Argument } from '../types'
import { useI18n } from '../i18n'

const props = defineProps<{
  arg: Argument
  side: 'pro' | 'con'
}>()

const { t, locale } = useI18n()

const expanded = ref(false)
const barFilled = ref(false)

onMounted(() => {
  setTimeout(() => {
    barFilled.value = true
  }, 80)
})

type DetailKey = 'reasoning' | 'evidence' | 'risk'

const detailRows = computed<Array<{ key: DetailKey; label: string }>>(() => [
  { key: 'reasoning', label: t('argument.detailLabels.reasoning') },
  { key: 'evidence', label: t('argument.detailLabels.evidence') },
  { key: 'risk', label: t('argument.detailLabels.risk') },
])

const isPro = computed(() => props.side === 'pro')
const confidencePct = computed(() => Math.round(props.arg.confidence * 100))
const evidenceIsAssumption = computed(() => {
  const normalized = props.arg.evidence.trim().toLowerCase()
  return normalized.startsWith('assumption:') || normalized.startsWith('допущение:')
})
const displayEvidence = computed(() => {
  if (locale.value !== 'ru') return props.arg.evidence
  return props.arg.evidence.replace(/^assumption:/i, 'допущение:')
})
const reasoningPreview = computed(() => {
  const text = props.arg.reasoning.trim()
  if (text.length <= 140) return text
  return `${text.slice(0, 137)}...`
})

const sideLabel = computed(() => (isPro.value ? t('app.chips.pro') : t('app.chips.con')))

const tone = computed(() => {
  if (isPro.value) {
    return {
      badge: 'text-emerald-200 bg-emerald-400/10 border-emerald-300/20',
      accentText: 'text-emerald-300/90',
      border: 'border-emerald-300/10 ring-emerald-300/15 hover:ring-emerald-300/20',
      bar: 'from-emerald-400 to-cyan-300',
      softBg: 'bg-emerald-400/8',
      dot: 'bg-emerald-400',
      glow: 'rgba(48, 203, 151, 0.18)',
    }
  }
  return {
    badge: 'text-rose-200 bg-rose-400/10 border-rose-300/20',
    accentText: 'text-rose-300/90',
    border: 'border-rose-300/10 ring-rose-300/15 hover:ring-rose-300/20',
    bar: 'from-rose-400 to-orange-300',
    softBg: 'bg-rose-400/8',
    dot: 'bg-rose-400',
    glow: 'rgba(255, 116, 111, 0.16)',
  }
})
</script>

<template>
  <article
    :class="[
      'relative overflow-hidden rounded-2xl border ring-1 glass p-4 sm:p-5 transition-all duration-300 hover:-translate-y-0.5',
      tone.border,
    ]"
    :style="{ boxShadow: `0 14px 30px rgba(0,0,0,0.28), 0 0 26px ${tone.glow}` }"
  >
    <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent" aria-hidden="true" />
    <div :class="['absolute right-0 top-0 w-28 h-28 rounded-full blur-2xl', tone.softBg]" aria-hidden="true" />

    <div class="relative">
      <div class="flex items-start justify-between gap-3 mb-3">
        <div class="min-w-0">
          <div class="flex items-center gap-2 mb-2">
            <span :class="['inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[11px] font-semibold tracking-[0.14em]', tone.badge]">
              <span :class="['w-1.5 h-1.5 rounded-full', tone.dot]" />
              {{ sideLabel }}
            </span>
            <span class="text-[11px] text-slate-500 uppercase tracking-[0.14em]">{{ t('argument.badge') }}</span>
          </div>
          <h4 class="text-sm sm:text-[15px] font-semibold text-white leading-snug text-balance">{{ arg.claim }}</h4>
        </div>
        <div class="shrink-0 text-right">
          <div class="text-[11px] text-slate-500 uppercase tracking-[0.14em]">{{ t('argument.confidence') }}</div>
          <div class="text-sm font-semibold text-slate-100 font-mono tabular-nums">{{ confidencePct }}%</div>
        </div>
      </div>

      <p class="text-sm text-slate-300 leading-relaxed mb-3">{{ reasoningPreview }}</p>

      <div class="space-y-2.5 mb-3">
        <div class="flex items-center justify-between gap-3 text-xs">
          <span :class="['font-medium', tone.accentText]">{{ t('argument.confidenceSignal') }}</span>
          <span class="text-slate-400 font-mono tabular-nums">{{ arg.confidence.toFixed(2) }}</span>
        </div>
        <div class="h-2 rounded-full bg-white/5 border border-white/5 overflow-hidden">
          <div
            :class="['h-full rounded-full bg-gradient-to-r transition-all duration-1000 ease-out', tone.bar]"
            :style="{ width: barFilled ? `${arg.confidence * 100}%` : '0%' }"
          />
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-2 mb-3">
        <span class="inline-flex items-center gap-2 text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300">
          <span class="w-1.5 h-1.5 rounded-full" :class="evidenceIsAssumption ? 'bg-amber-300' : 'bg-cyan-300'" />
          {{ evidenceIsAssumption ? t('argument.assumptionBacked') : t('argument.evidenceBacked') }}
        </span>
        <span class="inline-flex items-center text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-slate-400">
          {{ t('argument.riskIncluded') }}
        </span>
      </div>

      <button
        type="button"
        class="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white transition-colors"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        <span
          class="inline-flex items-center justify-center w-5 h-5 rounded-full border border-white/10 bg-white/5 text-xs transition-transform duration-200"
          :class="{ 'rotate-45': expanded }"
        >+</span>
        {{ expanded ? t('argument.hideDetails') : t('argument.showDetails') }}
      </button>

      <Transition name="expand">
        <div v-if="expanded" class="mt-4 panel-soft rounded-xl p-3.5 space-y-3">
          <div v-for="row in detailRows" :key="row.key">
            <div :class="['text-[11px] uppercase tracking-[0.14em] font-semibold mb-1', tone.accentText]">{{ row.label }}</div>
            <p class="text-sm text-slate-200/95 leading-relaxed break-words">
              {{ row.key === 'evidence' ? displayEvidence : arg[row.key] }}
            </p>
          </div>
        </div>
      </Transition>
    </div>
  </article>
</template>
