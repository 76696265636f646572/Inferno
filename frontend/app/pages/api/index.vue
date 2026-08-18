<script setup lang="ts">
const { apiBase } = useApi()
</script>

<template>
  <PageShell title="API" description="OpenAI-compatible gateway for local models.">
    <UCard variant="subtle">
      <div class="flex flex-col gap-4">
        <div>
          <p class="text-xs font-medium text-muted">
            Base URL
          </p>
          <code class="mt-1 inline-block text-sm font-mono text-highlighted">{{ apiBase }}/api/v1</code>
        </div>
        <p class="text-sm text-muted">
          Create an API key in Settings, then point Open WebUI, Continue, or the OpenAI SDK at this origin.
          Chat completions land in Phase 3. OpenAPI is already available at
          <NuxtLink :to="`${apiBase}/docs`" external class="text-primary">
            /docs
          </NuxtLink>.
        </p>
      </div>
    </UCard>
  </PageShell>
</template>
