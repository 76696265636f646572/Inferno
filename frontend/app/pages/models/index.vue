<template>
  <PageShell title="Models" description="Registered GGUF models and quantizations.">
    <EmptyState
      title="No models installed"
      description="Find a model on Hugging Face and download your first GGUF model."
      icon="i-lucide-boxes"
      :actions="[{
        label: 'Browse Hugging Face',
        icon: 'i-lucide-search',
        to: '/models'
      }]"
    />
  </PageShell>
</template>
