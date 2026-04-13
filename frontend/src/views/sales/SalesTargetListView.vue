<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Sales Targets</h1>
      <p class="text-gray-400">Set and manage performance targets by department</p>
    </div>

    <DataTable
      title="Sales Targets"
      :columns="columns"
      :data="targetData"
      show-add
      show-edit
      add-label="New Target"
      @add="handleAdd"
      @edit="handleEdit"
      @refresh="loadData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DataTable from '@/components/common/DataTable.vue'

const columns = [
  { key: 'period', label: 'Period' },
  { key: 'department', label: 'Department' },
  { key: 'target', label: 'Target', type: 'currency' },
  { key: 'actual', label: 'Actual', type: 'currency' },
  { key: 'deviation', label: 'Deviation', type: 'currency' },
  { key: 'variance', label: 'Variance %' },
]

const targetData = ref([
  { period: 'April 2026', department: 'Forecourt', target: 900000, actual: 940000, deviation: 40000, variance: '+4.4%' },
  { period: 'April 2026', department: 'Shop', target: 200000, actual: 185000, deviation: -15000, variance: '-7.5%' },
  { period: 'April 2026', department: 'Service', target: 150000, actual: 162000, deviation: 12000, variance: '+8.0%' },
])

const handleAdd = () => {
  alert('Create new sales target - form coming soon')
}

const handleEdit = (row: any) => {
  alert('Edit target: ' + JSON.stringify(row))
}

const loadData = () => {
  console.log('Refresh target data')
}
</script>