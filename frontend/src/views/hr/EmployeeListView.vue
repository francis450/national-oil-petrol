<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Employees</h1>
      <p class="text-gray-400">Canonical ERPNext/HRMS employee records for the station workforce.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Employees</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(employees.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Active</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(activeEmployees.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Departments</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(uniqueDepartments) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Companies</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(uniqueCompanies) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Workforce Directory</h2>
            <p class="text-sm text-gray-400">Employees come directly from canonical HRMS master data.</p>
          </div>
          <button
            @click="loadEmployees"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading employees...</div>

        <div v-else-if="employees.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No employees found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Employee</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Designation</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Company</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="employee in employees"
                :key="employee.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedEmployee?.name === employee.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedEmployee = employee"
              >
                <td class="px-4 py-3">
                  <div class="text-gray-100 font-medium">{{ employee.employee_name || employee.name }}</div>
                  <div class="text-xs text-gray-500">{{ employee.name }}</div>
                </td>
                <td class="px-4 py-3 text-gray-300">{{ employee.department || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ employee.designation || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ employee.company || '—' }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(employee.status)">
                    {{ employee.status || '—' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Employee Detail</h2>
          <p class="text-sm text-gray-400">Review one employee record at a time from the canonical workforce master.</p>
        </div>

        <div v-if="!selectedEmployee" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select an employee to inspect the record.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Employee</p>
              <p class="text-lg font-semibold text-white">{{ selectedEmployee.employee_name || selectedEmployee.name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Employee ID</p>
                <p class="text-gray-200">{{ selectedEmployee.name }}</p>
              </div>
              <div>
                <p class="text-gray-500">Status</p>
                <p class="text-gray-200">{{ selectedEmployee.status || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedEmployee.department || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Designation</p>
                <p class="text-gray-200">{{ selectedEmployee.designation || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Company</p>
                <p class="text-gray-200">{{ selectedEmployee.company || '—' }}</p>
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
import { workforceApi, type EmployeeRow } from '@/api/workforce'

const employees = ref<EmployeeRow[]>([])
const selectedEmployee = ref<EmployeeRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const activeEmployees = computed(() => employees.value.filter((employee) => employee.status === 'Active'))
const uniqueDepartments = computed(() => new Set(employees.value.map((employee) => employee.department).filter(Boolean)).size)
const uniqueCompanies = computed(() => new Set(employees.value.map((employee) => employee.company).filter(Boolean)).size)

const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const statusClass = (status?: string) => {
  if (status === 'Active') return 'border-green-700 bg-green-950 text-green-200'
  if (status === 'Inactive' || status === 'Left') return 'border-red-700 bg-red-950 text-red-200'
  return 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadEmployees = async () => {
  loading.value = true
  pageError.value = ''

  try {
    employees.value = await workforceApi.listEmployees()
    if (!selectedEmployee.value && employees.value.length > 0) {
      selectedEmployee.value = employees.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load employees.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadEmployees()
})
</script>
