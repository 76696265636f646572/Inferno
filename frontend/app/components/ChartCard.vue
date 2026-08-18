<script setup lang="ts">
export type ChartRange = '1h' | '6h' | '24h' | '7d' | '30d'

const props = withDefaults(defineProps<{
  title: string
  description?: string
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  ranges?: ChartRange[]
}>(), {
  description: undefined,
  loading: false,
  emptyTitle: 'No data yet',
  emptyDescription: 'Metrics will appear once inference traffic is flowing.',
  ranges: () => ['1h', '6h', '24h', '7d', '30d']
})

const range = defineModel<ChartRange>('range', { default: '24h' })
</script>

<template>
  <UCard variant="subtle">
    <template #header>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-sm font-semibold text-highlighted">
            {{ props.title }}
          </h3>
          <p v-if="props.description" class="text-xs text-muted mt-0.5">
            {{ props.description }}
          </p>
        </div>
        <UButtonGroup size="xs">
          <UButton
            v-for="option in props.ranges"
            :key="option"
            :label="option"
            color="neutral"
            :variant="range === option ? 'subtle' : 'ghost'"
            @click="range = option"
          />
        </UButtonGroup>
      </div>
    </template>

    <USkeleton v-if="props.loading" class="h-48 w-full" />
    <slot v-else-if="$slots.default" />
    <EmptyState
      v-else
      :title="props.emptyTitle"
      :description="props.emptyDescription"
      icon="i-lucide-chart-spline"
      variant="naked"
      size="sm"
    />
  </UCard>
</template>
