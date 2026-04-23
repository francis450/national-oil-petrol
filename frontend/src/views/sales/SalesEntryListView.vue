<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Sales Entries</h1>
        <p class="text-gray-400">Operational sales capture with ERPNext invoice bridge actions.</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shrink-0"
      >
        + New Entry
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.5fr)_minmax(340px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Operational Sales</h2>
            <p class="text-sm text-gray-400">Select a sales entry to preview its ERPNext invoice mapping.</p>
          </div>
          <button
            @click="loadSalesEntries"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading sales entries...</div>

        <div v-else-if="salesEntries.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No sales entry records found.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Method</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-center text-gray-400 font-medium text-xs uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in salesEntries"
                :key="row.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedEntry?.name === row.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
              >
                <td class="px-4 py-3 text-gray-200 font-medium">{{ formatDate(row.dated) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.department }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.sale_type }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.payment_method || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(row.amount) }}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-center gap-2">
                    <button
                      @click="selectEntry(row)"
                      class="px-3 py-1.5 text-xs rounded bg-blue-900 text-blue-200 hover:bg-blue-800 transition-colors"
                    >
                      Preview
                    </button>
                    <button
                      @click="createInvoice(row)"
                      :disabled="creatingInvoiceFor === row.name"
                      class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
                    >
                      {{ creatingInvoiceFor === row.name ? 'Creating...' : 'Create Invoice' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">ERPNext Invoice Preview</h2>
          <p class="text-sm text-gray-400">See how each operational sale maps into ERPNext.</p>
        </div>

        <div v-if="!selectedEntry" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select a sales entry to preview its ERPNext invoice mapping.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-2">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-xs uppercase tracking-wider text-gray-500">Selected Record</p>
                <p class="text-white font-semibold">{{ selectedEntry.name }}</p>
              </div>
              <button
                @click="loadPreview(selectedEntry.name)"
                :disabled="previewLoading"
                class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
              >
                {{ previewLoading ? 'Loading...' : 'Reload Preview' }}
              </button>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedEntry.department }}</p>
              </div>
              <div>
                <p class="text-gray-500">Sale Type</p>
                <p class="text-gray-200">{{ selectedEntry.sale_type }}</p>
              </div>
              <div>
                <p class="text-gray-500">Payment Method</p>
                <p class="text-gray-200">{{ selectedEntry.payment_method || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Customer</p>
                <p class="text-gray-200">{{ selectedEntry.customer || '—' }}</p>
              </div>
            </div>
          </div>

          <div v-if="previewError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
            {{ previewError }}
          </div>

          <div v-if="previewLoading" class="text-sm text-gray-400 py-8 text-center">Loading mapping preview...</div>

          <div v-else-if="preview?.targets?.length" class="space-y-4">
            <article
              v-for="target in preview.targets"
              :key="target.target_doctype"
              class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-3"
            >
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-white">{{ target.target_doctype }}</p>
                  <p class="text-xs text-gray-500">{{ target.recommended ? 'Recommended target' : 'Optional target' }}</p>
                </div>
                <button
                  v-if="target.target_doctype === 'Sales Invoice'"
                  @click="createInvoice(selectedEntry)"
                  :disabled="creatingInvoiceFor === selectedEntry.name"
                  class="px-3 py-1.5 text-xs rounded bg-deepseek-blue text-white hover:bg-blue-700 transition-colors"
                >
                  {{ creatingInvoiceFor === selectedEntry.name ? 'Creating...' : 'Create Sales Invoice' }}
                </button>
              </div>

              <div v-if="target.unresolved_dependencies.length" class="p-3 rounded border border-yellow-800 bg-yellow-500 bg-opacity-10">
                <p class="text-xs uppercase tracking-wider text-yellow-400 mb-2">Unresolved Dependencies</p>
                <ul class="space-y-1 text-sm text-yellow-200">
                  <li v-for="issue in target.unresolved_dependencies" :key="issue">{{ issue }}</li>
                </ul>
              </div>

              <pre class="text-xs text-gray-300 bg-black rounded p-3 overflow-x-auto whitespace-pre-wrap">{{ formatPayload(target.payload) }}</pre>
            </article>
          </div>
        </template>

        <div v-if="createdInvoices.length" class="pt-2 border-t border-gray-800 space-y-2">
          <p class="text-xs uppercase tracking-wider text-gray-500">Created ERPNext Drafts</p>
          <div
            v-for="invoice in createdInvoices"
            :key="invoice.name"
            class="rounded border border-green-800 bg-green-900 bg-opacity-10 px-3 py-2 text-sm text-green-200"
          >
            Sales Invoice: {{ invoice.name }}
          </div>
        </div>
      </aside>
    </div>

    <SlideOver v-model="showForm" title="New Sales Entry">
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
            <label class="block text-sm text-gray-400 mb-1">Department <span class="text-red-400">*</span></label>
            <input
              v-model="form.department"
              type="text"
              placeholder="e.g. Forecourt"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Sale Type <span class="text-red-400">*</span></label>
          <select
            v-model="form.sale_type"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— Select type —</option>
            <option>Wet Stock</option>
            <option>Other Sale</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Amount (KSh) <span class="text-red-400">*</span></label>
          <input
            v-model.number="form.amount"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Payment Method</label>
          <select
            v-model="form.payment_method"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— Select method —</option>
            <option>Cash</option>
            <option>M-Pesa</option>
            <option>Cheque</option>
            <option>Bank Transfer</option>
            <option>Credit</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Customer</label>
          <input
            v-model="form.customer"
            type="text"
            placeholder="Customer ID (optional)"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
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
          {{ creating ? 'Saving...' : 'Create Entry' }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  operationsBridgeApi,
  type BridgePreview,
  type SalesEntryRow,
} from '@/api/operationsBridge'
import SlideOver from '@/components/common/SlideOver.vue'
import { apiClient } from '@/api/client'

const salesEntries = ref<SalesEntryRow[]>([])
const loading = ref(false)
const pageError = ref('')

const selectedEntry = ref<SalesEntryRow | null>(null)
const preview = ref<BridgePreview | null>(null)
const previewLoading = ref(false)
const previewError = ref('')
const creatingInvoiceFor = ref('')
const createdInvoices = ref<Array<{ name: string }>>([])

const formatCurrency = (value: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value: string) => new Date(value).toLocaleDateString('en-KE')
const formatPayload = (payload: Record<string, any>) => JSON.stringify(payload, null, 2)

const loadSalesEntries = async () => {
  loading.value = true
  pageError.value = ''

  try {
    salesEntries.value = await operationsBridgeApi.listSalesEntries()
    if (!selectedEntry.value && salesEntries.value.length > 0) {
      await selectEntry(salesEntries.value[0])
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load sales entries.'
  } finally {
    loading.value = false
  }
}

const loadPreview = async (name: string) => {
  previewLoading.value = true
  previewError.value = ''

  try {
    preview.value = await operationsBridgeApi.previewSalesEntryMapping(name)
  } catch (error: any) {
    previewError.value = error?.response?.data?.message || error?.message || 'Failed to load ERPNext invoice preview.'
  } finally {
    previewLoading.value = false
  }
}

const selectEntry = async (row: SalesEntryRow) => {
  selectedEntry.value = row
  await loadPreview(row.name)
}

const createInvoice = async (row: SalesEntryRow) => {
  creatingInvoiceFor.value = row.name
  previewError.value = ''

  try {
    const result = await operationsBridgeApi.createSalesEntryTarget(row.name, 'Sales Invoice')
    createdInvoices.value = [
      { name: result.name },
      ...createdInvoices.value.filter((entry) => entry.name !== result.name),
    ]
    if (selectedEntry.value?.name === row.name) {
      await loadPreview(row.name)
    }
  } catch (error: any) {
    previewError.value = error?.response?.data?.message || error?.message || 'Failed to create Sales Invoice.'
  } finally {
    creatingInvoiceFor.value = ''
  }
}

const showForm = ref(false)
const creating = ref(false)
const createError = ref('')
const form = reactive({
  dated: '',
  department: '',
  sale_type: '',
  amount: 0,
  payment_method: '',
  customer: '',
  notes: '',
})

const openCreate = () => {
  form.dated = new Date().toISOString().split('T')[0]
  form.department = ''
  form.sale_type = ''
  form.amount = 0
  form.payment_method = ''
  form.customer = ''
  form.notes = ''
  createError.value = ''
  showForm.value = true
}

const saveForm = async () => {
  if (!form.dated || !form.department.trim() || !form.sale_type || !form.amount) {
    createError.value = 'Date, department, sale type, and amount are required.'
    return
  }
  creating.value = true
  createError.value = ''
  try {
    const payload: Record<string, any> = {
      dated: form.dated,
      department: form.department.trim(),
      sale_type: form.sale_type,
      amount: form.amount,
    }
    if (form.payment_method) payload.payment_method = form.payment_method
    if (form.customer.trim()) payload.customer = form.customer.trim()
    if (form.notes.trim()) payload.notes = form.notes.trim()

    const resp = await apiClient.post('/api/resource/Sales Entry', payload)
    const created = resp.data.data as SalesEntryRow
    showForm.value = false
    await loadSalesEntries()
    if (created?.name) {
      const found = salesEntries.value.find((r) => r.name === created.name)
      if (found) await selectEntry(found)
    }
  } catch (e: any) {
    createError.value = e?.response?.data?.message || e?.message || 'Failed to save sales entry.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  await loadSalesEntries()
})
</script>
