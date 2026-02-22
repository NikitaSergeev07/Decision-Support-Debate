import { ref } from 'vue'

export type Locale = 'en' | 'ru'

interface Messages {
  [key: string]: string | Messages
}
type Params = Record<string, string | number>

const STORAGE_KEY = 'decision-debate-locale'

const messages: Record<Locale, Messages> = {
  en: {
    app: {
      title: 'Decision Support Debate',
      languageLabel: 'Language',
      languageAria: 'Switch interface language',
      chips: {
        pro: 'PRO',
        con: 'CON',
        judge: 'JUDGE',
      },
      locales: {
        en: 'EN',
        ru: 'RU',
      },
    },
    form: {
      hero: {
        eyebrow: 'Decision Intelligence Workspace',
        titleBefore: 'Let three agents',
        titleAccent: 'stress-test your next move',
        description:
          'PRO and CON build structured arguments, then a JUDGE scores both sides on a weighted rubric and returns a clear verdict with risks, assumptions, and next actions.',
      },
      cards: {
        proText: 'Builds 3-8 strongest reasons to proceed, including evidence and known risks.',
        conText: 'Surfaces downside scenarios, execution risks, and hidden costs before you commit.',
        judgeText: 'Scores both sides with a rubric and gives verdict, confidence, and next 48h actions.',
      },
      flow: {
        eyebrow: 'Flow',
        title: 'START -> PRO -> CON -> JUDGE -> END',
        structuredJson: 'Structured JSON',
        pydantic: 'Pydantic',
        rubricTitle: 'Rubric',
        rubricValue: 'Weighted scorecard',
        outputTitle: 'Output',
        outputValue: 'Verdict + risks',
        questionsTitle: 'Questions',
        questionsValue: 'If info missing',
        actionsTitle: 'Actions',
        actionsValue: 'Next 48h plan',
      },
      panel: {
        eyebrow: 'Start a Debate',
        title: 'Frame your decision',
        frontendBadge: 'Vue + TS frontend',
      },
      labels: {
        decision: 'Decision to evaluate',
        model: 'Gemini model',
      },
      placeholders: {
        decision: 'e.g. Hire a second backend engineer in the next 30 days',
        context: 'e.g. Startup, 6-month runway, 2 senior devs, delivery pressure from enterprise pilot',
      },
      tips: {
        decision: 'Tip: include timeframe or target outcome for a better verdict.',
      },
      contextToggle: 'Add context and constraints',
      structuredResponse: 'Structured JSON response',
      cta: 'Launch Debate',
      outputs: {
        whatYouGetTitle: 'What you get',
        whatYouGetText:
          'Verdict, scorecard, key risks, assumptions to verify, and a concrete next-48h action list.',
        missingInfoTitle: 'If data is missing',
        missingInfoText:
          'Judge can still return a verdict and attach clarifying questions for the next iteration.',
      },
      modelHints: {
        defaultFast: 'default / fast',
        balanced: 'balanced',
        cheaperFast: 'cheaper / fast',
      },
    },
    debate: {
      header: {
        newDecision: 'New decision',
        eyebrow: 'Decision Under Review',
      },
      meta: {
        phase: 'Phase',
        agentsDone: 'Agents done',
        agentsDoneHint: 'PRO, CON, JUDGE',
        transport: 'Transport',
        transportValue: 'SSE stream',
        transportHint: 'Incremental updates',
      },
      phase: {
        liveLabel: 'Live Debate',
        liveHint: 'Streaming agent outputs',
        completeLabel: 'Complete',
        completeHint: 'Verdict ready',
        errorLabel: 'Error',
        errorHint: 'See message below',
        idleLabel: 'Idle',
        idleHint: 'Awaiting request',
      },
      error: {
        title: 'Debate request failed',
      },
      columns: {
        pro: 'PRO Arguments',
        con: 'CON Arguments',
        items: '{count} items',
        proIdleHint: 'PRO agent will generate 3-8 arguments supporting the decision.',
        conIdleHint: 'CON agent will challenge feasibility, cost, and uncertainty before you act.',
      },
      judgeThinking: {
        title: 'Judge is deliberating',
        text: 'Scoring PRO vs CON across the weighted rubric and writing the verdict.',
      },
    },
    statusBar: {
      eyebrow: 'Execution Pipeline',
      title: 'Live agent progress',
      streamBadge: 'Streaming updates from backend',
      agents: {
        pro: { label: 'PRO', title: 'Build upside case' },
        con: { label: 'CON', title: 'Stress downside' },
        judge: { label: 'JUDGE', title: 'Score and verdict' },
      },
      states: {
        thinking: 'thinking',
        done: 'done',
        queued: 'queued',
      },
    },
    argument: {
      badge: 'Argument',
      confidence: 'Confidence',
      confidenceSignal: 'Confidence signal',
      assumptionBacked: 'Assumption-backed',
      evidenceBacked: 'Evidence-backed',
      riskIncluded: 'Risk included',
      hideDetails: 'Hide argument details',
      showDetails: 'Show evidence, reasoning and risk',
      detailLabels: {
        reasoning: 'Reasoning',
        evidence: 'Evidence',
        risk: 'Risk',
      },
    },
    verdict: {
      judgeEyebrow: 'Judge Verdict',
      decisionSignal: 'Decision Signal',
      confidence: 'Confidence',
      confidenceSuffix: 'confidence',
      interpretationTitle: 'Interpretation',
      interpretationText:
        'Weighted totals summarize the scorecard only. Final verdict may still be conditional if critical evidence is missing or risks are hard to reverse.',
      metrics: {
        proTotal: 'PRO weighted total',
        conTotal: 'CON weighted total',
        netSwing: 'Net swing (PRO - CON)',
      },
      missingInfo: {
        title: 'Judge flagged missing information',
        text: 'The verdict is usable, but the confidence can improve after answering clarifying questions below.',
        flag: 'needs_more_info = true',
      },
      scorecard: {
        eyebrow: 'Scorecard',
        title: 'Rubric comparison by criterion',
        subtitle: '0-10 scores with criterion weights',
        weight: '{percent}% weight',
        pro: 'PRO',
        con: 'CON',
        tie: 'TIE',
      },
      sections: {
        keyRisks: 'Key Risks',
        assumptions: 'Assumptions To Verify',
        nextActions: 'Next 48h Actions',
        followUpEyebrow: 'Follow-up',
        clarifyingQuestions: 'Clarifying Questions',
        questionsCount: '{count} questions',
        clarifyingHelp:
          'Answer any of the questions below and rerun the debate. You can use quick options or write a custom response.',
        answerLabel: 'Your answer',
        answerPlaceholder: 'Type an answer or tap a quick option above…',
        answersProgress: 'Answered: {answered}/{total}',
        submitClarifications: 'Recompute with answers',
        recomputing: 'Recomputing…',
      },
      decision: {
        go: 'GO',
        no_go: 'NO GO',
        conditional_go: 'CONDITIONAL GO',
      },
      winner: {
        pro: 'PRO wins',
        con: 'CON wins',
        tie: 'Tie',
      },
    },
  },
  ru: {
    app: {
      title: 'Decision Support Debate',
      languageLabel: 'Язык',
      languageAria: 'Переключить язык интерфейса',
      chips: {
        pro: 'ЗА',
        con: 'ПРОТИВ',
        judge: 'СУДЬЯ',
      },
      locales: {
        en: 'EN',
        ru: 'RU',
      },
    },
    form: {
      hero: {
        eyebrow: 'Пространство анализа решений',
        titleBefore: 'Пусть три агента',
        titleAccent: 'проверят ваше решение на прочность',
        description:
          'PRO и CON собирают структурированные аргументы, после чего JUDGE оценивает обе стороны по взвешенной рубрике и возвращает вердикт, риски, допущения и следующие действия.',
      },
      cards: {
        proText: 'Собирает 3-8 сильных аргументов за действие, включая факты/наблюдения и признание рисков.',
        conText: 'Подсвечивает негативные сценарии, риски исполнения и скрытые издержки до принятия решения.',
        judgeText: 'Оценивает обе стороны по рубрике и выдает вердикт, уровень уверенности и план на ближайшие 48 часов.',
      },
      flow: {
        eyebrow: 'Поток',
        title: 'СТАРТ -> ЗА -> ПРОТИВ -> СУДЬЯ -> ФИНИШ',
        structuredJson: 'Структурированный JSON',
        pydantic: 'Pydantic',
        rubricTitle: 'Рубрика',
        rubricValue: 'Взвешенная карта оценок',
        outputTitle: 'Выход',
        outputValue: 'Вердикт + риски',
        questionsTitle: 'Вопросы',
        questionsValue: 'Если данных мало',
        actionsTitle: 'Действия',
        actionsValue: 'План на 48ч',
      },
      panel: {
        eyebrow: 'Запуск дебата',
        title: 'Сформулируйте решение',
        frontendBadge: 'Vue + TS фронтенд',
      },
      labels: {
        decision: 'Решение для оценки',
        model: 'Модель Gemini',
      },
      placeholders: {
        decision: 'например: Нанять второго backend-инженера в ближайшие 30 дней',
        context: 'например: Стартап, runway 6 месяцев, 2 senior-разработчика, давление по срокам от enterprise-пилота',
      },
      tips: {
        decision: 'Совет: добавьте срок или целевой результат, чтобы вердикт был точнее.',
      },
      contextToggle: 'Добавить контекст и ограничения',
      structuredResponse: 'Структурированный JSON-ответ',
      cta: 'Запустить дебаты',
      outputs: {
        whatYouGetTitle: 'Что получите',
        whatYouGetText:
          'Вердикт, карту оценок, ключевые риски, допущения для проверки и конкретный список действий на ближайшие 48 часов.',
        missingInfoTitle: 'Если данных не хватает',
        missingInfoText:
          'Судья всё равно может выдать вердикт и приложить уточняющие вопросы для следующей итерации.',
      },
      modelHints: {
        defaultFast: 'по умолчанию / быстро',
        balanced: 'сбалансировано',
        cheaperFast: 'дешевле / быстро',
      },
    },
    debate: {
      header: {
        newDecision: 'Новое решение',
        eyebrow: 'Решение на разборе',
      },
      meta: {
        phase: 'Этап',
        agentsDone: 'Завершено агентов',
        agentsDoneHint: 'ЗА, ПРОТИВ, СУДЬЯ',
        transport: 'Транспорт',
        transportValue: 'SSE-поток',
        transportHint: 'Пошаговые обновления',
      },
      phase: {
        liveLabel: 'Дебаты в процессе',
        liveHint: 'Идут ответы агентов',
        completeLabel: 'Готово',
        completeHint: 'Вердикт готов',
        errorLabel: 'Ошибка',
        errorHint: 'См. сообщение ниже',
        idleLabel: 'Ожидание',
        idleHint: 'Ожидает запуск',
      },
      error: {
        title: 'Не удалось выполнить дебаты',
      },
      columns: {
        pro: 'Аргументы ЗА',
        con: 'Аргументы ПРОТИВ',
        items: '{count} шт.',
        proIdleHint: 'Агент PRO сгенерирует 3-8 аргументов в поддержку решения.',
        conIdleHint: 'Агент CON проверит решение на реализуемость, стоимость и неопределенность.',
      },
      judgeThinking: {
        title: 'Судья анализирует',
        text: 'Сравнивает PRO и CON по взвешенной рубрике и формирует вердикт.',
      },
    },
    statusBar: {
      eyebrow: 'Пайплайн выполнения',
      title: 'Прогресс агентов',
      streamBadge: 'Потоковые обновления с бэкенда',
      agents: {
        pro: { label: 'ЗА', title: 'Собрать аргументы в пользу' },
        con: { label: 'ПРОТИВ', title: 'Проверить риски и минусы' },
        judge: { label: 'СУДЬЯ', title: 'Оценить и вынести вердикт' },
      },
      states: {
        thinking: 'думает',
        done: 'готово',
        queued: 'в очереди',
      },
    },
    argument: {
      badge: 'Аргумент',
      confidence: 'Уверенность',
      confidenceSignal: 'Сигнал уверенности',
      assumptionBacked: 'Основано на допущении',
      evidenceBacked: 'Основано на фактах',
      riskIncluded: 'Риск указан',
      hideDetails: 'Скрыть детали аргумента',
      showDetails: 'Показать факты, обоснование и риск',
      detailLabels: {
        reasoning: 'Обоснование',
        evidence: 'Факты / наблюдение',
        risk: 'Риск',
      },
    },
    verdict: {
      judgeEyebrow: 'Вердикт судьи',
      decisionSignal: 'Сигнал решения',
      confidence: 'Уверенность',
      confidenceSuffix: 'уровень уверенности',
      interpretationTitle: 'Как читать результат',
      interpretationText:
        'Взвешенные суммы отражают только карту оценок. Итоговый вердикт может оставаться условным, если критичных данных недостаточно или риски плохо обратимы.',
      metrics: {
        proTotal: 'Взвешенный итог PRO',
        conTotal: 'Взвешенный итог CON',
        netSwing: 'Разница (PRO - CON)',
      },
      missingInfo: {
        title: 'Судья отметил нехватку данных',
        text: 'Вердикт уже можно использовать, но уверенность можно повысить после ответов на вопросы ниже.',
        flag: 'Требуется больше данных',
      },
      scorecard: {
        eyebrow: 'Карта оценок',
        title: 'Сравнение по критериям рубрики',
        subtitle: 'Оценки 0-10 с весами критериев',
        weight: 'вес {percent}%',
        pro: 'ЗА',
        con: 'ПРОТИВ',
        tie: 'НИЧЬЯ',
      },
      sections: {
        keyRisks: 'Ключевые риски',
        assumptions: 'Допущения для проверки',
        nextActions: 'Действия на 48ч',
        followUpEyebrow: 'Следующий шаг',
        clarifyingQuestions: 'Уточняющие вопросы',
        questionsCount: '{count} вопросов',
        clarifyingHelp:
          'Ответьте на любые вопросы ниже и пересчитайте дебаты. Можно выбрать быстрый вариант или написать свой ответ.',
        answerLabel: 'Ваш ответ',
        answerPlaceholder: 'Введите ответ или выберите быстрый вариант выше…',
        answersProgress: 'Заполнено: {answered}/{total}',
        submitClarifications: 'Пересчитать с ответами',
        recomputing: 'Пересчитываем…',
      },
      decision: {
        go: 'ДА',
        no_go: 'НЕТ',
        conditional_go: 'УСЛОВНО',
      },
      winner: {
        pro: 'Побеждает ЗА',
        con: 'Побеждает ПРОТИВ',
        tie: 'Ничья',
      },
    },
  },
}

function detectInitialLocale(): Locale {
  // UI is intentionally Russian-only.
  return 'ru'
}

const locale = ref<Locale>(detectInitialLocale())

function applyLocaleToDocument(next: Locale) {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = next
  }
}

applyLocaleToDocument(locale.value)

function getByPath(obj: Messages, path: string): string | Messages | undefined {
  return path.split('.').reduce<string | Messages | undefined>((acc, key) => {
    if (!acc || typeof acc === 'string') return undefined
    return acc[key]
  }, obj)
}

function interpolate(template: string, params?: Params): string {
  if (!params) return template
  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(params[key] ?? `{${key}}`))
}

export function setLocale(next: Locale) {
  // Keep API surface for compatibility, but lock interface to RU.
  locale.value = 'ru'
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, 'ru')
  }
  applyLocaleToDocument('ru')
}

export function t(path: string, params?: Params): string {
  const current = getByPath(messages[locale.value], path)
  if (typeof current === 'string') return interpolate(current, params)

  const fallback = getByPath(messages.en, path)
  if (typeof fallback === 'string') return interpolate(fallback, params)

  return path
}

export function useI18n() {
  return {
    locale,
    setLocale,
    t,
  }
}
