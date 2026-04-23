<template>
  <div class="space-y-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Credit Payments</h1>
        <p class="text-gray-400">Payments made to suppliers against outstanding credit balances.</p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shrink-0"
      >
        + New Payment
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900/20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">All Payments</h2>
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

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading credit payments...</div>

        <div
          v-else-if="rows.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No credit payment records found. Use "New Payment" to record one.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">ID</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Credit Ref</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Method</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">State</th>
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
                <td class="px-4 py-3 text-gray-300">{{ row.supplier_credit }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.supplier || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ fmtDate(row.dated) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.payment_method || '—' }}</td>
                <td class="px-4 py-3 text-orange-300 font-medium">{{ fmtCurrency(row.amount) }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full border px-2.5 py-0.5 text-xs"
                    :class="docstatusClass(row.docstatus)"
                  >{{ docstatusLabel(row.docstatus) }}</span>
                </td>
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
          Select a payment to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-3">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Credit Payment</p>
              <p class="text-lg font-semibold text-white">{{ selected.name }}</p>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Supplier Credit</p>
                <p class="text-gray-200">{{ selected.supplier_credit }}</p>
              </div>
              <div>
                <p class="text-gray-500">Supplier</p>
                <p class="text-gray-200">{{ selected.supplier || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Payment Date</p>
                <p class="text-gray-200">{{ fmtDate(selected.dated) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Amount</p>
                <p class="text-orange-300 font-medium">{{ fmtCurrency(selected.amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Method</p>
                <p class="text-gray-200">{{ selected.payment_method || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Reference</p>
                <p class="text-gray-200">{{ selected.reference || '—' }}</p>
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
              @click="submitDoc(selected)"
              :disabled="actioning"
              class="w-full px-4 py-2 rounded-lg bg-deepseek-blue text-white hover:bg-blue-700 disabled:opacity-40 transition-colors text-sm"
            >
              {{ actioning ? 'Submitting...' : 'Submit Payment' }}
            </button>
            <button
              v-if="selected.docstatus === 1"
              @click="cancelDoc(selected)"
              :disabled="actioning"
              class="w-full px-4 py-2 rounded-lg border border-red-800 bg-red-900/20 text-red-300 hover:bg-red-900/40 disabled:opacity-40 transition-colors text-sm"
            >
              {{ actioning ? 'Cancelling...' : 'Cancel Payment' }}
            </button>
          </div>
        </template>
      </aside>
    </div>

    <SlideOver v-model="showForm" title="New Credit Payment">
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Supplier Credit <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.supplier_credit"
            type="text"
            placeholder="e.g. NOF-CRD-2026-0001"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Payment Date <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.dated"
            type="date"
            class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">
            Amount (KSh) <span class="text-red-400">*</span>
          </label>
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
            <option>Cheque</option>
            <option>M-Pesa</option>
            <option>Bank Transfer</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-400 mb-1">Reference (Cheque no. / Transfer ref.)</label>
          <input
            v-model="form.reference"
            type="text"
            placeholder="Optional reference"
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
          {{ saving ? 'Saving...' : 'Create Payment' }}
        </button>
      </template>
    </SlideOver>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import SlideOver from '@/components/common/SlideOver.vue'
import { frappeDB, apiClient } from '@/api/client'

interface CreditPaymentRow {
  name: string
  supplier_credit: string
  supplier: string
  dated: string
  amount: number
  payment_method: string
  reference: string
  docstatus: number
}

const rows = ref<CreditPaymentRow[]>([])
const selected = ref<CreditPaymentRow | null>(null)
const loading = ref(false)
const pageError = ref('')
const actioning = ref(false)
const actionError = ref('')

const showForm = ref(false)
const saving = ref(false)
const formError = ref('')
const form = reactive({
  supplier_credit: '',
  dated: '',
  amount: 0,
  payment_method: '',
  reference: '',
})

const today = () => new Date().toISOString().split('T')[0]
const fmtCurrency = (v?: number) => `KSh ${Number(v || 0).toLocaleString()}`
const fmtDate = (v?: string) => (v ? new Date(v).toLocaleDateString('en-KE') : '—')

const docstatusLabel = (ds: number) => {
  if (ds === 2) return 'Cancelled'
  if (ds === 0) return 'Draft'
  return 'Submitted'
}

const docstatusClass = (ds: number) => {
  if (ds === 2) return 'border-red-800 bg-red-950/60 text-red-300'
  if (ds === 1) return 'border-green-700 bg-green-950/60 text-green-300'
  return 'border-gray-700 bg-gray-800 text-gray-400'
}

const load = async () => {
  loading.value = true
  pageError.value = ''
  try {
    rows.value = await frappeDB.getDocList<CreditPaymentRow>('Credit Payment', {
      fields: ['name', 'supplier_credit', 'supplier', 'dated', 'amount', 'payment_method', 'reference', 'docstatus'],
      orderBy: { field: 'dated', order: 'desc' },
      limit: 100,
    })
    if (selected.value) {
      selected.value = rows.value.find((r) => r.name === selected.value!.name) ?? null
    }
  } catch (e: any) {
    pageError.value = e?.response?.data?.message || e?.message || 'Failed to load credit payments.'
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  form.supplier_credit = ''
  form.dated = today()
  form.amount = 0
  form.payment_method = ''
  form.reference = ''
  formError.value = ''
  showForm.value = true
}

const saveForm = async () => {
  if (!form.supplier_credit.trim() || !form.dated || !form.amount) {
    formError.value = 'Supplier credit reference, date, and amount are required.'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const resp = await apiClient.post('/api/resource/Credit Payment', {
      supplier_credit: form.supplier_credit.trim(),
      dated: form.dated,
      amount: form.amount,
      payment_method: form.payment_method || undefined,
      reference: form.reference || undefined,
    })
    const created = resp.data.data as CreditPaymentRow
    await load()
    selected.value = rows.value.find((r) => r.name === created.name) ?? null
    showForm.value = false
  } catch (e: any) {
    formError.value = e?.response?.data?.message || e?.message || 'Failed to save.'
  } finally {
    saving.value = false
  }
}

const submitDoc = async (row: CreditPaymentRow) => {
  if (!window.confirm(`Submit payment ${row.name}?`)) return
  actioning.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/api/resource/Credit Payment/${row.name}/submit`)
    await load()
  } catch (e: any) {
    actionError.value = e?.response?.data?.message || e?.message || 'Failed to submit.'
  } finally {
    actioning.value = false
  }
}

const cancelDoc = async (row: CreditPaymentRow) => {
  if (!window.confirm(`Cancel payment ${row.name}? This reverses the credit reduction.`)) return
  actioning.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/api/resource/Credit Payment/${row.name}/cancel`)
    await load()
  } catch (e: any) {
    actionError.value = e?.response?.data?.message || e?.message || 'Failed to cancel.'
  } finally {
    actioning.value = false
  }
}

onMounted(load)
</script>
