<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Attendance</h1>
      <p class="text-gray-400">Canonical attendance records from HRMS for daily workforce visibility.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Records</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(attendance.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Present</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(presentCount) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Absent</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(absentCount) }}</p>
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
            <h2 class="text-xl font-bold text-white">Attendance Register</h2>
            <p class="text-sm text-gray-400">Recent attendance records across departments.</p>
          </div>
          <button
            @click="loadAttendance"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading attendance...</div>

        <div v-else-if="attendance.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No attendance records found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Employee</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Company</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in attendance"
                :key="row.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedAttendance?.name === row.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedAttendance = row"
              >
                <td class="px-4 py-3 text-gray-200">{{ formatDate(row.attendance_date) }}</td>
                <td class="px-4 py-3 text-gray-100 font-medium">{{ row.employee_name || row.employee || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.department || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.company || '—' }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(row.status)">
                    {{ row.status || '—' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Attendance Detail</h2>
          <p class="text-sm text-gray-400">Inspect individual attendance records without leaving the module.</p>
        </div>

        <div v-if="!selectedAttendance" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select an attendance record to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Employee</p>
              <p class="text-lg font-semibold text-white">{{ selectedAttendance.employee_name || selectedAttendance.employee || '—' }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Attendance Date</p>
                <p class="text-gray-200">{{ formatDate(selectedAttendance.attendance_date) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Status</p>
                <p class="text-gray-200">{{ selectedAttendance.status || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedAttendance.department || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Company</p>
                <p class="text-gray-200">{{ selectedAttendance.company || '—' }}</p>
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
import { workforceApi, type AttendanceRow } from '@/api/workforce'

const attendance = ref<AttendanceRow[]>([])
const selectedAttendance = ref<AttendanceRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const presentCount = computed(() => attendance.value.filter((row) => row.status === 'Present').length)
const absentCount = computed(() => attendance.value.filter((row) => row.status && row.status !== 'Present').length)
const uniqueDepartments = computed(() => new Set(attendance.value.map((row) => row.department).filter(Boolean)).size)

const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const statusClass = (status?: string) => {
  if (status === 'Present') return 'border-green-700 bg-green-950 text-green-200'
  if (status === 'Absent') return 'border-red-700 bg-red-950 text-red-200'
  if (status === 'On Leave') return 'border-yellow-700 bg-yellow-950 text-yellow-200'
  return 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadAttendance = async () => {
  loading.value = true
  pageError.value = ''

  try {
    attendance.value = await workforceApi.listAttendance()
    if (!selectedAttendance.value && attendance.value.length > 0) {
      selectedAttendance.value = attendance.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load attendance.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadAttendance()
})
</script>
