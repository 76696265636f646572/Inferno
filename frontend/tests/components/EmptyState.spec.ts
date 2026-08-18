import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import EmptyState from '../../app/components/EmptyState.vue'

describe('EmptyState', () => {
  it('renders title and description', async () => {
    const wrapper = await mountSuspended(EmptyState, {
      props: {
        title: 'No models installed',
        description: 'Find a model on Hugging Face and download your first GGUF model.'
      }
    })

    expect(wrapper.text()).toContain('No models installed')
    expect(wrapper.text()).toContain('Find a model on Hugging Face')
  })
})
