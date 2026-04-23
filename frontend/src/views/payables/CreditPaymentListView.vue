<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Supplier Payments</h1>
      <p class="text-gray-400">Canonical ERPNext supplier payment entries created from payable settlement flows.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Payment Entry History</h2>
            <p class="text-sm text-gray-400">Recent ERPNext supplier disbursements, ordered from newest to oldest.</p>
          </div>
          <button
            @click="loadPayments"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading supplier payments...</div>

        <div
          v-else-if="payments.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No supplier payment entries found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Payment</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Mode</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="payment in payments"
                :key="payment.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedPayment?.name === payment.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedPayment = payment"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ payment.name }}</td>
                <td class="px-4 py-3 text-gray-300">{{ payment.party_name || payment.party || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(payment.posting_date) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ payment.mode_of_payment || '—' }}</td>
                <td class="px-4 py-3 text-orange-300 font-medium">{{ formatCurrency(payment.paid_amount) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(payment.status)">
                    {{ payment.status || draftLabel(payment.docstatus) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Payment Detail</h2>
          <p class="text-sm text-gray-400">Use this to confirm supplier, mode of payment, and current ERPNext document state.</p>
        </div>

        <div
          v-if="!selectedPayment"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select a payment entry to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Payment Entry</p>
              <p class="text-lg font-semibold text-white">{{ selectedPayment.name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Supplier</p>
                <p class="text-gray-200">{{ selectedPayment.party_name || selectedPayment.party || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Company</p>
                <p class="text-gray-200">{{ selectedPayment.company || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Type</p>
                <p class="text-gray-200">{{ selectedPayment.payment_type }}</p>
              </div>
              <div>
                <p class="text-gray-500">Mode</p>
                <p class="text-gray-200">{{ selectedPayment.mode_of_payment || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Paid</p>
                <p class="text-orange-300">{{ formatCurrency(selectedPayment.paid_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Posting Date</p>
                <p class="text-gray-200">{{ formatDate(selectedPayment.posting_date) }}</p>
              </div>
            </div>

            <div class="rounded-lg border border-gray-800 bg-black p-3 text-sm text-gray-300">
              Draft supplier disbursements created from the new frontend should appear here immediately, then continue through normal ERPNext approval and submission.
            </div>
          </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { commerceApi, type PaymentEntryRow } from '@/api/commerce'

const payments = ref<PaymentEntryRow[]>([])
const selectedPayment = ref<PaymentEntryRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')
const draftLabel = (docstatus?: number) => (docstatus === 1 ? 'Submitted' : 'Draft')

const statusClass = (status?: string) => {
  if (status === 'Submitted' || status === 'Paid') {
    return 'border-green-700 bg-green-950 text-green-200'
  }
  return 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadPayments = async () => {
  loading.value = true
  pageError.value = ''

  try {
    payments.value = await commerceApi.listPayablePayments()
    if (!selectedPayment.value && payments.value.length > 0) {
      selectedPayment.value = payments.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load supplier payments.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadPayments()
})
</script>
