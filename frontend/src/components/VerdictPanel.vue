<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Verdict } from '../types'
import { useI18n } from '../i18n'

const props = defineProps<{
  verdict: Verdict
  canRefine?: boolean
}>()

const emit = defineEmits<{
  submitClarifications: [payload: { answers: Array<{ question: string; answer: string }> }]
}>()

const { t, locale } = useI18n()

const barsAnimated = ref(false)

onMounted(() => {
  setTimeout(() => {
    barsAnimated.value = true
  }, 120)
})

const DECISION_CONFIG = {
  go: {
    icon: 'GO',
    pill: 'bg-emerald-400/10 text-emerald-200 border-emerald-300/20',
    glow: 'rgba(48, 203, 151, 0.18)',
    accent: '#30cb97',
  },
  no_go: {
    icon: 'NO',
    pill: 'bg-rose-400/10 text-rose-200 border-rose-300/20',
    glow: 'rgba(255, 116, 111, 0.16)',
    accent: '#ff746f',
  },
  conditional_go: {
    icon: 'CG',
    pill: 'bg-amber-300/10 text-amber-100 border-amber-200/20',
    glow: 'rgba(240, 179, 93, 0.18)',
    accent: '#f0b35d',
  },
} as const

const WINNER_CONFIG = {
  pro: { tone: 'text-emerald-200', chip: 'bg-emerald-400/10 border-emerald-300/20' },
  con: { tone: 'text-rose-200', chip: 'bg-rose-400/10 border-rose-300/20' },
  tie: { tone: 'text-amber-100', chip: 'bg-amber-300/10 border-amber-200/20' },
} as const

const decisionMeta = computed(() => {
  const base = DECISION_CONFIG[props.verdict.decision] ?? DECISION_CONFIG.conditional_go
  const ruIcons: Record<Verdict['decision'], string> = {
    go: 'ДА',
    no_go: 'НЕТ',
    conditional_go: 'УСЛ',
  }
  return {
    ...base,
    icon: locale.value === 'ru' ? ruIcons[props.verdict.decision] : base.icon,
    label: t(`verdict.decision.${props.verdict.decision}`),
  }
})

const winnerMeta = computed(() => {
  const base = WINNER_CONFIG[props.verdict.winner] ?? WINNER_CONFIG.tie
  return {
    ...base,
    label: t(`verdict.winner.${props.verdict.winner}`),
  }
})

const confidencePct = computed(() => Math.round(props.verdict.confidence * 100))
const confidenceRingStyle = computed(() => {
  const degrees = Math.max(0, Math.min(360, props.verdict.confidence * 360))
  const accent = decisionMeta.value.accent
  return {
    background: `conic-gradient(${accent} 0deg ${degrees}deg, rgba(255,255,255,0.08) ${degrees}deg 360deg)`,
  }
})

const weightedTotals = computed(() => {
  let pro = 0
  let con = 0
  for (const row of props.verdict.scorecard) {
    pro += row.pro_score * row.weight
    con += row.con_score * row.weight
  }
  return {
    pro: Number(pro.toFixed(2)),
    con: Number(con.toFixed(2)),
    delta: Number((pro - con).toFixed(2)),
  }
})

const criterionLabelMap: Record<string, { en: string; ru: string }> = {
  Feasibility: { en: 'Feasibility', ru: 'Реализуемость' },
  'Cost/Time': { en: 'Cost/Time', ru: 'Стоимость/Сроки' },
  'Risk/Uncertainty': { en: 'Risk/Uncertainty', ru: 'Риск/Неопределенность' },
  Reversibility: { en: 'Reversibility', ru: 'Обратимость' },
  'Expected value': { en: 'Expected value', ru: 'Ожидаемая ценность' },
  'Evidence quality': { en: 'Evidence quality', ru: 'Качество доказательной базы' },
  'Alignment with constraints': { en: 'Alignment with constraints', ru: 'Соответствие ограничениям' },
}

function localizedCriterionLabel(raw: string): string {
  const mapped = criterionLabelMap[raw]
  if (!mapped) return raw
  return locale.value === 'ru' ? mapped.ru : mapped.en
}

function scoreWinnerLabel(proScore: number, conScore: number): string {
  if (proScore === conScore) return t('verdict.scorecard.tie')
  return proScore > conScore ? t('verdict.scorecard.pro') : t('verdict.scorecard.con')
}

const clarifyingAnswers = ref<Record<string, string>>({})

watch(
  () => props.verdict.clarifying_questions,
  (questions) => {
    const next: Record<string, string> = {}
    for (const question of questions) {
      next[question] = clarifyingAnswers.value[question] ?? ''
    }
    clarifyingAnswers.value = next
  },
  { immediate: true },
)

