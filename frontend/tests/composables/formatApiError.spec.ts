import { describe, expect, it } from 'vitest'
import { formatApiError, InfernoApiError } from '../../app/composables/useApi'

describe('formatApiError', () => {
  it('translates known error codes', () => {
    const error = new InfernoApiError('MODEL_NOT_FOUND', 'raw', 404)
    expect(formatApiError(error)).toBe('The requested model does not exist.')
  })

  it('falls back for unknown errors', () => {
    expect(formatApiError(new Error('nope'))).toBe('Something went wrong. Try again.')
  })
})
