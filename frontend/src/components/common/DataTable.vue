<template>
  <div class="space-y-4">
    <!-- Search and Filter Bar -->
    <div class="flex gap-4 items-center justify-between">
      <div class="flex gap-2 flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search..."
          class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-deepseek-blue"
        />
        <button
          @click="$emit('refresh')"
          class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors"
          title="Refresh"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button
          v-if="showExport"
          @click="$emit('export')"
          class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
        >
          📥 Export
        </button>
        <button
          v-if="showAdd"
          @click="$emit('add')"
          class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          + {{ addLabel }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-400">Loading...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-4 bg-red-900 bg-opacity-20 border border-red-800 rounded-lg text-red-200 text-sm">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-if="!loading && filteredData.length === 0" class="text-center py-12 bg-gray-900 rounded-lg border border-gray-800">
      <svg class="w-12 h-12 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-400">No {{ title?.toLowerCase() || 'data' }} found</p>
    </div>

    <!-- Data Table -->
    <div v-if="!loading && filteredData.length > 0" class="overflow-x-auto rounded-lg border border-gray-800">
      <table class="w-full text-sm">
        <thead class="bg-gray-900 border-b border-gray-800">
          <tr>
            <th v-for="col in columns" :key="col.key" class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">
              {{ col.label }}
            </th>
            <th v-if="showActions" class="px-4 py-3 text-center text-gray-400 font-medium text-xs uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in filteredData" :key="idx" class="border-b border-gray-800 hover:bg-gray-900 transition-colors">
            <td v-for="col in columns" :key="col.key" class="px-4 py-3 text-gray-300">
              <slot :name="`cell-${col.key}`" :data="row">
                {{ formatCellValue(row[col.key], col.type) }}
              </slot>
            </td>
            <td v-if="showActions" class="px-4 py-3 text-center space-x-2 flex justify-center">
              <button
                v-if="showEdit"
                @click="$emit('edit', row)"
                class="px-2 py-1 text-xs bg-blue-900 text-blue-200 rounded hover:bg-blue-800 transition-colors"
              >
                Edit
              </button>
              <button
                v-if="showDelete"
                @click="$emit('delete', row)"
                class="px-2 py-1 text-xs bg-red-900 text-red-200 rounded hover:bg-red-800 transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredData.length > 0" class="flex items-center justify-between text-sm text-gray-400">
      <p>Showing {{ filteredData.length }} of {{ data.length }} records</p>
      <div v-if="showPagination" class="flex gap-2">
        <button class="px-3 py-1 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700">←</button>
        <span class="px-3 py-1">1 / 1</span>
        <button class="px-3 py-1 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700">→</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Column {
  key: string
  label: string
  type?: 'text' | 'number' | 'currency' | 'date' | 'status'
}

const props = withDefaults(defineProps<{
  title: string
  columns: Column[]
  data: any[]
  loading?: boolean
  error?: string
  showAdd?: boolean
  showEdit?: boolean
  showDelete?: boolean
  showActions?: boolean
  showExport?: boolean
  showPagination?: boolean
  addLabel?: string
}>(), {
  loading: false,
  error: '',
  showAdd: true,
  showEdit: true,
  showDelete: false,
  showActions: true,
  showExport: false,
  showPagination: true,
  addLabel: 'New',
})

const emit = defineEmits<{
  add: []
  edit: [data: any]
  delete: [data: any]
  refresh: []
  export: []
}>()

const searchQuery = ref('')

const filteredData = computed(() => {
  if (!searchQuery.value) return props.data
  
  const query = searchQuery.value.toLowerCase()
  return props.data.filter(row =>
    Object.values(row).some(val =>
      String(val).toLowerCase().includes(query)
    )
  )
})

const formatCellValue = (value: any, type?: string): string => {
  if (value === null || value === undefined) return '—'
  
  switch (type) {
    case 'currency':
      return `KSh ${Number(value).toLocaleString()}`
    case 'number':
      return Number(value).toLocaleString()
    case 'date':
      return new Date(value).toLocaleDateString('en-KE')
    case 'status':
      return String(value).charAt(0).toUpperCase() + String(value).slice(1)
    default:
      return String(value)
  }
}
</script>

<style scoped>
</style>
