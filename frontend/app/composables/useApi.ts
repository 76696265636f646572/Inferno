export interface ApiErrorBody {
  code: string
  message: string
  details?: Record<string, unknown>
}

export class InfernoApiError extends Error {
  readonly code: string
  readonly statusCode: number
  readonly details?: Record<string, unknown>

  constructor(code: string, message: string, statusCode: number, details?: Record<string, unknown>) {
    super(message)
    this.name = 'InfernoApiError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
  }
}

const HUMAN_MESSAGES: Record<string, string> = {
  MODEL_NOT_FOUND: 'The requested model does not exist.',
  VALIDATION_ERROR: 'The request is invalid.',
  UNAUTHORIZED: 'Authentication is required.',
  FORBIDDEN: 'You are not allowed to perform this action.',
  INTERNAL_ERROR: 'Something went wrong. Try again.',
  REQUEST_TOO_LARGE: 'The request is too large.'
}

export function formatApiError(error: unknown): string {
  if (error instanceof InfernoApiError) {
    return HUMAN_MESSAGES[error.code] ?? error.message
  }
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: { error?: ApiErrorBody } }).data
    if (data?.error?.code) {
      return HUMAN_MESSAGES[data.error.code] ?? data.error.message
    }
  }
  return 'Something went wrong. Try again.'
}

export function useApi() {
  const config = useRuntimeConfig()
  const apiBase = computed(() => String(config.public.apiBase).replace(/\/$/, ''))
  const wsBase = computed(() => String(config.public.wsBase).replace(/\/$/, ''))

  function apiUrl(path: string): string {
    const suffix = path.startsWith('/') ? path : `/${path}`
    return `${apiBase.value}${suffix}`
  }

  return { apiBase, wsBase, apiUrl, formatApiError }
}
