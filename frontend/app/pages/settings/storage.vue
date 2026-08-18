<template>
  <PageShell title="Storage" description="Where GGUF files are stored on disk.">
    <EmptyState
      title="Model storage"
      description="Files are confined to MODEL_STORAGE_PATH (default ./models locally, /models in Docker). Inferno will not write outside that directory."
      icon="i-lucide-hard-drive"
    />
  </PageShell>
</template>
