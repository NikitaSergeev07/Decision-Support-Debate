<script setup lang="ts">
import { ref } from 'vue'
import DebateForm from './components/DebateForm.vue'
import DebateView from './components/DebateView.vue'
import { useDebate } from './composables/useDebate'
import { useI18n } from './i18n'

const { state, startDebate, reset } = useDebate()
const { locale, t } = useI18n()
const currentDecision = ref('')
const currentContext = ref('')
const currentModel = ref('gemini-3-flash-preview')

async function handleSubmit(params: { decision: string; context: string; model: string }) {
  currentDecision.value = params.decision
  currentContext.value = params.context
  currentModel.value = params.model
  await startDebate(params.decision, params.context, params.model, locale.value)
}

function buildFollowUpContext(
  baseContext: string,
  answers: Array<{ question: string; answer: string }>,
  lang: 'en' | 'ru',
) {
  const trimmedBase = baseContext.trim()
  const heading = lang === 'ru'
    ? 'Ответы пользователя на уточняющие вопросы:'
    : 'User answers to clarifying questions:'
  const answerLabel = lang === 'ru' ? 'Ответ' : 'Answer'

  const answerBlocks = answers.map(
    ({ question, answer }, index) => `${index + 1}. ${question}\n${answerLabel}: ${answer}`,
  )

  return [trimmedBase, heading, ...answerBlocks].filter(Boolean).join('\n\n')
}

async function handleClarificationsSubmit(payload: { answers: Array<{ question: string; answer: string }> }) {
  if (!currentDecision.value || payload.answers.length === 0) return

  currentContext.value = buildFollowUpContext(
    currentContext.value,
    payload.answers,
    locale.value,
  )

  await startDebate(
    currentDecision.value,
    currentContext.value,
    currentModel.value,
    locale.value,
  )
}

function handleReset() {
  reset()
  currentDecision.value = ''
  currentContext.value = ''
  currentModel.value = 'gemini-3-flash-preview'
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden">
    <div class="fixed inset-0 pointer-events-none" aria-hidden="true">
      <div class="ambient-orb a" />
      <div class="ambient-orb b" />
      <div class="ambient-orb c" />

      <div class="radar-ring w-[36rem] h-[36rem] -top-40 left-[8%] opacity-40" />
      <div class="radar-ring w-[22rem] h-[22rem] top-[18%] right-[10%] opacity-30" />
      <div class="radar-ring w-[48rem] h-[48rem] -bottom-64 right-[20%] opacity-20" />

      <div class="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-white/[0.03] to-transparent" />
      <div class="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black/25 to-transparent" />
    </div>

    <div class="relative z-10 min-h-screen">
      <header class="max-w-7xl mx-auto px-4 sm:px-6 pt-4 sm:pt-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="inline-flex items-center gap-3 rounded-full px-3 py-2 panel-soft">
            <span class="w-2 h-2 rounded-full bg-[var(--brand-cyan)] status-dot-pulse" />
            <span class="text-xs sm:text-sm font-medium text-slate-200">{{ t('app.title') }}</span>
          </div>

          <div class="flex items-center gap-2 sm:gap-3">
            <div class="hidden sm:flex items-center gap-2 text-xs text-slate-400">
              <span class="kbd-chip">{{ t('app.chips.pro') }}</span>
              <span class="kbd-chip">{{ t('app.chips.con') }}</span>
              <span class="kbd-chip">{{ t('app.chips.judge') }}</span>
            </div>

            <div class="inline-flex items-center gap-2 px-3 py-2 rounded-full panel-soft text-xs text-slate-300">
              <span class="w-2 h-2 rounded-full bg-[var(--brand-cyan)]" />
              <span class="font-medium">RU</span>
            </div>
          </div>
        </div>
      </header>

      <Transition name="page" mode="out-in">
        <DebateForm
          v-if="state.phase === 'idle'"
          key="form"
          @submit="handleSubmit"
        />
        <DebateView
          v-else
          key="debate"
          :state="state"
          :decision="currentDecision"
          :can-refine="state.phase !== 'debating'"
          @reset="handleReset"
          @submit-clarifications="handleClarificationsSubmit"
        />
      </Transition>
    </div>
  </div>
</template>
