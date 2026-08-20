<template>
	<Card class="chart-card">
		<template #header>
			<div class="flex items-center justify-between">
				<div>
					<h3 class="text-lg font-semibold text-white">{{ title }}</h3>
					<p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
				</div>

				<!-- Legend -->
				<div v-if="legend && legend.length > 0" class="flex gap-4 text-xs">
					<div v-for="(item, idx) in legend" :key="idx" class="flex items-center gap-2">
						<div class="w-2 h-2 rounded-full" :class="item.color || getColor(idx)" />
						<span class="text-gray-400">{{ item.label }}</span>
					</div>
				</div>
			</div>
		</template>

		<div class="relative h-64">
			<!-- Loading state -->
			<div v-if="loading" class="absolute inset-0 flex items-center justify-center">
				<div
					class="animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"
				/>
			</div>

			<!-- Error state -->
			<div v-else-if="error" class="absolute inset-0 flex items-center justify-center">
				<p class="text-danger-500 text-sm">{{ error }}</p>
			</div>

			<!-- Empty state -->
			<div
				v-else-if="!data || data.length === 0"
				class="absolute inset-0 flex items-center justify-center"
			>
				<p class="text-gray-500 text-sm">No data available</p>
			</div>

			<!-- Chart container -->
			<div v-else class="h-full">
				<component
					:is="chartComponent"
					:data="chartData"
					:options="chartOptions"
					:key="chartKey"
				/>
			</div>
		</div>

		<template #footer v-if="footerText">
			<p class="text-xs text-gray-500 text-center">{{ footerText }}</p>
		</template>
	</Card>
</template>

<script setup lang="ts">
import { computed, ref, watch, type Component } from "vue";
import Card from "@/components/ui/Card.vue";
import {
	Bar as BarChart,
	Line as LineChart,
	Doughnut as DoughnutChart,
	Pie as PieChart,
	PolarArea as PolarAreaChart,
	Radar as RadarChart,
} from "vue-chartjs";
import type { ChartData, ChartOptions } from "chart.js";

interface ChartDataItem {
	label: string;
	value: number;
	color?: string;
}

interface LegendItem {
	label: string;
	color?: string;
}

const props = withDefaults(
	defineProps<{
		title: string;
		type?: "bar" | "line" | "doughnut" | "pie" | "polarArea" | "radar";
		data?: ChartDataItem[];
		legend?: LegendItem[];
		subtitle?: string;
		footerText?: string;
		loading?: boolean;
		error?: string;
		showLegend?: boolean;
		height?: number;
	}>(),
	{
		type: "bar",
		data: () => [],
		legend: () => [],
		loading: false,
		error: "",
		showLegend: true,
		height: 256,
	}
);

// Chart component mapping
const chartComponents: Record<string, Component> = {
	bar: BarChart,
	line: LineChart,
	doughnut: DoughnutChart,
	pie: PieChart,
	polarArea: PolarAreaChart,
	radar: RadarChart,
};

const chartComponent = computed(() => chartComponents[props.type] || BarChart);

// Generate unique key for chart re-rendering
const chartKey = ref(0);
watch(
	() => [props.type, props.data],
	() => {
		chartKey.value++;
	},
	{ deep: true }
);

// Color palette
const colors = [
	"#3b82f6", // primary-500
	"#22c55e", // success-500
	"#f59e0b", // warning-500
	"#ef4444", // danger-500
	"#8b5cf6", // purple-500
	"#06b6d4", // cyan-500
	"#f97316", // orange-500
	"#ec4899", // pink-500
];

const getColor = (index: number): string => {
	return colors[index % colors.length];
};

// Convert data to Chart.js format
const chartData = computed<ChartData>(() => {
	if (!props.data || props.data.length === 0) {
		return {
			labels: [],
			datasets: [],
		};
	}

	switch (props.type) {
		case "bar":
		case "line":
		case "radar":
			return {
				labels: props.data.map((d) => d.label),
				datasets: [
					{
						label: props.title,
						data: props.data.map((d) => d.value),
						backgroundColor: props.data.map(
							(_, i) => colors[i % colors.length] + "40"
						), // 25% opacity
						borderColor: props.data.map((_, i) => colors[i % colors.length]),
						borderWidth: 2,
						tension: props.type === "line" ? 0.4 : 0,
						pointBackgroundColor: props.data.map((_, i) => colors[i % colors.length]),
						pointBorderColor: "#fff",
						pointBorderWidth: 2,
						pointRadius: props.type === "line" ? 4 : 0,
						pointHoverRadius: props.type === "line" ? 6 : 0,
					},
				],
			};

		case "doughnut":
		case "pie":
		case "polarArea":
			return {
				labels: props.data.map((d) => d.label),
				datasets: [
					{
						label: props.title,
						data: props.data.map((d) => d.value),
						backgroundColor: props.data.map(
							(d, i) => d.color || colors[i % colors.length]
						),
						borderColor: "#1e293b", // surface-elevated
						borderWidth: 2,
						hoverOffset: props.type === "pie" ? 10 : 0,
					},
				],
			};

		default:
			return {
				labels: props.data.map((d) => d.label),
				datasets: [
					{
						label: props.title,
						data: props.data.map((d) => d.value),
						backgroundColor: props.data.map(
							(_, i) => colors[i % colors.length] + "40"
						),
						borderColor: props.data.map((_, i) => colors[i % colors.length]),
						borderWidth: 2,
					},
				],
			};
	}
});

// Chart options
const chartOptions = computed<ChartOptions>(() => {
	const isDark = document.documentElement.classList.contains("dark");
	const textColor = isDark ? "#e2e8f0" : "#334155";
	const gridColor = isDark ? "#334155" : "#e2e8f0";
	const backgroundColor = isDark ? "#1e293b" : "#ffffff";

	return {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				display: props.showLegend && props.legend && props.legend.length > 0,
				position: "bottom",
				labels: {
					color: textColor,
					padding: 15,
					usePointStyle: true,
					pointStyle: "circle",
				},
			},
			tooltip: {
				backgroundColor: backgroundColor,
				titleColor: "#ffffff",
				bodyColor: textColor,
				borderColor: gridColor,
				borderWidth: 1,
				padding: 12,
				cornerRadius: 8,
				displayColors: true,
				callbacks: {
					label: (context) => {
						let label = context.dataset.label || "";
						if (label) {
							label += ": ";
						}
						label +=
							context.parsed.y ||
							context.parsed.r ||
							context.parsed.x ||
							context.raw;
						return label;
					},
				},
			},
		},
		scales: {
			x: {
				grid: {
					color: gridColor,
					drawBorder: false,
				},
				ticks: {
					color: textColor,
					font: {
						size: 12,
					},
				},
			},
			y: {
				grid: {
					color: gridColor,
					drawBorder: false,
				},
				ticks: {
					color: textColor,
					font: {
						size: 12,
					},
					callback: (value) => {
						// Format numbers with commas
						return Number(value).toLocaleString();
					},
				},
			},
			r: {
				grid: {
					color: gridColor,
				},
				ticks: {
					color: textColor,
					display: false,
				},
			},
		},
		animation: {
			duration: 1000,
			easing: "easeInOutQuart",
		},
	};
});
</script>

<style scoped>
.chart-card {
	@apply border border-border/50;
}

.chart-card:hover {
	@apply border-border-subtle;
}
</style>
