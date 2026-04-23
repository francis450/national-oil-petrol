<template>
  <div class="flex h-screen bg-chronos-black">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div class="p-6 border-b border-gray-800">
        <h1 class="text-2xl font-bold text-deepseek-blue">National Oil</h1>
        <p class="text-sm text-gray-400">Management System</p>
      </div>

      <nav class="flex-1 overflow-y-auto p-4">
        <router-link
          to="/"
          class="nav-link"
          :class="{ 'bg-deepseek-blue': $route.path === '/' }"
        >
          🏠 Dashboard
        </router-link>
        <router-link to="/fuel/purchases" class="nav-link">⛽ Fuel Operations</router-link>
        <router-link to="/sales/entries" class="nav-link">💰 Sales</router-link>
        <router-link to="/receivables/debts" class="nav-link">📤 Receivables</router-link>
        <router-link to="/payables/credits" class="nav-link">📥 Payables</router-link>
      </nav>

      <div class="p-4 border-t border-gray-800">
        <button @click="logout" class="btn-danger w-full">Logout</button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Topbar -->
      <header class="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-white">{{ getPageTitle() }}</h2>
        <div class="flex items-center gap-4">
          <span class="text-gray-300">{{ authStore.user?.name }}</span>
          <button @click="uiStore.toggleDarkMode" class="text-gray-400 hover:text-white">
            {{ uiStore.darkMode ? '☀️' : '🌙' }}
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto">
        <div class="p-6">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import { computed } from 'vue'

const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUIStore()

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}

const getPageTitle = () => {
  const titles: Record<string, string> = {
    '/': 'Dashboard',
    '/fuel/purchases': 'Fuel Purchases',
    '/fuel/prices': 'Fuel Prices',
    '/fuel/readings': 'Pump Readings',
    '/sales/entries': 'Sales Entries',
    '/sales/targets': 'Sales Targets',
    '/receivables/debts': 'Customer Debts',
    '/receivables/payments': 'Debt Payments',
    '/payables/credits': 'Supplier Credits',
    '/payables/payments': 'Credit Payments',
  }
  return titles[router.currentRoute.value.path] || 'National Oil'
}
</script>

<style scoped>
.nav-link {
  @apply block px-4 py-2 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-deepseek-blue transition mb-2;
}
</style>
