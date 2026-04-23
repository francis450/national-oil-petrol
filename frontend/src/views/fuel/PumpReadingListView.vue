<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Pump Readings</h1>
        <p class="text-gray-400">Recent forecourt readings with live throughput summaries from the custom pump log.</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shrink-0"
      >
        + New Reading
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Today's Readings</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(summary.today.reading_count) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Today's Throughput</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(summary.today.throughput) }} L</p>
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
            <p class="text-sm text-gray-400">Latest pump readings captured per pump and date.</p>
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
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Pump</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Fuel Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Opening</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Closing</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Variance</th>
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
                <td class="px-4 py-3 text-gray-100 font-medium">{{ row.pump_number }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.fuel_type }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatNumber(row.opening_reading) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatNumber(row.closing_reading) }}</td>
                <td class="px-4 py-3 text-blue-300 font-medium">{{ formatNumber(row.variance) }} L</td>
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
              <p class="text-xs uppercase tracking-wider text-gray-500">Selected Pump</p>
              <p class="text-lg font-semibold text-white">{{ selectedReading.pump_number }}</p>
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
                <p class="text-gray-500">Variance</p>
                <p class="text-blue-300">{{ formatNumber(selectedReading.variance) }} L</p>
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
            Pump variance is calculated on the backend as closing minus opening, and duplicate readings for the same pump on the same date are blocked by the controller.
          </div>
        </template>
      </aside>
    </div>

    <SlideOver v-model="showForm" title="New Pump Reading">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Date <span class="text-red-400">*</span></label>
            <input
              v-model="form.dated"
              type="date"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Pump Number <span class="text-red-400">*</span></label>
            <input
              v-model="form.pump_number"
              type="text"
              placeholder="e.g. P1, P2"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Fuel Type <span class="text-red-400">*</span></label>
          <input
            v-model="form.fuel_type"
            type="text"
            placeholder="e.g. Petrol, Diesel"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Opening Reading <span class="text-red-400">*</span></label>
            <input
              v-model.number="form.opening_reading"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Closing Reading <span class="text-red-400">*</span></label>
            <input
              v-model.number="form.closing_reading"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Attendant</label>
            <input
              v-model="form.attendant"
              type="text"
              placeholder="Employee ID (optional)"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Department</label>
            <input
              v-model="form.department"
              type="text"
              placeholder="Department (optional)"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Notes</label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="Optional notes"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm resize-none"
          ></textarea>
        </div>
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
          {{ creating ? 'Saving...' : 'Create Reading' }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { fuelApi, type PumpReadingRow, type PumpReadingSummary } from '@/api/fuel'
import SlideOver from '@/components/common/SlideOver.vue'
import { apiClient } from '@/api/client'

const summary = ref<PumpReadingSummary>({
  count: 0,
  rows: [],
  today: {
    reading_count: 0,
    throughput: 0,
  },
})
const selectedReading = ref<PumpReadingRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
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

const showForm = ref(false)
const creating = ref(false)
const createError = ref('')
const form = reactive({
  dated: '',
  pump_number: '',
  fuel_type: '',
  opening_reading: 0,
  closing_reading: 0,
  attendant: '',
  department: '',
  notes: '',
})

const openCreate = () => {
  form.dated = new Date().toISOString().split('T')[0]
  form.pump_number = ''
  form.fuel_type = ''
  form.opening_reading = 0
  form.closing_reading = 0
  form.attendant = ''
  form.department = ''
  form.notes = ''
  createError.value = ''
  showForm.value = true
}

const saveForm = async () => {
  if (!form.dated || !form.pump_number.trim() || !form.fuel_type.trim() || form.opening_reading == null || form.closing_reading == null) {
    createError.value = 'Date, pump number, fuel type, and both readings are required.'
    return
  }
  creating.value = true
  createError.value = ''
  try {
    const payload: Record<string, any> = {
      dated: form.dated,
      pump_number: form.pump_number.trim(),
      fuel_type: form.fuel_type.trim(),
      opening_reading: form.opening_reading,
      closing_reading: form.closing_reading,
    }
    if (form.attendant.trim()) payload.attendant = form.attendant.trim()
    if (form.department.trim()) payload.department = form.department.trim()
    if (form.notes.trim()) payload.notes = form.notes.trim()

    await apiClient.post('/api/resource/Pump Reading', payload)
    showForm.value = false
    await loadReadings()
  } catch (e: any) {
    createError.value = e?.response?.data?.message || e?.message || 'Failed to save pump reading.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  await loadReadings()
})
</script>