const quickAnswerOptions = computed(() =>
  locale.value === 'ru'
    ? [
        'Да',
        'Нет',
        'Частично',
        'Неизвестно / пока нет данных',
        'Не применимо',
      ]
    : ['Yes', 'No', 'Partially', 'Unknown / no data yet', 'Not applicable'],
)

const answeredClarifyingCount = computed(() =>
  props.verdict.clarifying_questions.filter((q) => (clarifyingAnswers.value[q] ?? '').trim().length > 0)
    .length,
)

const canSubmitClarifications = computed(
  () => (props.canRefine ?? true) && answeredClarifyingCount.value > 0,
)

function setClarifyingAnswer(question: string, answer: string) {
  clarifyingAnswers.value = {
    ...clarifyingAnswers.value,
    [question]: answer,
  }
}

function onClarifyingInput(question: string, event: Event) {
  const target = event.target as HTMLTextAreaElement | null
  setClarifyingAnswer(question, target?.value ?? '')
}

function submitClarifications() {
  if (!canSubmitClarifications.value) return

  const answers = props.verdict.clarifying_questions
    .map((question) => ({
      question,
      answer: (clarifyingAnswers.value[question] ?? '').trim(),
    }))
    .filter((item) => item.answer.length > 0)

  if (answers.length === 0) return
  emit('submitClarifications', { answers })
}
</script>

