<template>
	<Card class="text-center py-12 sm:py-16" :no-border="true">
		<div class="flex flex-col items-center gap-4 sm:gap-6">
			<!-- Icon -->
			<div
				:class="[
					'w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center',
					'bg-surface-elevated/50',
					iconBackground,
				]"
			>
				<slot name="icon">
					<component
						:is="icon"
						v-if="icon"
						class="w-8 h-8 sm:w-10 sm:h-10"
						:class="iconColor"
					/>
					<svg
						v-else
						class="w-8 h-8 sm:w-10 sm:h-10 text-gray-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/>
					</svg>
				</slot>
			</div>

			<!-- Title -->
			<h3 v-if="title" class="text-lg sm:text-xl font-semibold text-white">
				{{ title }}
			</h3>

			<!-- Description -->
			<p v-if="description" class="text-sm sm:text-base text-gray-400 max-w-sm">
				{{ description }}
			</p>

			<!-- Actions -->
			<div v-if="$slots.actions" class="flex gap-3 mt-4">
				<slot name="actions" />
			</div>
		</div>
	</Card>
</template>

<script setup lang="ts">
import { computed, type Component } from "vue";
import Card from "./Card.vue";

const props = withDefaults(
	defineProps<{
		title?: string;
		description?: string;
		icon?: Component;
		variant?: "info" | "success" | "warning" | "danger";
	}>(),
	{
		title: "No data available",
		description: "",
		variant: "info",
	}
);

const iconBackground = computed(() => {
	const colors = {
		info: "bg-primary-600/10",
		success: "bg-success-600/10",
		warning: "bg-warning-600/10",
		danger: "bg-danger-600/10",
	};
	return colors[props.variant] || colors.info;
});

const iconColor = computed(() => {
	const colors = {
		info: "text-primary-500",
		success: "text-success-500",
		warning: "text-warning-500",
		danger: "text-danger-500",
	};
	return colors[props.variant] || colors.info;
});
</script>

<style scoped></style>
