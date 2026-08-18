<script setup lang="ts">
withDefaults(defineProps<{
  label: string
  value?: string | number | null
  hint?: string
  icon?: string
  loading?: boolean
}>(), {
  value: null,
  hint: undefined,
  icon: undefined,
  loading: false
})
</script>

<template>
  <UCard variant="subtle">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <p class="text-xs font-medium text-muted">
          {{ label }}
        </p>
        <USkeleton v-if="loading" class="h-7 w-20 mt-2" />
        <p v-else class="mt-1 text-2xl font-semibold tracking-tight text-highlighted tabular-nums">
          {{ value ?? '—' }}
        </p>
        <p v-if="hint && !loading" class="mt-1 text-xs text-muted">
          {{ hint }}
        </p>
      </div>
      <UIcon
        v-if="icon"
        :name="icon"
        class="size-4 text-primary/80 mt-0.5 shrink-0"
      />
    </div>
  </UCard>
</template>
