<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Supplier Credits</h1>
        <p class="text-gray-400">Outstanding amounts owed to suppliers from fuel purchases and inventory.</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shrink-0"
      >
        + New Credit
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">All Credits</h2>
            <p class="text-sm text-gray-400">{{ rows.length }} record(s)</p>
          </div>
          <button
            @click="load"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading supplier credits...</div>

        <div
          v-else-if="rows.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No supplier credit records found. Use "New Credit" to create one.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">ID</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Total</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Balance</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.name"
                @click="selected = row"
                class="border-b border-gray-800 cursor-pointer transition-colors"
                :class="selected?.name === row.name ? 'bg-gray-800' : 'hover:bg-gray-900/60'"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ row.name }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.supplier }}</td>
                <td class="px-4 py-3 text-gray-300">{{ fmtDate(row.dated) }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full border px-2.5 py-0.5 text-xs"
                    :class="statusClass(row)"
                  >{{ statusLabel(row) }}</span>
                </td>
                <td class="px-4 py-3 text-gray-300">{{ fmtCurrency(row.total_amount) }}</td>
                <td
                  class="px-4 py-3 font-medium"
                  :class="row.balance > 0 ? 'text-orange-300' : 'text-green-300'"
                >{{ fmtCurrency(row.balance) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <h2 class="text-xl font-bold text-white">Detail</h2>

        <div
          v-if="!selected"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select a record to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-3">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Supplier Credit</p>
              <p class="text-lg font-semibold text-white">{{ selected.name }}</p>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Supplier</p>
                <p class="text-gray-200">{{ selected.supplier }}</p>
              </div>
              <div>
                <p class="text-gray-500">Date</p>
                <p class="text-gray-200">{{ fmtDate(selected.dated) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Total Amount</p>
                <p class="text-gray-200">{{ fmtCurrency(selected.total_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Paid</p>
                <p class="text-gray-200">{{ fmtCurrency(selected.amount_paid) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Balance</p>
                <p :class="selected.balance > 0 ? 'text-orange-300 font-medium' : 'text-green-300'">
                  {{ fmtCurrency(selected.balance) }}
                </p>
              </div>
              <div>
                <p class="text-gray-500">Status</p>
                <span
                  class="inline-flex rounded-full border px-2.5 py-0.5 text-xs"
                  :class="statusClass(selected)"
                >{{ statusLabel(selected) }}</span>
              </div>
              <div v-if="selected.source_document_type">
                <p class="text-gray-500">Source Type</p>
                <p class="text-gray-200">{{ selected.source_document_type }}</p>
              </div>
              <div v-if="selected.source_document">
                <p class="text-gray-500">Source Doc</p>
                <p class="text-gray-200">{{ selected.source_document }}</p>
              </div>
            </div>
          </div>

          <div
            v-if="actionError"
            class="p-3 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-xs"
          >{{ actionError }}</div>

          <div class="flex flex-col gap-2">
            <button
              v-if="selected.docstatus === 0"
              @click="openEdit(selected)"
              class="w-full px-4 py-2 rounded-lg border border-gray-700 bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors text-sm"
            >
              Edit Draft
            </button>
            <button
              v-if="selected.docstatus === 0"
              @click="submitDoc(selected)"
              :disabled="actioning"
              class="w-full px-4 py-2 rounded-lg bg-deepseek-blue text-white hover:bg-blue-700 disabled:opacity-40 transition-colors text-sm"
            >
              {{ actioning ? 'Submitting...' : 'Submit' }}
            </button>
            <button
              v-if="selected.docstatus === 1"
              @click="cancelDoc(selected)"
              :disabled="actioning"
              class="w-full px-4 py-2 rounded-lg border border-red-800 bg-red-900/20 text-red-300 hover:bg-red-900/40 disabled:opacity-40 transition-colors text-sm"
            >
              {{ actioning ? 'Cancelling...' : 'Cancel Document' }}
            </button>
          </div>
        </template>
      </aside>
    </div>

    <SlideOver v-model="showForm" :title="editTarget ? 'Edit Supplier Credit' : 'New Supplier Credit'">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Supplier <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.supplier"
            type="text"
            placeholder="Supplier name or ID"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Date <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.dated"
            type="date"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Total Amount (KSh) <span class="text-red-400">*</span>
          </label>
          <input
            v-model.number="form.total_amount"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Source Document Type</label>
          <select
            v-model="form.source_document_type"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          >
            <option value="">— None —</option>
            <option>Fuel Purchase</option>
            <option>Inventory Receipt</option>
          </select>
        </div>
        <div v-if="form.source_document_type">
          <label class="block text-sm text-gray-400 mb-1">Source Document</label>
          <input
            v-model="form.source_document"
            type="text"
            placeholder="e.g. NOF-PUR-2026-0001"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div
          v-if="formError"
          class="p-3 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-xs"
        >{{ formError }}</div>
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
          :disabled="saving"
          class="px-4 py-2 text-sm text-white bg-deepseek-blue rounded-lg hover:bg-blue-700 disabled:opacity-40 transition-colors"
        >
          {{ saving ? 'Saving...' : (editTarget ? 'Update' : 'Create') }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import SlideOver from '@/components/common/SlideOver.vue'
import { frappeDB, apiClient } from '@/api/client'

interface SupplierCreditRow {
  name: string
  supplier: string
  dated: string
  status: string
  total_amount: number
  amount_paid: number
  balance: number
  source_document_type: string
  source_document: string
  docstatus: number
}

const rows = ref<SupplierCreditRow[]>([])
const selected = ref<SupplierCreditRow | null>(null)
const loading = ref(false)
const pageError = ref('')
const actioning = ref(false)
const actionError = ref('')

const showForm = ref(false)
const editTarget = ref<SupplierCreditRow | null>(null)
const saving = ref(false)
const formError = ref('')
const form = reactive({
  supplier: '',
  dated: '',
  total_amount: 0,
  source_document_type: '',
  source_document: '',
})

const today = () => new Date().toISOString().split('T')[0]
const fmtCurrency = (v?: number) => `KSh ${Number(v || 0).toLocaleString()}`
const fmtDate = (v?: string) => (v ? new Date(v).toLocaleDateString('en-KE') : '—')

const statusLabel = (row: SupplierCreditRow) => {
  if (row.docstatus === 2) return 'Cancelled'
  if (row.docstatus === 0) return 'Draft'
  return row.status || 'Open'
}

const statusClass = (row: SupplierCreditRow) => {
  if (row.docstatus === 2) return 'border-red-800 bg-red-950/60 text-red-300'
  if (row.docstatus === 0) return 'border-gray-700 bg-gray-800 text-gray-400'
  switch (row.status) {
    case 'Open': return 'border-orange-700 bg-orange-950/60 text-orange-300'
    case 'Partially Paid': return 'border-blue-700 bg-blue-950/60 text-blue-300'
    case 'Settled': return 'border-green-700 bg-green-950/60 text-green-300'
    default: return 'border-gray-700 bg-gray-900 text-gray-300'
  }
}

const load = async () => {
  loading.value = true
  pageError.value = ''
  try {
    rows.value = await frappeDB.getDocList<SupplierCreditRow>('Supplier Credit', {
      fields: [
        'name', 'supplier', 'dated', 'status', 'total_amount', 'amount_paid', 'balance',
        'source_document_type', 'source_document', 'docstatus',
      ],
      orderBy: { field: 'dated', order: 'desc' },
      limit: 100,
    })
    if (selected.value) {
      selected.value = rows.value.find((r) => r.name === selected.value!.name) ?? null
    }
  } catch (e: any) {
    pageError.value = e?.response?.data?.message || e?.message || 'Failed to load supplier credits.'
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editTarget.value = null
  form.supplier = ''
  form.dated = today()
  form.total_amount = 0
  form.source_document_type = ''
  form.source_document = ''
  formError.value = ''
  showForm.value = true
}

const openEdit = (row: SupplierCreditRow) => {
  editTarget.value = row
  form.supplier = row.supplier
  form.dated = row.dated
  form.total_amount = row.total_amount
  form.source_document_type = row.source_document_type || ''
  form.source_document = row.source_document || ''
  formError.value = ''
  showForm.value = true
}

const saveForm = async () => {
  if (!form.supplier.trim() || !form.dated || !form.total_amount) {
    formError.value = 'Supplier, date, and total amount are required.'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload: Record<string, any> = {
      supplier: form.supplier.trim(),
      dated: form.dated,
      total_amount: form.total_amount,
    }
    if (form.source_document_type) payload.source_document_type = form.source_document_type
    if (form.source_document) payload.source_document = form.source_document

    if (editTarget.value) {
      await apiClient.put(`/api/resource/Supplier Credit/${editTarget.value.name}`, payload)
    } else {
      const resp = await apiClient.post('/api/resource/Supplier Credit', payload)
      const created = resp.data.data as SupplierCreditRow
      await load()
      selected.value = rows.value.find((r) => r.name === created.name) ?? null
      showForm.value = false
      return
    }
    await load()
    showForm.value = false
  } catch (e: any) {
    formError.value = e?.response?.data?.message || e?.message || 'Failed to save.'
  } finally {
    saving.value = false
  }
}

const submitDoc = async (row: SupplierCreditRow) => {
  if (!window.confirm(`Submit ${row.name}? Once submitted, edit is locked.`)) return
  actioning.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/api/resource/Supplier Credit/${row.name}/submit`)
    await load()
  } catch (e: any) {
    actionError.value = e?.response?.data?.message || e?.message || 'Failed to submit.'
  } finally {
    actioning.value = false
  }
}

const cancelDoc = async (row: SupplierCreditRow) => {
  if (!window.confirm(`Cancel ${row.name}? This reverses linked payments.`)) return
  actioning.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/api/resource/Supplier Credit/${row.name}/cancel`)
    await load()
  } catch (e: any) {
    actionError.value = e?.response?.data?.message || e?.message || 'Failed to cancel.'
  } finally {
    actioning.value = false
  }
}

onMounted(load)
</script>
