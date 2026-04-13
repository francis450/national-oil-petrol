<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Dashboard</h1>
      <p class="text-gray-400">Welcome back! Here's your business summary.</p>
    </div>

    <!-- Stats Cards Row 1 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Today's Sales"
        :value="dashboardData.todaySales"
        type="currency"
        :change="4"
        variant="success"
      />
      <StatCard
        label="Month Sales"
        :value="dashboardData.monthSales"
        type="currency"
        :change="12"
        variant="success"
      />
      <StatCard
        label="Outstanding Debts"
        :value="dashboardData.outstandingDebts"
        type="currency"
        :change="-8"
        variant="danger"
      />
      <StatCard
        label="Fuel Stock"
        :value="dashboardData.fuelStock + ' L'"
        type="text"
        variant="info"
      />
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Chart
        title="Sales Trend (7 Days)"
        type="line"
        :data="salesTrendData"
        subtitle="Daily sales over the last 7 days"
      />
      <Chart
        title="Fuel Stock Levels"
        type="bar"
        :data="fuelStockData"
      />
    </div>

    <!-- Secondary Stats -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 class="text-lg font-bold text-white mb-4">Outstanding Debts Summary</h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center pb-3 border-b border-gray-800">
            <span class="text-gray-400">Total Outstanding</span>
            <span class="text-xl font-bold text-alert-magenta">KSh {{ dashboardData.outstandingDebts.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between items-center pb-3 border-b border-gray-800">
            <span class="text-gray-400">Number of Debts</span>
            <span class="text-xl font-bold text-white">14</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-400">Oldest Debt</span>
            <span class="text-sm text-yellow-400">45 days old</span>
          </div>
          <button class="mt-4 w-full px-4 py-2 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
            View All Debts →
          </button>
        </div>
      </div>

      <div class="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 class="text-lg font-bold text-white mb-4">Today's Attendance</h3>
        <Chart
          title=""
          type="pie"
          :data="attendanceData"
        />
      </div>
    </div>

    <!-- Performance vs Target -->
    <div class="bg-gray-900 border border-gray-800 rounded-lg p-6">
      <h3 class="text-lg font-bold text-white mb-4">Department Performance - This Month</h3>
      <div class="space-y-4">
        <div v-for="dept in departmentPerformance" :key="dept.name" class="space-y-1">
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">{{ dept.name }}</span>
            <span class="text-white font-medium">
              Target: KSh {{ dept.target.toLocaleString() }} | Hit: KSh {{ dept.hit.toLocaleString() }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <div class="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                class="h-full"
                :class="dept.hit >= dept.target ? 'bg-bioluminescent-green' : 'bg-alert-magenta'"
                :style="{ width: ((dept.hit / dept.target) * 100) + '%' }"
              ></div>
            </div>
            <span
              :class="dept.hit >= dept.target ? 'text-bioluminescent-green' : 'text-alert-magenta'"
              class="text-xs font-medium min-w-fit"
            >
              {{ dept.hit >= dept.target ? '+' : '' }}{{ ((dept.hit - dept.target) / dept.target * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import Chart from '@/components/common/Chart.vue'

const dashboardData = ref({
  todaySales: 45200,
  monthSales: 1250000,
  outstandingDebts: 124500,
  fuelStock: 4250,
})

const salesTrendData = [
  { label: 'Mon', value: 32000 },
  { label: 'Tue', value: 38500 },
  { label: 'Wed', value: 35200 },
  { label: 'Thu', value: 42100 },
  { label: 'Fri', value: 48900 },
  { label: 'Sat', value: 51200 },
  { label: 'Sun', value: 45200 },
]

const fuelStockData = [
  { label: 'Petrol', value: 2850, color: 'bg-deepseek-blue' },
  { label: 'Diesel', value: 1400, color: 'bg-bioluminescent-green' },
]

const attendanceData = [
  { label: 'Present', value: 10 },
  { label: 'Absent', value: 2 },
]

const departmentPerformance = ref([
  { name: 'Forecourt', target: 900000, hit: 940000 },
  { name: 'Shop', target: 200000, hit: 185000 },
  { name: 'Service', target: 150000, hit: 162000 },
])
</script>

<style scoped>
</style>
