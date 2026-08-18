<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{
  error: NuxtError
}>()

const handleError = () => clearError({ redirect: '/' })
</script>

<template>
  <UApp>
    <div class="min-h-svh flex items-center justify-center p-6">
      <EmptyState
        :title="props.error.statusCode === 404 ? 'Page not found' : 'Something went wrong'"
        :description="props.error.statusCode === 404
          ? 'That route does not exist in Inferno.'
          : 'The dashboard hit an unexpected error. You can return to Overview.'"
        :icon="props.error.statusCode === 404 ? 'i-lucide-search-x' : 'i-lucide-triangle-alert'"
        :actions="[{ label: 'Back to Overview', icon: 'i-lucide-arrow-left', onClick: handleError }]"
      />
    </div>
  </UApp>
</template>
