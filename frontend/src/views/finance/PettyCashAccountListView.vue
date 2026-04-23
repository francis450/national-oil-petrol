<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Petty Cash Accounts</h1>
      <p class="text-gray-400">Operational petty cash balances and ownership by department.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Accounts</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(accounts.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Total Balance</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(totalBalance) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Departments</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(uniqueDepartments) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Positive Balances</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(positiveBalances) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Account Register</h2>
            <p class="text-sm text-gray-400">Current petty cash balances from the custom finance model.</p>
          </div>
          <button
            @click="loadAccounts"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading petty cash accounts...</div>

        <div v-else-if="accounts.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No petty cash accounts found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Account</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Department</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Balance</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Last Replenished</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="account in accounts"
                :key="account.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedAccount?.name === account.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedAccount = account"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ account.account_name }}</td>
                <td class="px-4 py-3 text-gray-300">{{ account.department || '—' }}</td>
                <td class="px-4 py-3" :class="Number(account.balance || 0) > 0 ? 'text-green-300' : 'text-gray-300'">
                  {{ formatCurrency(account.balance) }}
                </td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(account.last_replenished) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Account Detail</h2>
          <p class="text-sm text-gray-400">Review account ownership and remaining balance before approving expenses.</p>
        </div>

        <div v-if="!selectedAccount" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select an account to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Account</p>
              <p class="text-lg font-semibold text-white">{{ selectedAccount.account_name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Department</p>
                <p class="text-gray-200">{{ selectedAccount.department || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Balance</p>
                <p class="text-green-300">{{ formatCurrency(selectedAccount.balance) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Last Replenished</p>
                <p class="text-gray-200">{{ formatDate(selectedAccount.last_replenished) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Record ID</p>
                <p class="text-gray-200">{{ selectedAccount.name }}</p>
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
import { financeApi, type PettyCashAccountRow } from '@/api/finance'

const accounts = ref<PettyCashAccountRow[]>([])
const selectedAccount = ref<PettyCashAccountRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const totalBalance = computed(() => accounts.value.reduce((sum, account) => sum + Number(account.balance || 0), 0))
const uniqueDepartments = computed(() => new Set(accounts.value.map((account) => account.department).filter(Boolean)).size)
const positiveBalances = computed(() => accounts.value.filter((account) => Number(account.balance || 0) > 0).length)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')

const loadAccounts = async () => {
  loading.value = true
  pageError.value = ''

  try {
    accounts.value = await financeApi.listPettyCashAccounts()
    if (!selectedAccount.value && accounts.value.length > 0) {
      selectedAccount.value = accounts.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load petty cash accounts.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadAccounts()
})
</script>
