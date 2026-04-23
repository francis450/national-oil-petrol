<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Petty Cash Entries</h1>
      <p class="text-gray-400">Expense movements and approvals from the custom petty cash ledger.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Entries</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(entries.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Total Amount</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(totalAmount) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Submitted</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(submittedCount) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Payment Modes</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(uniquePaymentMethods) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Expense Register</h2>
            <p class="text-sm text-gray-400">Petty cash expenses recorded against the custom account balances.</p>
          </div>
          <button
            @click="loadEntries"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading petty cash entries...</div>

        <div v-else-if="entries.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No petty cash entries found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Description</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Account</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Method</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in entries"
                :key="entry.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedEntry?.name === entry.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedEntry = entry"
              >
                <td class="px-4 py-3 text-gray-200">{{ formatDate(entry.dated) }}</td>
                <td class="px-4 py-3 text-gray-100 font-medium">{{ entry.description }}</td>
                <td class="px-4 py-3 text-gray-300">{{ entry.account }}</td>
                <td class="px-4 py-3 text-white">{{ formatCurrency(entry.amount) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ entry.payment_method || '—' }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex rounded-full border px-2.5 py-1 text-xs" :class="statusClass(entry.docstatus)">
                    {{ entry.docstatus === 1 ? 'Submitted' : 'Draft' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Entry Detail</h2>
          <p class="text-sm text-gray-400">Inspect amount, account, and approval metadata for a petty cash transaction.</p>
        </div>

        <div v-if="!selectedEntry" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select a petty cash entry to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Entry</p>
              <p class="text-lg font-semibold text-white">{{ selectedEntry.description }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Date</p>
                <p class="text-gray-200">{{ formatDate(selectedEntry.dated) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Amount</p>
                <p class="text-gray-200">{{ formatCurrency(selectedEntry.amount) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Account</p>
                <p class="text-gray-200">{{ selectedEntry.account }}</p>
              </div>
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedEntry.department || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Approved By</p>
                <p class="text-gray-200">{{ selectedEntry.approved_by || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Payment Method</p>
                <p class="text-gray-200">{{ selectedEntry.payment_method || '—' }}</p>
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
import { financeApi, type PettyCashEntryRow } from '@/api/finance'

const entries = ref<PettyCashEntryRow[]>([])
const selectedEntry = ref<PettyCashEntryRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const totalAmount = computed(() => entries.value.reduce((sum, entry) => sum + Number(entry.amount || 0), 0))
const submittedCount = computed(() => entries.value.filter((entry) => entry.docstatus === 1).length)
const uniquePaymentMethods = computed(() => new Set(entries.value.map((entry) => entry.payment_method).filter(Boolean)).size)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')

const statusClass = (docstatus: number) => {
  return docstatus === 1
    ? 'border-green-700 bg-green-950 text-green-200'
    : 'border-gray-700 bg-gray-900 text-gray-200'
}

const loadEntries = async () => {
  loading.value = true
  pageError.value = ''

  try {
    entries.value = await financeApi.listPettyCashEntries()
    if (!selectedEntry.value && entries.value.length > 0) {
      selectedEntry.value = entries.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load petty cash entries.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadEntries()
})
</script>
