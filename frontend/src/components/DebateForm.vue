<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from '../i18n'

const emit = defineEmits<{
  submit: [{ decision: string; context: string; model: string }]
}>()

const { t } = useI18n()

const decision = ref('')
const context = ref('')
const model = ref('gemini-3-flash-preview')
const showContext = ref(false)

const modelOptions = computed(() => [
  {
    value: 'gemini-3-flash-preview',
    label: 'gemini-3-flash-preview',
    hint: t('form.modelHints.defaultFast'),
  },
  {
    value: 'gemini-2.5-flash',
    label: 'gemini-2.5-flash',
    hint: t('form.modelHints.balanced'),
  },
  {
    value: 'gemini-2.5-flash-lite',
    label: 'gemini-2.5-flash-lite',
    hint: t('form.modelHints.cheaperFast'),
  },
])

const canSubmit = computed(() => decision.value.trim().length > 0)

function handleSubmit() {
  if (!canSubmit.value) return
  emit('submit', {
    decision: decision.value.trim(),
    context: context.value.trim(),
    model: model.value,
  })
}
</script>

<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center px-4 sm:px-6 py-8 sm:py-12">
    <div class="max-w-7xl mx-auto w-full grid grid-cols-1 xl:grid-cols-[1.05fr_0.95fr] gap-6 lg:gap-8 items-start">
      <section class="space-y-6 sm:space-y-7 animate-[card-in_0.55s_ease_both]" style="--i:0">
        <div class="space-y-4">
          <div class="eyebrow">{{ t('form.hero.eyebrow') }}</div>
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold leading-[0.95] tracking-tight text-balance">
            {{ t('form.hero.titleBefore') }}
            <span class="text-gradient">{{ t('form.hero.titleAccent') }}</span>
          </h1>
          <p class="text-base sm:text-lg text-slate-300/90 max-w-2xl leading-relaxed text-balance">
            {{ t('form.hero.description') }}
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="glass rounded-2xl p-4 animate-[card-in_0.55s_ease_both]" style="--i:1">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[var(--pro)] status-dot-pulse" />
              <span class="eyebrow !tracking-[0.14em]">{{ t('app.chips.pro') }}</span>
            </div>
            <p class="text-sm text-slate-200 leading-relaxed">{{ t('form.cards.proText') }}</p>
          </div>
          <div class="glass rounded-2xl p-4 animate-[card-in_0.55s_ease_both]" style="--i:2">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[var(--con)] status-dot-pulse" />
              <span class="eyebrow !tracking-[0.14em]">{{ t('app.chips.con') }}</span>
            </div>
            <p class="text-sm text-slate-200 leading-relaxed">{{ t('form.cards.conText') }}</p>
          </div>
          <div class="glass rounded-2xl p-4 animate-[card-in_0.55s_ease_both]" style="--i:3">
            <div class="flex items-center gap-2 mb-2">
              <span class="w-2.5 h-2.5 rounded-full bg-[var(--judge)] status-dot-pulse" />
              <span class="eyebrow !tracking-[0.14em]">{{ t('app.chips.judge') }}</span>
            </div>
            <p class="text-sm text-slate-200 leading-relaxed">{{ t('form.cards.judgeText') }}</p>
          </div>
        </div>

        <div class="panel-strong rounded-3xl p-5 sm:p-6 animate-[card-in_0.55s_ease_both]" style="--i:4">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <div class="eyebrow mb-1">{{ t('form.flow.eyebrow') }}</div>
              <div class="text-lg font-semibold text-white">{{ t('form.flow.title') }}</div>
            </div>
            <div class="flex items-center gap-2 text-xs text-slate-300/90 font-mono">
              <span class="px-2 py-1 rounded-full bg-white/5 border border-white/10">{{ t('form.flow.structuredJson') }}</span>
              <span class="px-2 py-1 rounded-full bg-white/5 border border-white/10">{{ t('form.flow.pydantic') }}</span>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-sm">
            <div class="panel-soft rounded-xl p-3">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.flow.rubricTitle') }}</div>
              <div class="text-slate-100 font-medium">{{ t('form.flow.rubricValue') }}</div>
            </div>
            <div class="panel-soft rounded-xl p-3">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.flow.outputTitle') }}</div>
              <div class="text-slate-100 font-medium">{{ t('form.flow.outputValue') }}</div>
            </div>
            <div class="panel-soft rounded-xl p-3">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.flow.questionsTitle') }}</div>
              <div class="text-slate-100 font-medium">{{ t('form.flow.questionsValue') }}</div>
            </div>
            <div class="panel-soft rounded-xl p-3">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.flow.actionsTitle') }}</div>
              <div class="text-slate-100 font-medium">{{ t('form.flow.actionsValue') }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-strong rounded-[1.75rem] p-5 sm:p-7 animate-[card-in_0.55s_ease_both] relative overflow-hidden" style="--i:2">
        <div class="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" aria-hidden="true" />
        <div class="absolute -right-10 -top-10 w-44 h-44 rounded-full blur-3xl bg-[rgba(68,212,200,0.12)]" aria-hidden="true" />
        <div class="absolute -left-14 bottom-0 w-44 h-44 rounded-full blur-3xl bg-[rgba(95,156,255,0.10)]" aria-hidden="true" />

        <div class="relative">
          <div class="flex flex-wrap items-center justify-between gap-2 mb-5">
            <div>
              <div class="eyebrow mb-1">{{ t('form.panel.eyebrow') }}</div>
              <h2 class="text-2xl font-semibold tracking-tight">{{ t('form.panel.title') }}</h2>
            </div>
            <div class="text-xs text-slate-400 panel-soft rounded-full px-3 py-1.5">{{ t('form.panel.frontendBadge') }}</div>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label for="decision" class="block text-sm font-medium text-slate-200 mb-2">{{ t('form.labels.decision') }}</label>
              <div class="input-shell rounded-2xl transition-all duration-200">
                <textarea
                  id="decision"
                  v-model="decision"
                  rows="4"
                  required
                  :placeholder="t('form.placeholders.decision')"
                  class="w-full bg-transparent rounded-2xl px-4 py-3.5 text-slate-100 placeholder:text-slate-500 resize-none outline-none text-[15px] leading-relaxed"
                />
              </div>
              <div class="mt-2 text-xs text-slate-500">{{ t('form.tips.decision') }}</div>
            </div>

            <div class="space-y-2">
              <button
                type="button"
                @click="showContext = !showContext"
                class="inline-flex items-center gap-2 text-sm text-slate-300 hover:text-white transition-colors"
                :aria-expanded="showContext"
              >
                <span
                  class="inline-flex items-center justify-center w-5 h-5 rounded-full border border-white/10 bg-white/5 text-xs transition-transform duration-200"
                  :class="{ 'rotate-45': showContext }"
                >+</span>
                {{ t('form.contextToggle') }}
              </button>

              <Transition name="expand">
                <div v-if="showContext" class="panel-soft rounded-2xl p-3">
                  <textarea
                    v-model="context"
                    rows="4"
                    :placeholder="t('form.placeholders.context')"
                    class="w-full bg-transparent rounded-xl px-2 py-2 text-slate-100 placeholder:text-slate-500 resize-none outline-none text-sm leading-relaxed"
                  />
                </div>
              </Transition>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-4 items-end">
              <div>
                <label for="model" class="block text-sm font-medium text-slate-200 mb-2">{{ t('form.labels.model') }}</label>
                <div class="input-shell rounded-2xl px-3 py-2.5">
                  <select
                    id="model"
                    v-model="model"
                    class="w-full bg-transparent text-sm text-slate-100 outline-none cursor-pointer"
                  >
                    <option
                      v-for="option in modelOptions"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }} - {{ option.hint }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="hidden sm:flex items-center gap-2 text-xs text-slate-400 mb-1">
                <span class="w-2 h-2 rounded-full bg-[var(--brand-cyan)]" />
                <span>{{ t('form.structuredResponse') }}</span>
              </div>
            </div>

            <button
              type="submit"
              class="cta-button w-full rounded-2xl px-5 py-4 font-semibold text-white tracking-[0.01em] transition duration-200 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-45 disabled:cursor-not-allowed disabled:hover:translate-y-0"
              :disabled="!canSubmit"
            >
              <span class="relative z-10 flex items-center justify-center gap-2">
                <span>{{ t('form.cta') }}</span>
                <span class="text-sm opacity-90">→</span>
              </span>
            </button>
          </form>

          <div class="surface-line my-5" />

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div class="panel-soft rounded-xl p-3.5">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.outputs.whatYouGetTitle') }}</div>
              <p class="text-slate-200 leading-relaxed">{{ t('form.outputs.whatYouGetText') }}</p>
            </div>
            <div class="panel-soft rounded-xl p-3.5">
              <div class="text-slate-400 text-xs mb-1">{{ t('form.outputs.missingInfoTitle') }}</div>
              <p class="text-slate-200 leading-relaxed">{{ t('form.outputs.missingInfoText') }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
