<script setup lang="ts">
import type { ChartRange } from '~/components/ChartCard.vue'
import type { MetricItem } from '~/components/MetricGrid.vue'

const range = ref<ChartRange>('24h')

const metrics = computed<MetricItem[]>(() => [
  { label: 'Requests', value: null, icon: 'i-lucide-activity' },
  { label: 'Tokens', value: null, icon: 'i-lucide-coins' },
  { label: 'Tokens/sec', value: null, icon: 'i-lucide-zap' },
  { label: 'Avg latency', value: null, icon: 'i-lucide-timer' },
  { label: 'TTFT', value: null, icon: 'i-lucide-hourglass' },
  { label: 'Active models', value: 0, icon: 'i-lucide-boxes' },
  { label: 'Running runtimes', value: 0, icon: 'i-lucide-cpu' },
  { label: 'Errors', value: 0, icon: 'i-lucide-triangle-alert' }
])

const hardware = computed<MetricItem[]>(() => [
  { label: 'GPU utilization', value: null, icon: 'i-lucide-circuit-board' },
  { label: 'GPU memory', value: null, icon: 'i-lucide-memory-stick' },
  { label: 'CPU', value: null, icon: 'i-lucide-gauge' },
  { label: 'RAM', value: null, icon: 'i-lucide-server' },
  { label: 'Disk', value: null, icon: 'i-lucide-hard-drive' }
])
</script>

<template>
  <PageShell title="Overview" description="What is installed, running, and how inference is performing.">
    <div>
      <p class="text-sm text-muted">
        Your local AI control plane. Metrics populate once a runtime is serving traffic.
      </p>
    </div>

    <section class="flex flex-col gap-3">
      <h2 class="text-sm font-semibold text-highlighted">
        Inference
      </h2>
      <MetricGrid :items="metrics" />
    </section>

    <section class="flex flex-col gap-3">
      <h2 class="text-sm font-semibold text-highlighted">
        Hardware
      </h2>
      <MetricGrid :items="hardware" />
    </section>

    <section class="grid gap-4 xl:grid-cols-2">
      <ChartCard v-model:range="range" title="Requests over time" />
      <ChartCard v-model:range="range" title="Tokens over time" />
      <ChartCard v-model:range="range" title="Latency" />
      <ChartCard v-model:range="range" title="Tokens/sec" />
    </section>
  </PageShell>
</template>
