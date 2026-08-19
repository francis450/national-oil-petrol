<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Shift Assignments</h1>
        <p class="text-gray-400">Assign attendants to shifts — Pump Reading's Open/Close flow and the attendant landing page both depend on this.</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shrink-0"
      >
        + New Shift Assignment
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Shifts</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(shifts.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Open</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(openCount) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Closed</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(closedCount) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Total Expected Sales</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(totalExpectedSales) }}</p>
      </div>
    </div>

    <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-white">Shift Register</h2>
          <p class="text-sm text-gray-400">All Shift Assignments, most recent first.</p>
        </div>
        <button
          @click="loadShifts"
          :disabled="loading"
          class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
        >
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>

      <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading shift assignments...</div>

      <div v-else-if="shifts.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
        No shift assignments found yet.
      </div>

      <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
        <table class="w-full text-sm">
          <thead class="bg-gray-950 border-b border-gray-800">
            <tr>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Attendant</th>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Shift Type</th>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Start Date</th>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">End Date</th>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Reconciliation</th>
              <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Expected Sales</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="shift in shifts"
              :key="shift.name"
              class="border-b border-gray-800 hover:bg-gray-900 transition-colors"
            >
              <td class="px-4 py-3 text-gray-100 font-medium">{{ shift.employee_name || shift.employee }}</td>
              <td class="px-4 py-3 text-gray-300">{{ shift.shift_type }}</td>
              <td class="px-4 py-3 text-gray-300">{{ formatDate(shift.start_date) }}</td>
              <td class="px-4 py-3 text-gray-300">{{ formatDate(shift.end_date) }}</td>
              <td class="px-4 py-3">
                <span
                  class="px-2 py-1 rounded-full text-xs font-medium"
                  :class="reconciliationBadgeClass(shift.reconciliation_status)"
                >
                  {{ shift.reconciliation_status || 'Open' }}
                </span>
              </td>
              <td class="px-4 py-3 text-green-300 font-medium">{{ formatCurrency(shift.total_expected_sales) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <SlideOver v-model="showForm" title="New Shift Assignment">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Attendant <span class="text-red-400">*</span></label>
          <select
            v-model="form.employee"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— Select —</option>
            <option v-for="emp in employeeOptions" :key="emp.name" :value="emp.name">{{ emp.label || emp.employee_name }}</option>
          </select>
          <p v-if="!formOptionsLoading && employeeOptions.length === 0" class="text-xs text-yellow-300 mt-1">
            No attendants loaded — try Refresh below, or reload the page.
          </p>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Shift Type <span class="text-red-400">*</span></label>
          <select
            v-model="form.shift_type"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— Select —</option>
            <option v-for="st in shiftTypeOptions" :key="st.name" :value="st.name">{{ st.name }}</option>
          </select>
          <p v-if="!formOptionsLoading && shiftTypeOptions.length === 0" class="text-xs text-yellow-300 mt-1">
            No shift types loaded — try Refresh below, or reload the page.
          </p>
        </div>
        <button
          type="button"
          @click="loadFormOptions"
          :disabled="formOptionsLoading"
          class="text-xs text-gray-400 hover:text-gray-200 underline disabled:opacity-40"
        >
          {{ formOptionsLoading ? 'Refreshing options...' : 'Refresh attendant/shift type options' }}
        </button>
        <p v-if="formOptionsError" class="text-xs text-red-300">{{ formOptionsError }}</p>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Start Date <span class="text-red-400">*</span></label>
            <input
              v-model="form.start_date"
              type="date"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">End Date</label>
            <input
              v-model="form.end_date"
              type="date"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>
        <p class="text-xs text-gray-500">
          Pumps get assigned to this shift automatically as the attendant opens each reading — no need to pre-fill them here.
        </p>
        <div
          v-if="createError"
          class="p-3 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-xs"
        >{{ createError }}</div>
      </div>
      <template #footer>
        <button
          @click="showForm = false"
          class="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="saveForm"
          :disabled="creating"
          class="px-4 py-2 text-sm text-white bg-deepseek-blue rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
        >
          {{ creating ? 'Saving...' : 'Create Shift Assignment' }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { workforceApi, type CompanyRow, type EmployeeRow, type ShiftAssignmentRow, type ShiftTypeRow } from '@/api/workforce'
import SlideOver from '@/components/common/SlideOver.vue'
import { apiClient } from '@/api/client'

const shifts = ref<ShiftAssignmentRow[]>([])
const loading = ref(false)
const pageError = ref('')

const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')

const openCount = computed(() => shifts.value.filter((s) => (s.reconciliation_status || 'Open') === 'Open').length)
const closedCount = computed(() => shifts.value.filter((s) => s.reconciliation_status === 'Closed').length)
const totalExpectedSales = computed(() => shifts.value.reduce((sum, s) => sum + Number(s.total_expected_sales || 0), 0))

const reconciliationBadgeClass = (status?: string) => {
  if (status === 'Closed') return 'bg-bioluminescent-green bg-opacity-20 text-bioluminescent-green'
  if (status === 'Verified') return 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue'
  return 'bg-yellow-500 bg-opacity-20 text-yellow-300'
}

const loadShifts = async () => {
  loading.value = true
  pageError.value = ''
  try {
    shifts.value = await workforceApi.listShiftAssignments()
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load shift assignments.'
  } finally {
    loading.value = false
  }
}

const employeeOptions = ref<EmployeeRow[]>([])
const shiftTypeOptions = ref<ShiftTypeRow[]>([])
const companyOptions = ref<CompanyRow[]>([])
const formOptionsLoading = ref(false)
const formOptionsError = ref('')

const loadFormOptions = async () => {
  formOptionsLoading.value = true
  formOptionsError.value = ''
  const [employees, shiftTypes, companies] = await Promise.allSettled([
    workforceApi.listEmployees(),
    workforceApi.listShiftTypes(),
    workforceApi.listCompanies(),
  ])

  const errors: string[] = []

  if (employees.status === 'fulfilled') {
    employeeOptions.value = employees.value.filter((emp) => emp.status === 'Active' || !emp.status)
  } else {
    errors.push(`Attendants: ${employees.reason?.response?.data?.message || employees.reason?.message || 'failed to load'}`)
  }

  if (shiftTypes.status === 'fulfilled') {
    shiftTypeOptions.value = shiftTypes.value
  } else {
    errors.push(`Shift types: ${shiftTypes.reason?.response?.data?.message || shiftTypes.reason?.message || 'failed to load'}`)
  }

  if (companies.status === 'fulfilled') {
    companyOptions.value = companies.value
  } else {
    errors.push(`Company: ${companies.reason?.response?.data?.message || companies.reason?.message || 'failed to load'}`)
  }

  formOptionsError.value = errors.join(' | ')
  formOptionsLoading.value = false
}

const showForm = ref(false)
const creating = ref(false)
const createError = ref('')
const form = reactive({
  employee: '',
  shift_type: '',
  start_date: '',
  end_date: '',
})

const openCreate = () => {
  form.employee = ''
  form.shift_type = ''
  form.start_date = new Date().toISOString().split('T')[0]
  form.end_date = new Date().toISOString().split('T')[0]
  createError.value = ''
  showForm.value = true
}

const saveForm = async () => {
  if (!form.employee || !form.shift_type || !form.start_date) {
    createError.value = 'Attendant, shift type, and start date are required.'
    return
  }
  creating.value = true
  createError.value = ''
  try {
    const payload: Record<string, any> = {
      employee: form.employee,
      shift_type: form.shift_type,
      start_date: form.start_date,
      company: companyOptions.value[0]?.name,
    }
    if (form.end_date) payload.end_date = form.end_date

    await apiClient.post('/api/resource/Shift Assignment', payload)
    showForm.value = false
    await loadShifts()
  } catch (e: any) {
    createError.value = e?.response?.data?.message || e?.message || 'Failed to create shift assignment.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadShifts(), loadFormOptions()])
})
</script>
