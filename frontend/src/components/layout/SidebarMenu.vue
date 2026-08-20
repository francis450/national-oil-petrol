<template>
	<nav class="space-y-2">
		<!-- Dashboard -->
		<router-link
			to="/"
			:class="[
				'group flex items-center gap-3 px-4 py-3 rounded-xl',
				'text-sm font-medium transition-all duration-200',
				isActive('/')
					? 'bg-primary-600 text-white shadow-lg shadow-primary-500/20'
					: 'text-gray-400 hover:bg-surface hover:text-gray-300',
			]"
		>
			<div
				class="w-8 h-8 rounded-xl bg-primary-600/10 flex items-center justify-center group-hover:bg-primary-600/20 transition-colors"
			>
				<svg
					class="w-4 h-4"
					:class="isActive('/') ? 'text-white' : 'text-primary-500'"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
					/>
				</svg>
			</div>
			<span>Dashboard</span>
		</router-link>

		<!-- Fuel Operations (Collapsible) -->
		<SidebarMenuGroup
			:label="'Fuel Operations'"
			:icon="'FuelPump'"
			:expanded="expandedGroups.fuel"
			@toggle="toggleGroup('fuel')"
		>
			<router-link
				v-for="item in fuelItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-primary-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- Sales (Collapsible) -->
		<SidebarMenuGroup
			v-if="canAccessModule('sales')"
			:label="'Sales'"
			:icon="'ShoppingCart'"
			:expanded="expandedGroups.sales"
			@toggle="toggleGroup('sales')"
		>
			<router-link
				v-for="item in salesItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-success-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- Payables (Collapsible) -->
		<SidebarMenuGroup
			v-if="canAccessModule('payables')"
			:label="'Payables'"
			:icon="'CreditCard'"
			:expanded="expandedGroups.payables"
			@toggle="toggleGroup('payables')"
		>
			<router-link
				v-for="item in payablesItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-warning-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- Divider -->
		<div class="my-4 border-t border-border"></div>

		<!-- Inventory (Collapsible) -->
		<SidebarMenuGroup
			v-if="canAccessModule('inventory')"
			:label="'Inventory'"
			:icon="'Box'"
			:expanded="expandedGroups.inventory"
			@toggle="toggleGroup('inventory')"
		>
			<router-link
				v-for="item in inventoryItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-info-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- Finance (Collapsible) -->
		<SidebarMenuGroup
			v-if="canAccessModule('finance')"
			:label="'Finance'"
			:icon="'Banknote'"
			:expanded="expandedGroups.finance"
			@toggle="toggleGroup('finance')"
		>
			<router-link
				v-for="item in financeItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-purple-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- HR (Collapsible) -->
		<SidebarMenuGroup
			v-if="canAccessModule('hr')"
			:label="'Human Resources'"
			:icon="'Users'"
			:expanded="expandedGroups.hr"
			@toggle="toggleGroup('hr')"
		>
			<router-link
				v-for="item in hrItems"
				:key="item.path"
				:to="item.path"
				class="menu-subitem"
			>
				<div class="w-2 h-2 rounded-full bg-pink-500 mr-3" />
				<span>{{ item.label }}</span>
			</router-link>
		</SidebarMenuGroup>

		<!-- Reports -->
		<router-link
			v-if="canAccessModule('reports')"
			to="/reports"
			:class="[
				'group flex items-center gap-3 px-4 py-3 rounded-xl',
				'text-sm font-medium transition-all duration-200',
				isActive('/reports')
					? 'bg-primary-600 text-white shadow-lg shadow-primary-500/20'
					: 'text-gray-400 hover:bg-surface hover:text-gray-300',
			]"
		>
			<div
				class="w-8 h-8 rounded-xl bg-primary-600/10 flex items-center justify-center group-hover:bg-primary-600/20 transition-colors"
			>
				<svg
					class="w-4 h-4"
					:class="isActive('/reports') ? 'text-white' : 'text-primary-500'"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					/>
				</svg>
			</div>
			<span>Reports</span>
		</router-link>
	</nav>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import SidebarMenuGroup from "./SidebarMenuGroup.vue";
import { usePermissions } from "@/composables/usePermissions";

const route = useRoute();
const { canAccessModule } = usePermissions();

const expandedGroups = ref({
	fuel: false,
	sales: false,
	payables: false,
	inventory: false,
	finance: false,
	hr: false,
});

const toggleGroup = (group: keyof typeof expandedGroups.value) => {
	expandedGroups.value[group] = !expandedGroups.value[group];
};

const isActive = (path: string) => {
	return route.path === path || route.path.startsWith(path + "/");
};

// Menu items
const fuelItems = [
	{ path: "/fuel/purchases", label: "Fuel Purchases" },
	{ path: "/fuel/readings", label: "Pump Readings" },
	{ path: "/fuel/prices", label: "Fuel Prices" },
];

const salesItems = [
	{ path: "/sales/entries", label: "Sales Entries" },
	{ path: "/sales/targets", label: "Sales Targets" },
];

const payablesItems = [
	{ path: "/payables/credits", label: "Supplier Credits" },
	{ path: "/payables/payments", label: "Credit Payments" },
];

const inventoryItems = [
	{ path: "/inventory/receipts", label: "Inventory Receipts" },
	{ path: "/inventory/products", label: "Products" },
];

const financeItems = [
	{ path: "/finance/accounts", label: "Petty Cash Accounts" },
	{ path: "/finance/entries", label: "Petty Cash Entries" },
];

const hrItems = [
	{ path: "/hr/employees", label: "Employees" },
	{ path: "/hr/attendance", label: "Attendance" },
	{ path: "/hr/leave", label: "Leave Applications" },
];
</script>

<style scoped>
.menu-subitem {
	@apply flex items-center gap-3 px-4 py-2.5 text-sm rounded-xl;
	@apply text-gray-400 hover:bg-surface hover:text-gray-300;
	@apply transition-colors ml-6;
}

.menu-subitem.router-link-active {
	@apply bg-surface-elevated text-primary-400;
}
</style>
