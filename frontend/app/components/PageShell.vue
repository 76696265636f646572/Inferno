<script setup lang="ts">
const props = defineProps<{
  title: string
  description?: string
}>()

useSeoMeta({
  title: () => props.title,
  description: () => props.description
})
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <AppHeader :title="title" :description="description" />
    </template>
    <template #body>
      <div class="flex flex-col gap-6">
        <slot />
      </div>
    </template>
  </UDashboardPanel>
</template>
