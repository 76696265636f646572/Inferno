import type { NavigationMenuItem } from '@nuxt/ui'

export function useNavigation() {
  const route = useRoute()

  const items = computed<NavigationMenuItem[][]>(() => [
    [
      {
        label: 'Overview',
        icon: 'i-lucide-layout-dashboard',
        to: '/',
        active: route.path === '/'
      },
      {
        label: 'Models',
        icon: 'i-lucide-boxes',
        to: '/models',
        active: route.path.startsWith('/models')
      },
      {
        label: 'Downloads',
        icon: 'i-lucide-download',
        to: '/downloads',
        active: route.path.startsWith('/downloads')
      },
      {
        label: 'Runtimes',
        icon: 'i-lucide-cpu',
        to: '/runtimes',
        active: route.path.startsWith('/runtimes')
      }
    ],
    [
      {
        label: 'Analytics',
        icon: 'i-lucide-chart-line',
        to: '/analytics/requests',
        defaultOpen: route.path.startsWith('/analytics'),
        children: [
          {
            label: 'Requests',
            icon: 'i-lucide-activity',
            to: '/analytics/requests',
            active: route.path === '/analytics/requests'
          },
          {
            label: 'Tokens',
            icon: 'i-lucide-coins',
            to: '/analytics/tokens',
            active: route.path === '/analytics/tokens'
          },
          {
            label: 'Performance',
            icon: 'i-lucide-gauge',
            to: '/analytics/performance',
            active: route.path === '/analytics/performance'
          }
        ]
      }
    ],
    [
      {
        label: 'API',
        icon: 'i-lucide-code',
        to: '/api',
        active: route.path === '/api'
      },
      {
        label: 'Settings',
        icon: 'i-lucide-settings',
        to: '/settings/general',
        defaultOpen: route.path.startsWith('/settings'),
        children: [
          {
            label: 'General',
            to: '/settings/general',
            active: route.path === '/settings/general'
          },
          {
            label: 'Storage',
            to: '/settings/storage',
            active: route.path === '/settings/storage'
          },
          {
            label: 'Authentication',
            to: '/settings/authentication',
            active: route.path === '/settings/authentication'
          },
          {
            label: 'API Keys',
            to: '/settings/api-keys',
            active: route.path === '/settings/api-keys'
          }
        ]
      }
    ]
  ])

  return { items }
}
