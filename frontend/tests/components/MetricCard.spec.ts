import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MetricCard from '../../app/components/MetricCard.vue'

describe('MetricCard', () => {
  it('shows an em dash when the value is missing', async () => {
    const wrapper = await mountSuspended(MetricCard, {
      props: { label: 'Requests' }
    })

    expect(wrapper.text()).toContain('Requests')
    expect(wrapper.text()).toContain('—')
  })

  it('renders a numeric value', async () => {
    const wrapper = await mountSuspended(MetricCard, {
      props: { label: 'Active models', value: 3 }
    })

    expect(wrapper.text()).toContain('3')
  })
})
