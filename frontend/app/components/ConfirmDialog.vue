<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

const props = withDefaults(defineProps<{
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  confirmColor?: 'error' | 'primary' | 'neutral'
  loading?: boolean
}>(), {
  description: undefined,
  confirmLabel: 'Confirm',
  cancelLabel: 'Cancel',
  confirmColor: 'error',
  loading: false
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function onCancel() {
  open.value = false
  emit('cancel')
}

function onConfirm() {
  emit('confirm')
}
</script>

<template>
  <UModal
    v-model:open="open"
    :title="props.title"
    :description="props.description"
    :ui="{ footer: 'justify-end gap-2' }"
  >
    <template v-if="$slots.body" #body>
      <slot name="body" />
    </template>
    <template #footer>
      <UButton
        :label="props.cancelLabel"
        color="neutral"
        variant="outline"
        :disabled="props.loading"
        @click="onCancel"
      />
      <UButton
        :label="props.confirmLabel"
        :color="props.confirmColor"
        :loading="props.loading"
        @click="onConfirm"
      />
    </template>
  </UModal>
</template>
