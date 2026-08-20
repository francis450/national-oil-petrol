<template>
	<div class="space-y-6 animate-fade-in">
		<!-- Header -->
		<div class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
			<div>
				<h1 class="text-3xl font-bold text-white mb-1">Operations Dashboard</h1>
				<p class="text-gray-400">
					Canonical ERPNext activity plus the operational backlog still waiting to be
					bridged.
				</p>
			</div>
			<Button @click="loadDashboard" :disabled="loading" variant="secondary">
				<svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
					/>
				</svg>
				{{ loading ? "Refreshing..." : "Refresh" }}
			</Button>
		</div>

		<!-- Error Alert -->
		<Card v-if="pageError" class="p-4 border border-danger-500 bg-danger-600/10">
			<div class="flex items-center gap-3 text-danger-500">
				<svg
					class="w-5 h-5 flex-shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<span class="text-sm">{{ pageError }}</span>
			</div>
		</Card>

		<!-- Stats Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
			<StatCard
				label="Today's Sales"
				:value="metrics.today_sales"
				type="currency"
				variant="success"
				:change="salesChange"
			>
				<template #icon>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</template>
			</StatCard>

			<StatCard
				label="Month Sales"
				:value="metrics.month_sales"
				type="currency"
				variant="success"
				:change="monthSalesChange"
			>
				<template #icon>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
						/>
					</svg>
				</template>
			</StatCard>

			<StatCard
				label="Receivables"
				:value="metrics.outstanding_receivables"
				type="currency"
				variant="danger"
				:change="receivablesChange"
			>
				<template #icon>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</template>
			</StatCard>

			<StatCard
				label="Payables"
				:value="metrics.outstanding_payables"
				type="currency"
				variant="warning"
				:change="payablesChange"
			>
				<template #icon>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
						/>
					</svg>
				</template>
			</StatCard>

			<StatCard
				label="Stock Balance"
				:value="`${formatNumber(metrics.stock_balance_qty)} Qty`"
				type="text"
				variant="info"
			>
				<template #icon>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
						/>
					</svg>
				</template>
			</StatCard>
		</div>

		<!-- Charts Row 1 -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
			<Chart
				title="Posted Sales Trend"
				type="line"
				:data="metrics.sales_trend"
				subtitle="Submitted ERPNext sales invoices over the last 7 days"
				:legend="salesTrendLegend"
			/>

			<Chart
				title="Stock Overview"
				type="bar"
				:data="stockLevels"
				subtitle="Top in-stock ERPNext items by current bin quantity"
			/>
		</div>

		<!-- Charts Row 2 -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
			<!-- Operational Backlog -->
			<Card class="bg-surface-elevated border border-border rounded-xl p-6 space-y-4">
				<div>
					<h3 class="text-lg font-bold text-white">Operational Backlog</h3>
					<p class="text-sm text-gray-400">
						Custom operational records that still need to move into canonical ERPNext
						documents.
					</p>
				</div>

				<div class="rounded-xl border border-primary-900 bg-primary-950/40 px-4 py-3">
					<div class="flex items-center justify-between gap-4">
						<span class="text-sm text-primary-100"
							>Total backlog across operational doctypes</span
						>
						<span class="text-2xl font-bold text-white">{{
							formatNumber(metrics.operational_backlog)
						}}</span>
					</div>
				</div>

				<Chart
					title="Operational Pipeline"
					type="bar"
					:data="metrics.pipeline"
					subtitle="Fuel purchases, inventory receipts, and sales entries still in operational capture"
					:show-legend="false"
				/>
			</Card>

			<!-- Settlement Snapshot -->
			<Card class="bg-surface-elevated border border-border rounded-xl p-6 space-y-4">
				<div>
					<h3 class="text-lg font-bold text-white">Settlement Snapshot</h3>
					<p class="text-sm text-gray-400">
						ERPNext settlement totals for the current month.
					</p>
				</div>

				<div class="grid grid-cols-1 gap-3">
					<div class="rounded-xl border border-success-900 bg-success-950/20 px-4 py-4">
						<p class="text-sm text-success-200">Receipts This Month</p>
						<p class="text-2xl font-bold text-white">
							{{ formatCurrency(metrics.settlement.receipts_this_month) }}
						</p>
					</div>
					<div class="rounded-xl border border-warning-900 bg-warning-950/20 px-4 py-4">
						<p class="text-sm text-warning-200">Payments This Month</p>
						<p class="text-2xl font-bold text-white">
							{{ formatCurrency(metrics.settlement.payments_this_month) }}
						</p>
					</div>
				</div>

				<Chart
					title="Today's Attendance"
					type="doughnut"
					:data="metrics.attendance"
					:legend="attendanceLegend"
					subtitle="ERPNext Attendance status counts for today"
				/>
			</Card>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import Chart from "@/components/common/Chart.vue";
import StatCard from "@/components/common/StatCard.vue";
import Card from "@/components/ui/Card.vue";
import Button from "@/components/ui/Button.vue";
import { dashboardApi, type DashboardMetrics } from "@/api/dashboard";

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
		{ label: "Present", value: 0, color: "bg-success-500" },
		{ label: "Absent", value: 0, color: "bg-danger-500" },
	],
	pipeline: [],
	settlement: {
		receipts_this_month: 0,
		payments_this_month: 0,
	},
};

const metrics = ref<DashboardMetrics>(defaultMetrics);
const loading = ref(false);
const pageError = ref("");

const stockLevels = computed(() =>
	metrics.value.stock_levels.length
		? metrics.value.stock_levels
		: [{ label: "No stock yet", value: 0, color: "bg-gray-600" }]
);

const attendanceLegend = computed(() =>
	metrics.value.attendance.map((row) => ({
		label: row.label,
		color: row.color || "bg-gray-500",
	}))
);

const salesTrendLegend = computed(() => [{ label: "Sales", color: "bg-primary-500" }]);

// Mock change percentages (in a real app, these would come from the API)
const salesChange = computed(() => {
	return metrics.value.today_sales > 0 ? 12.5 : 0;
});

const monthSalesChange = computed(() => {
	return metrics.value.month_sales > 0 ? 8.3 : 0;
});

const receivablesChange = computed(() => {
	return metrics.value.outstanding_receivables > 0 ? -5.2 : 0;
});

const payablesChange = computed(() => {
	return metrics.value.outstanding_payables > 0 ? 3.1 : 0;
});

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`;
const formatNumber = (value?: number) => Number(value || 0).toLocaleString();

const loadDashboard = async () => {
	loading.value = true;
	pageError.value = "";

	try {
		metrics.value = await dashboardApi.getMetrics();
	} catch (error: any) {
		pageError.value =
			error?.response?.data?.message ||
			error?.message ||
			"Failed to load dashboard metrics.";
	} finally {
		loading.value = false;
	}
};

onMounted(async () => {
	await loadDashboard();
});
</script>

<style scoped></style>