<template>
  <section class="mt-6 sm:mt-7 space-y-5">
    <div class="grid grid-cols-1 xl:grid-cols-[1.1fr_0.9fr] gap-5">
      <div class="panel-strong rounded-3xl p-5 sm:p-6 relative overflow-hidden"
           :style="{ boxShadow: `0 18px 48px rgba(0,0,0,0.3), 0 0 36px ${decisionMeta.glow}` }">
        <div class="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" aria-hidden="true" />
        <div class="absolute -right-10 -top-10 w-44 h-44 rounded-full blur-3xl" :style="{ background: decisionMeta.glow }" aria-hidden="true" />

        <div class="relative">
          <div class="eyebrow mb-2">{{ t('verdict.judgeEyebrow') }}</div>
          <div class="flex flex-wrap items-center gap-3 mb-4">
            <div :class="['inline-flex items-center gap-3 rounded-2xl border px-4 py-2.5 font-semibold tracking-[0.02em]', decisionMeta.pill]">
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-white/5 border border-white/10 text-xs font-mono">
                {{ decisionMeta.icon }}
              </span>
              <span>{{ decisionMeta.label }}</span>
            </div>

            <div :class="['inline-flex items-center rounded-full border px-3 py-1.5 text-sm', winnerMeta.chip, winnerMeta.tone]">
              {{ winnerMeta.label }}
            </div>

            <div class="text-sm text-slate-300">
              <span class="font-mono tabular-nums text-white">{{ confidencePct }}%</span>
              {{ t('verdict.confidenceSuffix') }}
            </div>
          </div>

          <p class="text-slate-100/95 text-base leading-relaxed text-balance">
            {{ verdict.summary }}
          </p>
        </div>
      </div>

      <div class="glass rounded-3xl p-5 sm:p-6">
        <div class="eyebrow mb-3">{{ t('verdict.decisionSignal') }}</div>
        <div class="flex items-center gap-4 mb-5">
          <div class="relative w-24 h-24 rounded-full p-[5px]" :style="confidenceRingStyle">
            <div class="w-full h-full rounded-full bg-[rgba(8,17,24,0.92)] border border-white/10 flex flex-col items-center justify-center">
              <div class="text-xs text-slate-400">{{ t('verdict.confidence') }}</div>
              <div class="text-xl font-semibold text-white font-mono tabular-nums">{{ confidencePct }}%</div>
            </div>
          </div>

          <div class="space-y-2 flex-1 min-w-0">
            <div class="panel-soft rounded-xl p-3">
              <div class="flex items-center justify-between gap-3 text-sm">
                <span class="text-slate-300">{{ t('verdict.metrics.proTotal') }}</span>
                <span class="font-mono tabular-nums text-emerald-200">{{ weightedTotals.pro.toFixed(2) }}</span>
              </div>
            </div>
            <div class="panel-soft rounded-xl p-3">
              <div class="flex items-center justify-between gap-3 text-sm">
                <span class="text-slate-300">{{ t('verdict.metrics.conTotal') }}</span>
                <span class="font-mono tabular-nums text-rose-200">{{ weightedTotals.con.toFixed(2) }}</span>
              </div>
            </div>
            <div class="panel-soft rounded-xl p-3">
              <div class="flex items-center justify-between gap-3 text-sm">
                <span class="text-slate-300">{{ t('verdict.metrics.netSwing') }}</span>
                <span class="font-mono tabular-nums" :class="weightedTotals.delta >= 0 ? 'text-emerald-200' : 'text-rose-200'">
                  {{ weightedTotals.delta >= 0 ? '+' : '' }}{{ weightedTotals.delta.toFixed(2) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-soft rounded-xl p-3.5 text-sm text-slate-300 leading-relaxed">
          <div class="text-xs uppercase tracking-[0.14em] text-slate-500 mb-1">{{ t('verdict.interpretationTitle') }}</div>
          {{ t('verdict.interpretationText') }}
        </div>
      </div>
    </div>

    <div
      v-if="verdict.needs_more_info"
      class="glass rounded-2xl p-4 sm:p-5 border border-amber-200/10 ring-1 ring-amber-200/15"
    >
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div class="text-sm font-semibold text-amber-100 mb-1">{{ t('verdict.missingInfo.title') }}</div>
          <p class="text-sm text-amber-100/75 leading-relaxed">
            {{ t('verdict.missingInfo.text') }}
          </p>
        </div>
        <div class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 bg-amber-300/10 border border-amber-200/20 text-xs text-amber-100">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-200" />
          {{ t('verdict.missingInfo.flag') }}
        </div>
      </div>
    </div>

    <div class="glass rounded-3xl p-5 sm:p-6">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <div class="eyebrow mb-1">{{ t('verdict.scorecard.eyebrow') }}</div>
          <h3 class="text-lg font-semibold tracking-tight">{{ t('verdict.scorecard.title') }}</h3>
        </div>
        <div class="text-xs text-slate-400 panel-soft rounded-full px-3 py-1.5">
          {{ t('verdict.scorecard.subtitle') }}
        </div>
      </div>

      <div class="space-y-4">
        <div
          v-for="(row, idx) in verdict.scorecard"
          :key="row.criterion"
          class="panel-soft rounded-2xl p-4 border border-white/5"
        >
          <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div>
              <div class="text-sm font-semibold text-slate-100">{{ localizedCriterionLabel(row.criterion) }}</div>
              <div class="text-xs text-slate-500">{{ t('verdict.scorecard.weight', { percent: Math.round(row.weight * 100) }) }}</div>
            </div>
            <div class="text-xs font-mono tabular-nums px-2.5 py-1 rounded-full border"
                 :class="row.pro_score === row.con_score ? 'border-white/10 text-slate-300 bg-white/5' : row.pro_score > row.con_score ? 'border-emerald-300/20 text-emerald-200 bg-emerald-400/10' : 'border-rose-300/20 text-rose-200 bg-rose-400/10'">
              {{ scoreWinnerLabel(row.pro_score, row.con_score) }}
              {{ row.pro_score === row.con_score ? '' : ` ${row.pro_score > row.con_score ? '+' : ''}${(row.pro_score - row.con_score).toFixed(1)}` }}
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-2">
            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-emerald-200">{{ t('verdict.scorecard.pro') }}</span>
                <span class="text-slate-400 font-mono tabular-nums">{{ row.pro_score.toFixed(1) }}</span>
              </div>
              <div class="h-2.5 rounded-full bg-white/5 border border-white/5 overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-emerald-400 to-cyan-300 transition-all duration-1000 ease-out"
                  :style="{ width: barsAnimated ? `${row.pro_score * 10}%` : '0%', transitionDelay: `${idx * 55}ms` }"
                />
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="text-rose-200">{{ t('verdict.scorecard.con') }}</span>
                <span class="text-slate-400 font-mono tabular-nums">{{ row.con_score.toFixed(1) }}</span>
              </div>
              <div class="h-2.5 rounded-full bg-white/5 border border-white/5 overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-rose-400 to-orange-300 transition-all duration-1000 ease-out"
                  :style="{ width: barsAnimated ? `${row.con_score * 10}%` : '0%', transitionDelay: `${idx * 55 + 40}ms` }"
                />
              </div>
            </div>
          </div>

          <p class="text-sm text-slate-300/85 leading-relaxed">{{ row.rationale }}</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="glass rounded-2xl p-4 sm:p-5 border border-amber-200/10">
        <div class="flex items-center gap-2 mb-3">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-300" />
          <h3 class="text-sm font-semibold uppercase tracking-[0.14em] text-amber-100">{{ t('verdict.sections.keyRisks') }}</h3>
        </div>
        <ul class="space-y-2">
          <li v-for="risk in verdict.key_risks" :key="risk" class="flex gap-2 text-sm text-slate-200">
            <span class="text-amber-200/70 shrink-0 mt-[2px]">•</span>
            <span class="leading-relaxed">{{ risk }}</span>
          </li>
        </ul>
      </div>

      <div class="glass rounded-2xl p-4 sm:p-5 border border-cyan-200/10">
        <div class="flex items-center gap-2 mb-3">
          <span class="w-2.5 h-2.5 rounded-full bg-cyan-300" />
          <h3 class="text-sm font-semibold uppercase tracking-[0.14em] text-cyan-100">{{ t('verdict.sections.assumptions') }}</h3>
        </div>
        <ul class="space-y-2">
          <li v-for="item in verdict.assumptions_to_verify" :key="item" class="flex gap-2 text-sm text-slate-200">
            <span class="text-cyan-200/70 shrink-0 mt-[2px]">•</span>
            <span class="leading-relaxed">{{ item }}</span>
          </li>
        </ul>
      </div>

      <div class="glass rounded-2xl p-4 sm:p-5 border border-blue-200/10">
        <div class="flex items-center gap-2 mb-3">
          <span class="w-2.5 h-2.5 rounded-full bg-blue-300" />
          <h3 class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-100">{{ t('verdict.sections.nextActions') }}</h3>
        </div>
        <ol class="space-y-2">
          <li v-for="(item, index) in verdict.next_48h_actions" :key="item" class="flex gap-2.5 text-sm text-slate-200">
            <span class="text-blue-200/80 shrink-0 font-mono text-xs mt-[3px]">{{ index + 1 }}.</span>
            <span class="leading-relaxed">{{ item }}</span>
          </li>
        </ol>
      </div>
    </div>

    <div v-if="verdict.needs_more_info && verdict.clarifying_questions.length" class="glass rounded-2xl p-4 sm:p-5">
      <div class="flex items-center justify-between gap-3 mb-3">
        <div>
          <div class="eyebrow mb-1">{{ t('verdict.sections.followUpEyebrow') }}</div>
          <h3 class="text-base font-semibold">{{ t('verdict.sections.clarifyingQuestions') }}</h3>
        </div>
        <div class="text-xs text-slate-400 panel-soft rounded-full px-3 py-1.5">
          {{ t('verdict.sections.questionsCount', { count: verdict.clarifying_questions.length }) }}
        </div>
      </div>

      <p class="text-sm text-slate-300/85 leading-relaxed mb-4">
        {{ t('verdict.sections.clarifyingHelp') }}
      </p>

      <form class="space-y-3.5" @submit.prevent="submitClarifications">
        <div
          v-for="(q, index) in verdict.clarifying_questions"
          :key="q"
          class="panel-soft rounded-xl p-3.5 border border-white/5"
        >
          <div class="flex items-start gap-3 mb-3">
            <span class="w-6 h-6 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-xs text-slate-400 shrink-0">
              {{ index + 1 }}
            </span>
            <div class="min-w-0 flex-1">
              <div class="text-sm text-slate-100 leading-relaxed">{{ q }}</div>
              <div class="mt-2 flex flex-wrap gap-1.5">
                <button
                  v-for="option in quickAnswerOptions"
                  :key="`${q}-${option}`"
                  type="button"
                  class="text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300 hover:text-white hover:border-white/20 transition-colors"
                  @click="setClarifyingAnswer(q, option)"
                >
                  {{ option }}
                </button>
              </div>
            </div>
          </div>

          <label class="block text-xs uppercase tracking-[0.14em] text-slate-500 mb-2">
            {{ t('verdict.sections.answerLabel') }}
          </label>
          <textarea
            :value="clarifyingAnswers[q] ?? ''"
            rows="2"
            class="w-full bg-transparent rounded-xl px-3 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 border border-white/10 focus:border-white/20 outline-none resize-y"
            :placeholder="t('verdict.sections.answerPlaceholder')"
            @input="onClarifyingInput(q, $event)"
          />
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-1">
          <div class="text-xs text-slate-400">
            {{ t('verdict.sections.answersProgress', {
              answered: answeredClarifyingCount,
              total: verdict.clarifying_questions.length,
            }) }}
          </div>

          <button
            type="submit"
            class="inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium text-white bg-white/8 border border-white/12 hover:bg-white/12 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="!canSubmitClarifications"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-[var(--brand-cyan)]" />
            {{ (props.canRefine ?? true) ? t('verdict.sections.submitClarifications') : t('verdict.sections.recomputing') }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>
