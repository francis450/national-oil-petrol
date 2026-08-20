<template>
	<transition
		enter-active-class="transition-all duration-300 ease-out"
		leave-active-class="transition-all duration-200 ease-in"
		enter-from-class="transform translate-x-full opacity-0"
		enter-to-class="transform translate-x-0 opacity-100"
		leave-from-class="transform translate-x-0 opacity-100"
		leave-to-class="transform translate-x-full opacity-0"
	>
		<div
			v-if="show"
			:class="[
				'fixed top-6 right-6 z-50',
				'max-w-sm w-full px-6 py-4 rounded-xl',
				'shadow-lg animate-slide-up',
				{
					'bg-primary-600 text-white': variant === 'info',
					'bg-success-600 text-white': variant === 'success',
					'bg-warning-600 text-white': variant === 'warning',
					'bg-danger-600 text-white': variant === 'error',
				},
			]"
			@mouseenter="pauseTimer"
			@mouseleave="resumeTimer"
		>
			<div class="flex items-start gap-3">
				<!-- Icon -->
				<div class="flex-shrink-0">
					<svg
						v-if="variant === 'info'"
						class="w-5 h-5"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<svg
						v-if="variant === 'success'"
						class="w-5 h-5"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					<svg
						v-if="variant === 'warning'"
						class="w-5 h-5"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					<svg
						v-if="variant === 'error'"
						class="w-5 h-5"
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
				</div>

				<!-- Content -->
				<div class="flex-1">
					<p class="font-medium">{{ message }}</p>
					<p v-if="subtitle" class="text-sm opacity-90 mt-1">{{ subtitle }}</p>
				</div>

				<!-- Close button -->
				<button
					@click="close"
					class="flex-shrink-0 p-1 rounded-lg hover:bg-white/20 transition-colors"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
		</div>
	</transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";

const props = withDefaults(
	defineProps<{
		message: string;
		subtitle?: string;
		variant?: "info" | "success" | "warning" | "error";
		duration?: number;
		persistent?: boolean;
	}>(),
	{
		variant: "info",
		duration: 5000,
		persistent: false,
	}
);

const emit = defineEmits(["close", "dismissed"]);

const show = ref(true);
let timer: ReturnType<typeof setTimeout> | null = null;

const startTimer = () => {
	if (props.persistent) return;

	timer = setTimeout(() => {
		close();
	}, props.duration);
};

const pauseTimer = () => {
	if (timer) {
		clearTimeout(timer);
		timer = null;
	}
};

const resumeTimer = () => {
	if (props.persistent) return;
	startTimer();
};

const close = () => {
	show.value = false;
	emit("close");

	// Small delay to allow transition to complete
	setTimeout(() => {
		emit("dismissed");
	}, 200);
};

onMounted(() => {
	startTimer();
});

onUnmounted(() => {
	if (timer) {
		clearTimeout(timer);
	}
});

defineExpose({
	close,
	show,
});
</script>

<style scoped></style>
