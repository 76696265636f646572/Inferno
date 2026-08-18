<script setup lang="ts">
const props = defineProps<{
  title: string
  description?: string
}>()

const system = useSystemStore()

onMounted(() => {
  void system.refresh()
})

const healthLabel = computed(() => {
  if (system.status === 'healthy') {
    return 'System healthy'
  }
  if (system.status === 'degraded') {
    return 'System degraded'
  }
  return 'System unknown'
})

const healthColor = computed(() => {
  if (system.status === 'healthy') {
    return 'success' as const
  }
  if (system.status === 'degraded') {
    return 'warning' as const
  }
  return 'neutral' as const
})
</script>

<template>
  <UDashboardNavbar :title="props.title">
    <template #leading>
      <UDashboardSidebarToggle />
    </template>

    <template #right>
      <div class="hidden md:flex items-center gap-4 text-xs text-muted font-medium">
        <span class="inline-flex items-center gap-1.5">
          <span
            class="size-1.5 rounded-full"
            :class="{
              'bg-success': system.status === 'healthy',
              'bg-warning': system.status === 'degraded',
              'bg-muted': system.status === 'unknown'
            }"
          />
          {{ healthLabel }}
        </span>
        <span class="hidden lg:inline">GPU {{ system.gpuLabel }}</span>
        <span class="hidden lg:inline">CPU {{ system.cpuLabel }}</span>
        <span class="hidden xl:inline">RAM {{ system.ramLabel }}</span>
      </div>
      <StatusBadge :status="system.status" :label="healthLabel" :color="healthColor" class="md:hidden" />
    </template>
  </UDashboardNavbar>
  <p v-if="props.description" class="sr-only">
    {{ props.description }}
  </p>
</template>
