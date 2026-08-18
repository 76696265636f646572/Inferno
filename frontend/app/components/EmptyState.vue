<script setup lang="ts">
import type { ButtonProps } from '@nuxt/ui'

withDefaults(defineProps<{
  title: string
  description?: string
  icon?: string
  loading?: boolean
  variant?: 'outline' | 'solid' | 'soft' | 'subtle' | 'naked'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  actions?: ButtonProps[]
}>(), {
  description: undefined,
  icon: 'i-lucide-inbox',
  loading: false,
  variant: 'naked',
  size: 'md',
  actions: () => []
})
</script>

<template>
  <UEmpty
    :title="title"
    :description="description"
    :icon="icon"
    :loading="loading"
    :variant="variant"
    :size="size"
    :actions="actions"
  >
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </UEmpty>
</template>
