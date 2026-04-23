<template>
  <div class="space-y-5">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">{{ config?.name ?? 'Report' }}</h1>
      <p class="text-gray-400 text-sm">{{ config?.category }} &rsaquo; {{ config?.name }}</p>
    </div>

    <!-- Unknown report -->
    <div v-if="!config" class="p-6 bg-red-900 bg-opacity-20 border border-red-800 rounded-lg text-red-200">
      Unknown report "{{ route.params.reportSlug }}". Check the URL.
    </div>

    <template v-else>
      <!-- Filter panel -->
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <div class="flex flex-wrap gap-4 items-end">
          <template v-for="filter in config.filters" :key="filter.name">
            <div class="flex flex-col gap-1">
              <label class="text-xs font-medium text-gray-400 uppercase tracking-wide">
                {{ filter.label }}
                <span v-if="filter.required" class="text-red-400 ml-0.5">*</span>
              </label>

              <!-- Date -->
              <input
                v-if="filter.type === 'Date'"
                v-model="filterValues[filter.name]"
                type="date"
                class="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-deepseek-blue w-40"
              />

              <!-- Int -->
              <input
                v-else-if="filter.type === 'Int'"
                v-model.number="filterValues[filter.name]"
                type="number"
                :placeholder="filter.label"
                class="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-deepseek-blue w-28"
              />

              <!-- Select -->
              <select
                v-else-if="filter.type === 'Select'"
                v-model="filterValues[filter.name]"
                class="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-deepseek-blue"
              >
                <option v-for="opt in selectOptions(filter.options ?? '')" :key="opt" :value="opt">
                  {{ opt === '' ? '— All —' : opt }}
                </option>
              </select>

              <!-- Link / Data -->
              <input
                v-else
                v-model="filterValues[filter.name]"
                type="text"
                :placeholder="filter.type === 'Link' ? `${filter.options} name…` : filter.label"
                class="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-deepseek-blue w-44"
              />
            </div>
          </template>

          <!-- Run button -->
          <button
            @click="runReport"
            :disabled="loading || !allRequiredFilled"
            class="px-5 py-2 bg-deepseek-blue text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Running…' : 'Run Report' }}
          </button>

          <!-- Clear button (only after results) -->
          <button
            v-if="result"
            @click="clearResult"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 text-sm hover:bg-gray-700 transition-colors"
          >
            Clear
          </button>
        </div>

        <p v-if="!allRequiredFilled" class="mt-2 text-xs text-yellow-400">
          Fill in the required filter(s) marked with * to run the report.
        </p>
      </section>

      <!-- Error -->
      <div v-if="error" class="p-4 bg-red-900 bg-opacity-20 border border-red-800 rounded-lg text-red-200 text-sm">
        {{ error }}
      </div>

      <!-- Results -->
      <section v-if="result" class="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden">
        <!-- Result header -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-gray-800">
          <p class="text-sm text-gray-400">
            <span class="text-white font-semibold">{{ result.rows.length }}</span> row{{ result.rows.length !== 1 ? 's' : '' }}
          </p>
          <button
            @click="exportCsv"
            class="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-gray-300 text-xs hover:bg-gray-700 transition-colors"
          >
            Export CSV
          </button>
        </div>

        <!-- Empty result -->
        <div v-if="result.rows.length === 0" class="py-12 text-center text-gray-400 text-sm">
          No data found for the selected filters.
        </div>

        <!-- Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th
                  v-for="col in result.columns"
                  :key="col.fieldname"
                  class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider whitespace-nowrap"
                  :style="col.width ? `min-width: ${col.width}px` : ''"
                >
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in result.rows"
                :key="idx"
                class="border-b border-gray-800 hover:bg-gray-950 transition-colors"
              >
                <td
                  v-for="col in result.columns"
                  :key="col.fieldname"
                  class="px-4 py-2.5 text-gray-300 whitespace-nowrap"
                >
                  {{ formatCell(row[col.fieldname], col.fieldtype) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Placeholder before first run -->
      <div v-else-if="!loading && !error" class="py-16 text-center text-gray-500 border border-dashed border-gray-800 rounded-lg">
        Set your filters above and click <span class="text-gray-300">Run Report</span> to see results.
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { runReport as apiRunReport, type ReportResult } from '@/api/reports'
import { REPORT_BY_SLUG, type ReportConfig } from './reports.config'

const route = useRoute()

const config = computed<ReportConfig | null>(
  () => REPORT_BY_SLUG[route.params.reportSlug as string] ?? null
)

// ─── filter state ───────────────────────────────────────────────────────────
const filterValues = ref<Record<string, any>>({})

function initFilters(cfg: ReportConfig | null) {
  if (!cfg) return
  const vals: Record<string, any> = {}
  for (const f of cfg.filters) {
    vals[f.name] = f.default !== undefined ? f.default : ''
  }
  filterValues.value = vals
}

watch(config, (cfg) => initFilters(cfg), { immediate: true })

const allRequiredFilled = computed(() => {
  if (!config.value) return false
  return config.value.filters
    .filter((f) => f.required)
    .every((f) => {
      const v = filterValues.value[f.name]
      return v !== '' && v !== null && v !== undefined
    })
})

// ─── report execution ───────────────────────────────────────────────────────
const loading = ref(false)
const error = ref('')
const result = ref<ReportResult | null>(null)

async function runReport() {
  if (!config.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await apiRunReport(config.value.name, { ...filterValues.value })
  } catch (err: any) {
    error.value =
      err?.response?.data?.exception ||
      err?.response?.data?.message ||
      err?.message ||
      'Failed to run report.'
  } finally {
    loading.value = false
  }
}

function clearResult() {
  result.value = null
  error.value = ''
}

// ─── helpers ────────────────────────────────────────────────────────────────
function selectOptions(raw: string): string[] {
  return raw.split('\n')
}

function formatCell(value: any, fieldtype: string): string {
  if (value === null || value === undefined || value === '') return '—'
  switch (fieldtype) {
    case 'Currency':
      return `KSh ${Number(value).toLocaleString('en-KE', { minimumFractionDigits: 2 })}`
    case 'Float':
    case 'Int':
      return Number(value).toLocaleString('en-KE')
    case 'Percent':
      return `${Number(value).toFixed(1)}%`
    case 'Date':
      return new Date(value).toLocaleDateString('en-KE')
    default:
      return String(value)
  }
}

function exportCsv() {
  if (!result.value) return
  const { columns, rows } = result.value
  const header = columns.map((c) => c.label).join(',')
  const body = rows
    .map((row) =>
      columns
        .map((col) => {
          const v = row[col.fieldname]
          const s = v === null || v === undefined ? '' : String(v)
          return s.includes(',') || s.includes('"') || s.includes('\n')
            ? `"${s.replace(/"/g, '""')}"`
            : s
        })
        .join(',')
    )
    .join('\n')
  const blob = new Blob([header + '\n' + body], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${config.value?.slug ?? 'report'}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
