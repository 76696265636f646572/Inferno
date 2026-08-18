<script setup lang="ts">
const props = withDefaults(defineProps<{
  status: string
  label?: string
  color?: 'success' | 'warning' | 'error' | 'neutral' | 'primary' | 'secondary' | 'info'
}>(), {
  label: undefined,
  color: undefined
})

const resolvedColor = computed(() => {
  if (props.color) {
    return props.color
  }
  const value = props.status.toLowerCase()
  if (['healthy', 'running', 'completed', 'ok', 'success'].includes(value)) {
    return 'success' as const
  }
  if (['starting', 'stopping', 'queued', 'downloading', 'verifying', 'degraded', 'warning'].includes(value)) {
    return 'warning' as const
  }
  if (['error', 'failed', 'crashed', 'unhealthy'].includes(value)) {
    return 'error' as const
  }
  return 'neutral' as const
})

const display = computed(() => props.label ?? props.status)
</script>

<template>
  <UBadge :color="resolvedColor" variant="subtle" class="capitalize">
    {{ display }}
  </UBadge>
</template>
