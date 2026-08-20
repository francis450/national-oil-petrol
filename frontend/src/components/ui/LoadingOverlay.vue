<template>
	<transition
		enter-active-class="transition-opacity duration-300"
		leave-active-class="transition-opacity duration-200"
	>
		<div
			v-if="loading"
			class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
		>
			<Card class="max-w-sm w-full mx-4">
				<div class="flex items-center gap-4">
					<!-- Spinner -->
					<div class="relative">
						<div
							class="animate-spin rounded-full h-10 w-10 border-4 border-primary-500 border-t-transparent"
						/>
						<div
							class="absolute inset-0 animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent"
							style="animation-delay: -0.15s"
						/>
						<div
							class="absolute inset-0 animate-spin rounded-full h-10 w-10 border-4 border-primary-700 border-t-transparent"
							style="animation-delay: -0.3s"
						/>
					</div>

					<!-- Message -->
					<div>
						<h3 class="text-lg font-semibold text-white">
							{{ message || "Loading..." }}
						</h3>
						<p v-if="subtitle" class="text-sm text-gray-400 mt-1">{{ subtitle }}</p>
					</div>
				</div>
			</Card>
		</div>
	</transition>
</template>

<script setup lang="ts">
import Card from "./Card.vue";

withDefaults(
	defineProps<{
		loading?: boolean;
		message?: string;
		subtitle?: string;
	}>(),
	{
		loading: false,
		message: "Loading...",
		subtitle: "",
	}
);
</script>
