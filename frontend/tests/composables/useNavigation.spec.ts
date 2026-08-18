import { describe, expect, it } from 'vitest'
import { useNavigation } from '../../app/composables/useNavigation'

describe('useNavigation', () => {
  it('includes the primary Inferno sections', () => {
    const { items } = useNavigation()
    const labels = items.value.flatMap(group => group.map(item => item.label))

    expect(labels).toEqual(expect.arrayContaining([
      'Overview',
      'Models',
      'Downloads',
      'Runtimes',
      'Analytics',
      'API',
      'Settings'
    ]))
  })
})
