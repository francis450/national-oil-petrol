<template>
	<Card class="group stat-card" :no-border="true">
		<div class="flex items-center gap-4">
			<!-- Icon Container -->
			<div
				:class="[
					'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
					'transition-all duration-300 group-hover:scale-110',
					iconBackground,
				]"
			>
				<slot name="icon">
					<component :is="icon" v-if="icon" class="w-6 h-6 text-white" />
					<svg
						v-else
						class="w-6 h-6 text-white"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 10V3L4 14h7v7l9-11h-7z"
						/>
					</svg>
				</slot>
			</div>

			<!-- Content -->
			<div class="flex-1 min-w-0">
				<p class="text-sm text-gray-400 mb-1 truncate">{{ label }}</p>
				<p class="text-2xl sm:text-3xl font-bold text-white truncate">
					{{ formattedValue }}
				</p>

				<!-- Change indicator -->
				<div v-if="change !== null" class="flex items-center gap-1 mt-2">
					<svg
						v-if="change >= 0"
						class="w-4 h-4 text-success-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z"
						/>
					</svg>
					<svg
						v-else
						class="w-4 h-4 text-danger-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 13a1 1 0 110 2H7a1 1 0 01-1-1V9a1 1 0 112 0v3.586l4.293-4.293a1 1 0 011.414 1.414L8.414 13H12z"
						/>
					</svg>
					<span
						:class="change >= 0 ? 'text-success-500' : 'text-danger-500'"
						class="text-sm font-medium"
					>
						{{ Math.abs(change) }}% {{ change >= 0 ? "increase" : "decrease" }}
					</span>
				</div>
			</div>

			<!-- Action slot -->
			<div v-if="$slots.action" class="flex-shrink-0">
				<slot name="action" />
			</div>
		</div>
	</Card>
</template>

<script setup lang="ts">
import { computed, type Component } from "vue";
import Card from "@/components/ui/Card.vue";

const props = defineProps({
	label: {
		type: String,
		required: true,
	},
	value: {
		type: [Number, String],
		required: true,
	},
	type: {
		type: String as () => "currency" | "number" | "text" | "percentage",
		default: "number",
	},
	change: {
		type: Number,
		default: null,
	},
	variant: {
		type: String as () => "primary" | "success" | "warning" | "danger" | "info",
		default: "primary",
	},
	icon: {
		type: Object as () => Component,
		default: null,
	},
});

const formattedValue = computed(() => {
	switch (props.type) {
		case "currency":
			return `KSh ${Number(props.value).toLocaleString()}`;
		case "number":
			return Number(props.value).toLocaleString();
		case "percentage":
			return `${Number(props.value).toFixed(2)}%`;
		default:
			return String(props.value);
	}
});

const iconBackground = computed(() => {
	const colors = {
		primary: "bg-primary-600",
		success: "bg-success-600",
		warning: "bg-warning-600",
		danger: "bg-danger-600",
		info: "bg-info-600",
	};
	return colors[props.variant] || colors.primary;
});
</script>

<style scoped>
.stat-card {
	@apply border border-border/50;
}

.stat-card:hover {
	@apply border-border-subtle shadow-soft;
}
</style>
