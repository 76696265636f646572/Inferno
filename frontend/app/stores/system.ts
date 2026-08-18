import { defineStore } from 'pinia'
import { formatApiError, useApi } from '~/composables/useApi'

export type SystemHealth = 'healthy' | 'degraded' | 'unknown'

interface ReadyPayload {
  status: string
}

export const useSystemStore = defineStore('system', () => {
  const { apiUrl } = useApi()

  const status = ref<SystemHealth>('unknown')
  const lastError = ref<string | null>(null)
  const gpuUsedGb = ref<number | null>(null)
  const gpuTotalGb = ref<number | null>(null)
  const cpuPercent = ref<number | null>(null)
  const ramUsedGb = ref<number | null>(null)
  const ramTotalGb = ref<number | null>(null)

  const gpuLabel = computed(() => formatPair(gpuUsedGb.value, gpuTotalGb.value, 'GB'))
  const cpuLabel = computed(() => (cpuPercent.value == null ? '—' : `${Math.round(cpuPercent.value)}%`))
  const ramLabel = computed(() => formatPair(ramUsedGb.value, ramTotalGb.value, 'GB'))

  async function refresh() {
    try {
      const payload = await $fetch<ReadyPayload>(apiUrl('/api/v1/system/ready'))
      status.value = payload.status === 'ok' ? 'healthy' : 'degraded'
      lastError.value = null
    } catch (error) {
      status.value = 'degraded'
      lastError.value = formatApiError(error)
    }
  }

  return {
    status,
    lastError,
    gpuUsedGb,
    gpuTotalGb,
    cpuPercent,
    ramUsedGb,
    ramTotalGb,
    gpuLabel,
    cpuLabel,
    ramLabel,
    refresh
  }
})

function formatPair(used: number | null, total: number | null, unit: string): string {
  if (used == null || total == null) {
    return '—'
  }
  return `${used.toFixed(1)} / ${total.toFixed(0)} ${unit}`
}
