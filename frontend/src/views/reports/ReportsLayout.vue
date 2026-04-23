<template>
  <div class="flex gap-6 h-full">
    <!-- Report picker sidebar -->
    <aside class="w-56 shrink-0">
      <div class="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-800">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400">Reports</h2>
        </div>

        <nav class="py-2">
          <template v-for="category in CATEGORIES" :key="category">
            <!-- Category heading -->
            <div class="px-4 pt-3 pb-1">
              <span class="text-xs font-semibold uppercase tracking-wider text-gray-500">{{ category }}</span>
            </div>

            <!-- Report links -->
            <router-link
              v-for="report in REPORTS_BY_CATEGORY[category]"
              :key="report.slug"
              :to="`/reports/${report.slug}`"
              class="flex items-center px-4 py-2 text-xs text-gray-400 hover:bg-gray-800 hover:text-gray-200 transition-colors"
              active-class="bg-gray-800 text-deepseek-blue"
            >
              <span class="w-1 h-1 rounded-full bg-gray-600 mr-2.5 shrink-0"></span>
              {{ report.name }}
            </router-link>
          </template>
        </nav>
      </div>
    </aside>

    <!-- Report content -->
    <main class="flex-1 min-w-0">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { CATEGORIES, REPORTS_BY_CATEGORY } from './reports.config'
</script>
