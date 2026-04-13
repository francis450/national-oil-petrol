<template>
  <div class="flex h-screen bg-chronos-black">
    <!-- Sidebar -->
    <transition
      enter-active-class="transition-all duration-300"
      leave-active-class="transition-all duration-200"
      enter-from-class="w-0 -translate-x-full"
      enter-to-class="w-64"
      leave-from-class="w-64"
      leave-to-class="w-0 -translate-x-full"
    >
      <aside
        v-if="uiStore.sidebarOpen"
        class="w-64 bg-gray-900 border-r border-gray-800 flex flex-col overflow-hidden"
      >
        <!-- Logo Section -->
        <div class="p-6 border-b border-gray-800 flex-shrink-0">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-8 h-8 rounded-lg bg-deepseek-blue flex items-center justify-center">
              <span class="text-white font-bold text-sm">NO</span>
            </div>
            <h1 class="text-xl font-bold text-deepseek-blue">National Oil</h1>
          </div>
          <p class="text-xs text-gray-500 ml-10">Management System</p>
        </div>

        <!-- Navigation Menu -->
        <nav class="flex-1 overflow-y-auto pt-4 pb-4">
          <SidebarMenu />
        </nav>

        <!-- Footer Actions -->
        <div class="p-4 border-t border-gray-800 flex-shrink-0 space-y-2">
          <button
            @click="showAbout = true"
            class="w-full text-left px-4 py-2 text-xs text-gray-400 hover:text-gray-300 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Version 1.0.0
          </button>
        </div>
      </aside>
    </transition>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Topbar -->
      <Topbar />

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto bg-chronos-black">
        <div class="max-w-7xl mx-auto px-6 py-8">
          <RouterView />
        </div>
      </main>
    </div>

    <!-- About Modal (placeholder) -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      leave-active-class="transition duration-200 ease-in"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showAbout" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-gray-900 rounded-lg p-6 max-w-sm border border-gray-800">
          <h2 class="text-lg font-bold text-white mb-2">National Oil System</h2>
          <p class="text-sm text-gray-400 mb-4">v1.0.0</p>
          <p class="text-xs text-gray-500 mb-6">A comprehensive petrol station management system built with Vue 3 and Frappe.</p>
          <button
            @click="showAbout = false"
            class="w-full px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Close
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'
import Topbar from '@/components/layout/Topbar.vue'
import SidebarMenu from '@/components/layout/SidebarMenu.vue'

const authStore = useAuthStore()
const uiStore = useUIStore()
const showAbout = ref(false)
</script>

<style scoped>
</style>
