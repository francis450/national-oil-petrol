<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Department Sales Targets</h1>
      <p class="text-gray-400">Live departmental targets from the custom target doctype, aligned to submitted sales entries.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Tracked Targets</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(targets.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Combined Target</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(totalTarget) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Combined Hit</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(totalHit) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Net Deviation</p>
        <p class="text-3xl font-bold mt-2" :class="totalDeviation >= 0 ? 'text-green-300' : 'text-red-300'">
          {{ formatCurrency(totalDeviation) }}
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Target Register</h2>
            <p class="text-sm text-gray-400">Targets are recalculated against submitted `Sales Entry` amounts per department and period.</p>
          </div>
          <button
            @click="loadTargets"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div
          v-if="loading"
          class="text-sm text-gray-400 py-8 text-center"
        >
          Loading department sales targets...
        </div>

        <div
          v-else-if="targets.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No department sales targets found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Period</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Target</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Hit</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Deviation</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Variance</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="target in targets"
                :key="target.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedTarget?.name === target.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedTarget = target"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ target.department }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatPeriod(target) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(target.target_amount) }}</td>
                <td class="px-4 py-3 text-white">{{ formatCurrency(target.hit_amount) }}</td>
                <td class="px-4 py-3" :class="target.deviation >= 0 ? 'text-green-300' : 'text-red-300'">
                  {{ formatCurrency(target.deviation) }}
                </td>
                <td class="px-4 py-3" :class="target.deviation >= 0 ? 'text-green-300' : 'text-red-300'">
                  {{ formatPercent(target.variance_percent) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Target Detail</h2>
          <p class="text-sm text-gray-400">Review one department target at a time and see how close the team is to plan.</p>
        </div>

        <div
          v-if="!selectedTarget"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select a target row to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Department</p>
              <p class="text-lg font-semibold text-white">{{ selectedTarget.department }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Period Type</p>
                <p class="text-gray-200">{{ selectedTarget.period_type }}</p>
              </div>
              <div>
                <p class="text-gray-500">Period Window</p>
                <p class="text-gray-200">{{ formatPeriod(selectedTarget) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Target Amount</p>
                <p class="text-gray-200">{{ formatCurrency(selectedTarget.target_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Actual Hit</p>
                <p class="text-gray-200">{{ formatCurrency(selectedTarget.hit_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Deviation</p>
                <p :class="selectedTarget.deviation >= 0 ? 'text-green-300' : 'text-red-300'">
                  {{ formatCurrency(selectedTarget.deviation) }}
                </p>
              </div>
              <div>
                <p class="text-gray-500">Variance %</p>
                <p :class="selectedTarget.deviation >= 0 ? 'text-green-300' : 'text-red-300'">
                  {{ formatPercent(selectedTarget.variance_percent) }}
                </p>
              </div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-400">Progress to Target</span>
                <span class="text-white font-medium">{{ progressPercent(selectedTarget) }}</span>
              </div>
              <div class="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all"
                  :class="selectedTarget.deviation >= 0 ? 'bg-bioluminescent-green' : 'bg-alert-magenta'"
                  :style="{ width: progressWidth(selectedTarget) }"
                ></div>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-gray-800 bg-black p-3 text-sm text-gray-300">
            Targets are recalculated from submitted sales entries in the selected department and period, so this view stays aligned with operational sales capture.
          </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { salesApi, type DepartmentSalesTargetRow } from '@/api/sales'

const targets = ref<DepartmentSalesTargetRow[]>([])
const selectedTarget = ref<DepartmentSalesTargetRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const totalTarget = computed(() =>
  targets.value.reduce((sum, row) => sum + Number(row.target_amount || 0), 0),
)

const totalHit = computed(() =>
  targets.value.reduce((sum, row) => sum + Number(row.hit_amount || 0), 0),
)

const totalDeviation = computed(() => totalHit.value - totalTarget.value)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
const formatPercent = (value?: number) => `${Number(value || 0).toFixed(1)}%`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')

const formatPeriod = (row: DepartmentSalesTargetRow) => {
  const start = formatDate(row.period_start)
  const end = row.period_end ? formatDate(row.period_end) : null
  return end ? `${row.period_type}: ${start} to ${end}` : `${row.period_type}: ${start}`
}

const progressWidth = (row: DepartmentSalesTargetRow) => {
  const percent = row.target_amount > 0 ? (Number(row.hit_amount || 0) / Number(row.target_amount || 0)) * 100 : 0
  return `${Math.min(Math.max(percent, 0), 100)}%`
}

const progressPercent = (row: DepartmentSalesTargetRow) => {
  const percent = row.target_amount > 0 ? (Number(row.hit_amount || 0) / Number(row.target_amount || 0)) * 100 : 0
  return `${percent.toFixed(1)}%`
}

const loadTargets = async () => {
  loading.value = true
  pageError.value = ''

  try {
    targets.value = await salesApi.listDepartmentSalesTargets()
    if (!selectedTarget.value && targets.value.length > 0) {
      selectedTarget.value = targets.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load department sales targets.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadTargets()
})
</script>
