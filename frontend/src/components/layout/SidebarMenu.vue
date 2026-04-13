<template>
  <nav class="space-y-1">
    <!-- Dashboard -->
    <router-link
      to="/"
      :class="[
        'group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        isActive('/') 
          ? 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue border-l-4 border-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
      </svg>
      Dashboard
    </router-link>

    <!-- Fuel Operations (Collapsible) -->
    <SidebarMenuGroup 
      :label="'Fuel Operations'" 
      :expanded="expandedGroups.fuel"
      @toggle="toggleGroup('fuel')"
    >
      <router-link to="/fuel/purchases" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Fuel Purchases
      </router-link>
      <router-link to="/fuel/readings" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Pump Readings
      </router-link>
      <router-link to="/fuel/prices" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Fuel Prices
      </router-link>
    </SidebarMenuGroup>

    <!-- Sales (Collapsible) -->
    <SidebarMenuGroup 
      :label="'Sales'" 
      :expanded="expandedGroups.sales"
      @toggle="toggleGroup('sales')"
    >
      <router-link to="/sales/entries" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Sales Entries
      </router-link>
      <router-link to="/sales/targets" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Sales Targets
      </router-link>
    </SidebarMenuGroup>

    <!-- Receivables (Collapsible) -->
    <SidebarMenuGroup 
      :label="'Receivables'" 
      :expanded="expandedGroups.receivables"
      @toggle="toggleGroup('receivables')"
    >
      <router-link to="/receivables/debts" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Customer Debts
      </router-link>
      <router-link to="/receivables/payments" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Debt Payments
      </router-link>
    </SidebarMenuGroup>

    <!-- Payables (Collapsible) -->
    <SidebarMenuGroup 
      :label="'Payables'" 
      :expanded="expandedGroups.payables"
      @toggle="toggleGroup('payables')"
    >
      <router-link to="/payables/credits" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Supplier Credits
      </router-link>
      <router-link to="/payables/payments" class="menu-subitem">
        <span class="w-1 h-1 rounded-full bg-gray-600 mr-3"></span>
        Credit Payments
      </router-link>
    </SidebarMenuGroup>

    <!-- Divider -->
    <div class="my-4 border-t border-gray-800"></div>

    <!-- Inventory -->
    <router-link
      to="/inventory"
      :class="[
        'group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        isActive('/inventory') 
          ? 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue border-l-4 border-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
        <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" />
      </svg>
      Inventory
    </router-link>

    <!-- Finance -->
    <router-link
      to="/finance"
      :class="[
        'group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        isActive('/finance') 
          ? 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue border-l-4 border-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
      </svg>
      Finance
    </router-link>

    <!-- HR -->
    <router-link
      to="/hr"
      :class="[
        'group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        isActive('/hr') 
          ? 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue border-l-4 border-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v2h8v-2zM16 11a2 2 0 100-4 2 2 0 000 4zM20 13a2 2 0 100-4 2 2 0 000 4z" />
      </svg>
      Human Resources
    </router-link>

    <!-- Reports -->
    <router-link
      to="/reports"
      :class="[
        'group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        isActive('/reports') 
          ? 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue border-l-4 border-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg class="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zm0 8a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" />
      </svg>
      Reports
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import SidebarMenuGroup from './SidebarMenuGroup.vue'

const route = useRoute()

const expandedGroups = ref({
  fuel: false,
  sales: false,
  receivables: false,
  payables: false,
})

const toggleGroup = (group: keyof typeof expandedGroups.value) => {
  expandedGroups.value[group] = !expandedGroups.value[group]
}

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
.menu-subitem {
  @apply flex items-center px-4 py-2.5 text-xs font-medium rounded-lg text-gray-400 hover:bg-gray-800 hover:text-deepseek-blue transition-colors ml-1 my-1;
}

.menu-subitem.router-link-active {
  @apply bg-gray-800 text-deepseek-blue;
}
</style>
