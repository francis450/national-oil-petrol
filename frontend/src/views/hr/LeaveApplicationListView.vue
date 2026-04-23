<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Leave Applications</h1>
      <p class="text-gray-400">Canonical HRMS leave records for absence planning and review.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Applications</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(leaves.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Open</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(openLeaves.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Approved</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(approvedLeaves.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Departments</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(uniqueDepartments) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Leave Register</h2>
            <p class="text-sm text-gray-400">Recent leave applications pulled directly from HRMS.</p>
          </div>
          <button
            @click="loadLeaves"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading leave applications...</div>

        <div v-else-if="leaves.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No leave applications found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Employee</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Leave Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">From</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">To</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="leave in leaves"
                :key="leave.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedLeave?.name === leave.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedLeave = leave"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ leave.employee_name || leave.employee || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ leave.department || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ leave.leave_type || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(leave.from_date) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(leave.to_date) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(leave.status)">
                    {{ leave.status || '—' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Leave Detail</h2>
          <p class="text-sm text-gray-400">Review one leave request at a time without leaving the HR module.</p>
        </div>

        <div v-if="!selectedLeave" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select a leave application to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Employee</p>
              <p class="text-lg font-semibold text-white">{{ selectedLeave.employee_name || selectedLeave.employee || '—' }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedLeave.department || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Leave Type</p>
                <p class="text-gray-200">{{ selectedLeave.leave_type || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">From Date</p>
                <p class="text-gray-200">{{ formatDate(selectedLeave.from_date) }}</p>
              </div>
              <div>
                <p class="text-gray-500">To Date</p>
                <p class="text-gray-200">{{ formatDate(selectedLeave.to_date) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Status</p>
                <p class="text-gray-200">{{ selectedLeave.status || '—' }}</p>
              </div>
            </div>
          </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { workforceApi, type LeaveApplicationRow } from '@/api/workforce'

const leaves = ref<LeaveApplicationRow[]>([])
const selectedLeave = ref<LeaveApplicationRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const openLeaves = computed(() => leaves.value.filter((leave) => ['Open', 'Pending Approval'].includes(leave.status || '')))
const approvedLeaves = computed(() => leaves.value.filter((leave) => leave.status === 'Approved'))
const uniqueDepartments = computed(() => new Set(leaves.value.map((leave) => leave.department).filter(Boolean)).size)

const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const statusClass = (status?: string) => {
  if (status === 'Approved') return 'border-green-700 bg-green-950 text-green-200'
  if (status === 'Rejected') return 'border-red-700 bg-red-950 text-red-200'
  if (status === 'Open' || status === 'Pending Approval') return 'border-yellow-700 bg-yellow-950 text-yellow-200'
  return 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadLeaves = async () => {
  loading.value = true
  pageError.value = ''

  try {
    leaves.value = await workforceApi.listLeaveApplications()
    if (!selectedLeave.value && leaves.value.length > 0) {
      selectedLeave.value = leaves.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load leave applications.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadLeaves()
})
</script>
