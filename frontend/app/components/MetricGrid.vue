<script setup lang="ts">
export interface MetricItem {
  label: string
  value?: string | number | null
  hint?: string
  icon?: string
  loading?: boolean
}

withDefaults(defineProps<{
  items: MetricItem[]
  loading?: boolean
}>(), {
  loading: false
})
</script>

<template>
  <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
    <MetricCard
      v-for="item in items"
      :key="item.label"
      :label="item.label"
      :value="item.value"
      :hint="item.hint"
      :icon="item.icon"
      :loading="loading || item.loading"
    />
  </div>
</template>
