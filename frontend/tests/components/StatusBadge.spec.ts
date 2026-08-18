import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import StatusBadge from '../../app/components/StatusBadge.vue'

describe('StatusBadge', () => {
  it('maps healthy statuses to a success badge', async () => {
    const wrapper = await mountSuspended(StatusBadge, {
      props: { status: 'healthy' }
    })

    expect(wrapper.text()).toContain('healthy')
    expect(wrapper.html()).toContain('success')
  })

  it('maps crashed statuses to an error badge', async () => {
    const wrapper = await mountSuspended(StatusBadge, {
      props: { status: 'crashed' }
    })

    expect(wrapper.text()).toContain('crashed')
  })
})
