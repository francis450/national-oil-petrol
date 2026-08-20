<template>
	<div>
		<button
			@click="$emit('toggle')"
			:class="[
				'w-full group flex items-center gap-3 px-4 py-3 rounded-xl',
				'text-sm font-medium transition-all duration-200',
				expanded
					? 'bg-surface-elevated text-primary-400'
					: 'text-gray-400 hover:bg-surface hover:text-gray-300',
			]"
		>
			<!-- Icon -->
			<div
				class="w-8 h-8 rounded-xl bg-surface-elevated/50 flex items-center justify-center group-hover:bg-surface-elevated/80 transition-colors"
			>
				<slot name="icon">
					<svg
						class="w-4 h-4 text-gray-400 group-hover:text-primary-400 transition-colors"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</slot>
			</div>

			<span class="flex-1 text-left">{{ label }}</span>

			<!-- Chevron icon -->
			<svg
				class="w-4 h-4 transition-transform duration-200"
				:class="expanded ? 'rotate-90' : 'rotate-0'"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M9 5l7 7-7 7"
				/>
			</svg>
		</button>

		<!-- Submenu items -->
		<transition
			enter-active-class="transition-all duration-200 ease-out"
			leave-active-class="transition-all duration-150 ease-in"
			enter-from-class="opacity-0 max-h-0"
			enter-to-class="opacity-100 max-h-96"
			leave-from-class="opacity-100 max-h-96"
			leave-to-class="opacity-0 max-h-0"
		>
			<div v-if="expanded" class="overflow-hidden pl-4">
				<slot></slot>
			</div>
		</transition>
	</div>
</template>

<script setup lang="ts">
defineProps({
	label: {
		type: String,
		required: true,
	},
	expanded: {
		type: Boolean,
		default: false,
	},
	icon: {
		type: String,
		default: "",
	},
});

defineEmits(["toggle"]);
</script>

<style scoped></style>
