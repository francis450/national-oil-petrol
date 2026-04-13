<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Sales Entries</h1>
      <p class="text-gray-400">Track and manage all sales transactions</p>
    </div>

    <DataTable
      title="Sales Entries"
      :columns="columns"
      :data="salesData"
      show-add
      show-edit
      add-label="New Entry"
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
  { key: 'date', label: 'Date', type: 'date' },
  { key: 'department', label: 'Department' },
  { key: 'type', label: 'Type' },
  { key: 'amount', label: 'Amount', type: 'currency' },
  { key: 'method', label: 'Payment Method' },
  { key: 'customer', label: 'Customer' },
  { key: 'status', label: 'Status', type: 'status' },
]

const salesData = ref([
  { date: '2026-04-11', department: 'Forecourt', type: 'Wet Stock', amount: 45200, method: 'Cash', customer: 'Retail', status: 'completed' },
  { date: '2026-04-11', department: 'Shop', type: 'Other', amount: 8500, method: 'Cash', customer: 'Retail', status: 'completed' },
  { date: '2026-04-10', department: 'Forecourt', type: 'Wet Stock', amount: 62100, method: 'Card', customer: 'Corporate', status: 'completed' },
  { date: '2026-04-10', department: 'Shop', type: 'Other', amount: 12300, method: 'Cash', customer: 'Retail', status: 'completed' },
])

const handleAdd = () => {
  alert('Create new sales entry - form coming soon')
}

const handleEdit = (row: any) => {
  alert('Edit sales entry: ' + JSON.stringify(row))
}

const loadData = () => {
  console.log('Refresh sales data')
}
</script>