<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Supplier Payables</h1>
      <p class="text-gray-400">Canonical ERPNext purchase invoices with draft payment-entry disbursement actions.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Outstanding Purchase Invoices</h2>
            <p class="text-sm text-gray-400">Supplier balances now come directly from ERPNext purchase accounting records.</p>
          </div>
          <button
            @click="loadInvoices"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div class="rounded-lg border border-blue-900 bg-blue-950/40 px-4 py-3 text-sm text-blue-100">
          This first settlement pass creates draft ERPNext <span class="font-semibold">Payment Entry</span> records using
          <span class="font-semibold">Cash</span>, which is the configured supplier payment mode on this site.
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading payables...</div>

        <div
          v-else-if="outstandingInvoices.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No outstanding purchase invoices found.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Invoice</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Outstanding</th>
                <th class="px-4 py-3 text-center text-gray-400 font-medium text-xs uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="invoice in outstandingInvoices"
                :key="invoice.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedInvoice?.name === invoice.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
              >
                <td class="px-4 py-3">
                  <button class="text-left" @click="selectedInvoice = invoice">
                    <span class="block text-gray-100 font-medium">{{ invoice.name }}</span>
                    <span class="block text-xs text-gray-500">{{ formatCurrency(invoice.grand_total) }} total</span>
                  </button>
                </td>
                <td class="px-4 py-3 text-gray-300">{{ invoice.supplier_name || invoice.supplier || '—' }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(invoice.posting_date) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(invoice.status)">
                    {{ invoice.status || draftLabel(invoice) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-orange-300 font-medium">{{ formatCurrency(invoice.outstanding_amount) }}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-center gap-2">
                    <button
                      @click="selectedInvoice = invoice"
                      class="px-3 py-1.5 text-xs rounded bg-blue-900 text-blue-200 hover:bg-blue-800 transition-colors"
                    >
                      Details
                    </button>
                    <button
                      @click="createPayment(invoice)"
                      :disabled="creatingPaymentFor === invoice.name || invoice.docstatus !== 1"
                      class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      {{ creatingPaymentFor === invoice.name ? 'Creating...' : 'Create Cash Payment' }}
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
          <h2 class="text-xl font-bold text-white">Payable Detail</h2>
          <p class="text-sm text-gray-400">Use ERPNext purchase invoices as the source of truth, then create draft disbursements from there.</p>
        </div>

        <div
          v-if="!selectedInvoice"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select an invoice to inspect its payable state.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Purchase Invoice</p>
              <p class="text-lg font-semibold text-white">{{ selectedInvoice.name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Supplier</p>
                <p class="text-gray-200">{{ selectedInvoice.supplier_name || selectedInvoice.supplier || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Company</p>
                <p class="text-gray-200">{{ selectedInvoice.company || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Total</p>
                <p class="text-gray-200">{{ formatCurrency(selectedInvoice.grand_total) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Outstanding</p>
                <p class="text-orange-300">{{ formatCurrency(selectedInvoice.outstanding_amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Posting Date</p>
                <p class="text-gray-200">{{ formatDate(selectedInvoice.posting_date) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Docstatus</p>
                <p class="text-gray-200">{{ selectedInvoice.docstatus === 1 ? 'Submitted' : 'Draft' }}</p>
              </div>
            </div>

            <div class="rounded-lg border border-gray-800 bg-black p-3 text-sm text-gray-300 space-y-2">
              <p class="text-xs uppercase tracking-wider text-gray-500">Disbursement Rule</p>
              <p>
                Payment entries can only be created from submitted ERPNext invoices. Draft purchase invoices should be
                reviewed and submitted in ERPNext first.
              </p>
            </div>

            <button
              @click="createPayment(selectedInvoice)"
              :disabled="creatingPaymentFor === selectedInvoice.name || selectedInvoice.docstatus !== 1"
              class="w-full px-4 py-2 rounded-lg bg-deepseek-blue text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {{ creatingPaymentFor === selectedInvoice.name ? 'Creating Payment Entry...' : 'Create Cash Payment Entry' }}
            </button>
          </div>
        </template>

        <div v-if="createdPayments.length" class="pt-2 border-t border-gray-800 space-y-2">
          <p class="text-xs uppercase tracking-wider text-gray-500">Created ERPNext Drafts</p>
          <div
            v-for="payment in createdPayments"
            :key="payment.name"
            class="rounded border border-green-800 bg-green-900 bg-opacity-10 px-3 py-2 text-sm text-green-200"
          >
            Payment Entry: {{ payment.name }} for {{ payment.reference_name }}
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { commerceApi, type CommerceInvoiceRow, type PaymentEntryResult } from '@/api/commerce'

const invoices = ref<CommerceInvoiceRow[]>([])
const loading = ref(false)
const pageError = ref('')
const creatingPaymentFor = ref('')
const selectedInvoice = ref<CommerceInvoiceRow | null>(null)
const createdPayments = ref<PaymentEntryResult[]>([])

const outstandingInvoices = computed(() =>
  invoices.value.filter((invoice) => Number(invoice.outstanding_amount || 0) > 0),
)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')
const draftLabel = (invoice: CommerceInvoiceRow) => (invoice.docstatus === 1 ? 'Submitted' : 'Draft')

const statusClass = (status?: string) => {
  if (status === 'Overdue' || status === 'Unpaid') {
    return 'border-orange-700 bg-orange-950 text-orange-200'
  }
  if (status === 'Paid') {
    return 'border-green-700 bg-green-950 text-green-200'
  }
  return 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadInvoices = async () => {
  loading.value = true
  pageError.value = ''

  try {
    invoices.value = await commerceApi.listPayableInvoices()
    if (!selectedInvoice.value && outstandingInvoices.value.length > 0) {
      selectedInvoice.value = outstandingInvoices.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load supplier payables.'
  } finally {
    loading.value = false
  }
}

const createPayment = async (invoice: CommerceInvoiceRow) => {
  creatingPaymentFor.value = invoice.name
  pageError.value = ''

  try {
    const result = await commerceApi.createPaymentEntry('Purchase Invoice', invoice.name)
    createdPayments.value = [
      result,
      ...createdPayments.value.filter((entry) => entry.name !== result.name),
    ]
  } catch (error: any) {
    pageError.value =
      error?.response?.data?.message || error?.message || `Failed to create payment entry for ${invoice.name}.`
  } finally {
    creatingPaymentFor.value = ''
  }
}

onMounted(async () => {
  await loadInvoices()
})
</script>
