<template>
  <PageShell title="Authentication" description="Optional OIDC for the dashboard.">
    <EmptyState
      title="Authentication is off"
      description="AUTH_ENABLED=false keeps local use frictionless. Enable generic OIDC (issuer, client id, secret) when you bind Inferno beyond localhost."
      icon="i-lucide-shield"
    />
  </PageShell>
</template>
