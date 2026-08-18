<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const { items } = useNavigation()
</script>

<template>
  <UDashboardSidebar
    id="inferno-sidebar"
    collapsible
    resizable
    :min-size="12"
    :default-size="16"
    :max-size="22"
    :ui="{ footer: 'border-t border-default' }"
  >
    <template #header="{ collapsed }">
      <NuxtLink
        to="/"
        class="flex items-center gap-2 min-w-0"
        :class="collapsed ? 'justify-center w-full' : ''"
      >
        <AppLogo class="size-7 shrink-0" />
        <span
          v-if="!collapsed"
          class="text-sm font-semibold tracking-tight text-highlighted truncate"
        >
          Inferno
        </span>
      </NuxtLink>
    </template>

    <template #default="{ collapsed }">
      <UNavigationMenu
        :collapsed="collapsed"
        :items="items as NavigationMenuItem[][]"
        orientation="vertical"
        class="data-[orientation=vertical]:w-full"
      />
    </template>

    <template #footer="{ collapsed }">
      <div class="flex items-center gap-1 w-full" :class="collapsed ? 'flex-col' : 'justify-between'">
        <p v-if="!collapsed" class="text-[11px] text-muted truncate px-1">
          Manage. Run. Observe.
        </p>
        <UColorModeButton size="sm" />
      </div>
    </template>
  </UDashboardSidebar>
</template>
