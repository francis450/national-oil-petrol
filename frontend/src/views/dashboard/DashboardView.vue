<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-1">Operations Dashboard</h1>
        <p class="text-gray-400">Canonical ERPNext activity plus the operational backlog still waiting to be bridged.</p>
      </div>
      <button
        @click="loadDashboard"
        :disabled="loading"
        class="self-start px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
      <StatCard label="Today's Sales" :value="metrics.today_sales" type="currency" variant="success" />
      <StatCard label="Month Sales" :value="metrics.month_sales" type="currency" variant="success" />
      <StatCard label="Receivables" :value="metrics.outstanding_receivables" type="currency" variant="danger" />
      <StatCard label="Payables" :value="metrics.outstanding_payables" type="currency" variant="warning" />
      <StatCard label="Stock Balance" :value="`${formatNumber(metrics.stock_balance_qty)} Qty`" type="text" variant="info" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Chart
        title="Posted Sales Trend"
        type="line"
        :data="metrics.sales_trend"
        subtitle="Submitted ERPNext sales invoices over the last 7 days"
      />
      <Chart
        title="Stock Overview"
        type="bar"
        :data="stockLevels"
        subtitle="Top in-stock ERPNext items by current bin quantity"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h3 class="text-lg font-bold text-white">Operational Backlog</h3>
          <p class="text-sm text-gray-400">Custom operational records that still need to move into canonical ERPNext documents.</p>
        </div>

        <div class="rounded-lg border border-blue-900 bg-blue-950/40 px-4 py-3">
          <div class="flex items-center justify-between gap-4">
            <span class="text-sm text-blue-100">Total backlog across operational doctypes</span>
            <span class="text-2xl font-bold text-white">{{ formatNumber(metrics.operational_backlog) }}</span>
          </div>
        </div>

        <Chart
          title="Operational Pipeline"
          type="bar"
          :data="metrics.pipeline"
          subtitle="Fuel purchases, inventory receipts, and sales entries still in operational capture"
        />
      </div>

      <div class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h3 class="text-lg font-bold text-white">Settlement Snapshot</h3>
          <p class="text-sm text-gray-400">ERPNext settlement totals for the current month.</p>
        </div>

        <div class="grid grid-cols-1 gap-3">
          <div class="rounded-lg border border-green-900 bg-green-950/20 px-4 py-4">
            <p class="text-sm text-green-200">Receipts This Month</p>
            <p class="text-2xl font-bold text-white">{{ formatCurrency(metrics.settlement.receipts_this_month) }}</p>
          </div>
          <div class="rounded-lg border border-orange-900 bg-orange-950/20 px-4 py-4">
            <p class="text-sm text-orange-200">Payments This Month</p>
            <p class="text-2xl font-bold text-white">{{ formatCurrency(metrics.settlement.payments_this_month) }}</p>
          </div>
        </div>

        <Chart
          title="Today's Attendance"
          type="pie"
          :data="metrics.attendance"
          :legend="attendanceLegend"
          subtitle="ERPNext Attendance status counts for today"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Chart from '@/components/common/Chart.vue'
import StatCard from '@/components/common/StatCard.vue'
import { dashboardApi, type DashboardMetrics } from '@/api/dashboard'

const defaultMetrics: DashboardMetrics = {
  today_sales: 0,
  month_sales: 0,
  outstanding_receivables: 0,
  outstanding_payables: 0,
  stock_balance_qty: 0,
  operational_backlog: 0,
  sales_trend: [],
  stock_levels: [],
  attendance: [
    { label: 'Present', value: 0, color: 'bg-bioluminescent-green' },
    { label: 'Absent', value: 0, color: 'bg-alert-magenta' },
  ],
  pipeline: [],
  settlement: {
    receipts_this_month: 0,
    payments_this_month: 0,
  },
}

const metrics = ref<DashboardMetrics>(defaultMetrics)
const loading = ref(false)
const pageError = ref('')

const stockLevels = computed(() =>
  metrics.value.stock_levels.length
    ? metrics.value.stock_levels
    : [{ label: 'No stock yet', value: 0, color: 'bg-gray-600' }],
)

const attendanceLegend = computed(() =>
  metrics.value.attendance.map((row) => ({
    label: row.label,
    color: row.color || 'bg-gray-500',
  })),
)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const loadDashboard = async () => {
  loading.value = true
  pageError.value = ''

  try {
    metrics.value = await dashboardApi.getMetrics()
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load dashboard metrics.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDashboard()
})
</script>
