<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Pump Readings</h1>
        <p class="text-gray-400">Shift meter readings per nozzle, with expected sales computed automatically.</p>
      </div>
      <div class="flex gap-2 shrink-0">
        <button
          @click="openOpenShiftForm"
          class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          + Open Reading
        </button>
        <button
          @click="openCloseShiftForm"
          :disabled="!shiftContext.open_readings.length"
          class="px-4 py-2 bg-gray-800 border border-gray-700 text-white rounded-lg hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm font-medium"
        >
          Close Reading
        </button>
      </div>
    </div>

    <div
      v-if="!shiftContext.shift && !shiftContextLoading"
      class="p-4 rounded-lg border border-yellow-800 bg-yellow-900 bg-opacity-20 text-yellow-200 text-sm"
    >
      No active Shift Assignment found for your account today — ask your manager to assign you a shift before opening a reading.
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Today's Readings</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(summary.today.reading_count) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Today's Throughput</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(summary.today.throughput) }} L</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Today's Expected Sales</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(summary.today.expected_sales) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Recent Log Size</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(summary.count) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Recent Readings</h2>
            <p class="text-sm text-gray-400">Latest readings captured per nozzle, shift, and date.</p>
          </div>
          <button
            @click="loadReadings"
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
          Loading pump readings...
        </div>

        <div
          v-else-if="summary.rows.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No pump readings found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Shift</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Nozzle</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Fuel Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Litres Sold</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Expected Sales</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in summary.rows"
                :key="row.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedReading?.name === row.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedReading = row"
              >
                <td class="px-4 py-3 text-gray-200">{{ formatDate(row.dated) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.shift }}</td>
                <td class="px-4 py-3 text-gray-100 font-medium">Nozzle {{ row.nozzle_no }} (P{{ row.pump_no }})</td>
                <td class="px-4 py-3 text-gray-300">{{ row.fuel_type }}</td>
                <td class="px-4 py-3 text-blue-300 font-medium">{{ formatNumber(row.variance) }} L</td>
                <td class="px-4 py-3 text-green-300 font-medium">{{ formatCurrency(row.expected_sales_amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Reading Detail</h2>
          <p class="text-sm text-gray-400">Inspect the latest throughput and who captured the reading.</p>
        </div>

        <div
          v-if="!selectedReading"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select a pump reading to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Nozzle {{ selectedReading.nozzle_no }}</p>
              <p class="text-lg font-semibold text-white">Pump {{ selectedReading.pump_no }} &middot; {{ selectedReading.shift }} shift</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Date</p>
                <p class="text-gray-200">{{ formatDate(selectedReading.dated) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Fuel Type</p>
                <p class="text-gray-200">{{ selectedReading.fuel_type }}</p>
              </div>
              <div>
                <p class="text-gray-500">Opening</p>
                <p class="text-gray-200">{{ formatNumber(selectedReading.opening_reading) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Closing</p>
                <p class="text-gray-200">{{ formatNumber(selectedReading.closing_reading) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Litres Sold</p>
                <p class="text-blue-300">{{ formatNumber(selectedReading.variance) }} L</p>
              </div>
              <div>
                <p class="text-gray-500">Unit Price</p>
                <p class="text-gray-200">{{ formatCurrency(selectedReading.unit_price) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Expected Sales</p>
                <p class="text-green-300 font-semibold">{{ formatCurrency(selectedReading.expected_sales_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Attendant</p>
                <p class="text-gray-200">{{ selectedReading.attendant || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedReading.department || '—' }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-gray-800 bg-black p-3 text-sm text-gray-300">
            Expected sales = litres sold &times; unit price, for management reconciliation against actual till/M-Pesa
            collections. No Sales Invoice is created automatically in this phase. Duplicate readings for the same
            nozzle, date, and shift are blocked by the controller.
          </div>
        </template>
      </aside>
    </div>

    <SlideOver v-model="showOpenForm" title="Open Shift Reading">
      <div class="space-y-4">
        <div class="rounded-lg border border-gray-800 bg-gray-950 p-3 text-sm text-gray-300">
          <p>Shift <span class="text-white font-medium">{{ shiftContext.shift?.name || '—' }}</span></p>
          <p class="text-gray-500 text-xs mt-1">Attendant is auto-detected from your account — no manual selection needed.</p>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Nozzle No <span class="text-red-400">*</span></label>
          <select
            v-model.number="openForm.nozzle_no"
            @change="onNozzleChange"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option :value="0">— Select —</option>
            <option v-for="n in 13" :key="n" :value="n">Nozzle {{ n }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Pump / Fuel Type</label>
          <input
            :value="nozzleDefaults ? `Pump ${nozzleDefaults.pump_no} — ${nozzleDefaults.fuel_type || nozzleDefaults.item}` : ''"
            type="text"
            readonly
            placeholder="Auto-filled from nozzle"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 text-sm cursor-not-allowed"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Opening Reading <span class="text-red-400">*</span></label>
          <input
            v-model.number="openForm.opening_reading"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div
          v-if="openError"
          class="p-3 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-xs"
        >{{ openError }}</div>
      </div>
      <template #footer>
        <button
          @click="showOpenForm = false"
          class="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="saveOpenForm"
          :disabled="opening"
          class="px-4 py-2 text-sm text-white bg-deepseek-blue rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
        >
          {{ opening ? 'Saving...' : 'Open Reading' }}
        </button>
      </template>
    </SlideOver>

    <SlideOver v-model="showCloseForm" title="Close Shift Reading">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Open Reading <span class="text-red-400">*</span></label>
          <select
            v-model="closeForm.name"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— Select —</option>
            <option v-for="reading in shiftContext.open_readings" :key="reading.name" :value="reading.name">
              Nozzle {{ reading.nozzle_no }} ({{ reading.pump_number }}) — opened at {{ formatNumber(reading.opening_reading) }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Closing Reading <span class="text-red-400">*</span></label>
          <input
            v-model.number="closeForm.closing_reading"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Unit Price (KSh, optional — defaults from Fuel Price)</label>
          <input
            v-model.number="closeForm.unit_price"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div
          v-if="closeError"
          class="p-3 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-xs"
        >{{ closeError }}</div>
      </div>
      <template #footer>
        <button
          @click="showCloseForm = false"
          class="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="saveCloseForm"
          :disabled="closing"
          class="px-4 py-2 text-sm text-white bg-deepseek-blue rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
        >
          {{ closing ? 'Submitting...' : 'Close Reading' }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  fuelApi,
  type MyShiftContext,
  type NozzleDefaults,
  type PumpReadingRow,
  type PumpReadingSummary,
} from '@/api/fuel'
import SlideOver from '@/components/common/SlideOver.vue'

const summary = ref<PumpReadingSummary>({
  count: 0,
  rows: [],
  today: {
    reading_count: 0,
    throughput: 0,
    expected_sales: 0,
  },
})
const selectedReading = ref<PumpReadingRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')

const loadReadings = async () => {
  loading.value = true
  pageError.value = ''

  try {
    summary.value = await fuelApi.getRecentPumpReadings()
    if (!selectedReading.value && summary.value.rows.length > 0) {
      selectedReading.value = summary.value.rows[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load pump readings.'
  } finally {
    loading.value = false
  }
}

const shiftContext = ref<MyShiftContext>({ employee: null, shift: null, open_readings: [] })
const shiftContextLoading = ref(false)
const loadShiftContext = async () => {
  shiftContextLoading.value = true
  try {
    shiftContext.value = await fuelApi.getMyShiftContext()
  } catch (error) {
    // Non-fatal — the Open/Close buttons just stay disabled without a detected shift.
  } finally {
    shiftContextLoading.value = false
  }
}

const nozzleDefaults = ref<NozzleDefaults | null>(null)
const onNozzleChange = async () => {
  nozzleDefaults.value = null
  if (!openForm.nozzle_no) return
  try {
    nozzleDefaults.value = await fuelApi.getNozzleDefaults(openForm.nozzle_no)
  } catch (error) {
    // Non-fatal — server-side validation still enforces the mapping on save.
  }
}

const showOpenForm = ref(false)
const opening = ref(false)
const openError = ref('')
const openForm = reactive({
  nozzle_no: 0,
  opening_reading: 0,
})

const openOpenShiftForm = () => {
  openForm.nozzle_no = 0
  openForm.opening_reading = 0
  nozzleDefaults.value = null
  openError.value = ''
  showOpenForm.value = true
}

const saveOpenForm = async () => {
  if (!shiftContext.value.shift) {
    openError.value = 'No active shift detected for your account.'
    return
  }
  if (!openForm.nozzle_no || openForm.opening_reading == null) {
    openError.value = 'Nozzle and opening reading are required.'
    return
  }
  opening.value = true
  openError.value = ''
  try {
    await fuelApi.openPumpReading(shiftContext.value.shift.name, openForm.nozzle_no, openForm.opening_reading)
    showOpenForm.value = false
    await Promise.all([loadReadings(), loadShiftContext()])
  } catch (e: any) {
    openError.value = e?.response?.data?.message || e?.message || 'Failed to open pump reading.'
  } finally {
    opening.value = false
  }
}

const showCloseForm = ref(false)
const closing = ref(false)
const closeError = ref('')
const closeForm = reactive({
  name: '',
  closing_reading: 0,
  unit_price: 0,
})

const openCloseShiftForm = () => {
  closeForm.name = shiftContext.value.open_readings[0]?.name || ''
  closeForm.closing_reading = 0
  closeForm.unit_price = 0
  closeError.value = ''
  showCloseForm.value = true
}

const saveCloseForm = async () => {
  if (!closeForm.name || closeForm.closing_reading == null) {
    closeError.value = 'Select an open reading and enter the closing value.'
    return
  }
  closing.value = true
  closeError.value = ''
  try {
    await fuelApi.closePumpReading(closeForm.name, closeForm.closing_reading, closeForm.unit_price || undefined)
    showCloseForm.value = false
    await Promise.all([loadReadings(), loadShiftContext()])
  } catch (e: any) {
    closeError.value = e?.response?.data?.message || e?.message || 'Failed to close pump reading.'
  } finally {
    closing.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadReadings(), loadShiftContext()])
})
</script>
