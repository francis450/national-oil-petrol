<template>
	<span
		:class="[
			'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium',
			'transition-colors duration-200',
			{
				// Primary variants
				'bg-primary-600/10 text-primary-400 border border-primary-600/20':
					variant === 'primary' && !dot,
				'bg-primary-600 text-white': variant === 'primary' && dot,

				// Success variants
				'bg-success-600/10 text-success-400 border border-success-600/20':
					variant === 'success' && !dot,
				'bg-success-600 text-white': variant === 'success' && dot,

				// Danger variants
				'bg-danger-600/10 text-danger-400 border border-danger-600/20':
					variant === 'danger' && !dot,
				'bg-danger-600 text-white': variant === 'danger' && dot,

				// Warning variants
				'bg-warning-600/10 text-warning-400 border border-warning-600/20':
					variant === 'warning' && !dot,
				'bg-warning-600 text-white': variant === 'warning' && dot,

				// Info variants
				'bg-info-600/10 text-info-400 border border-info-600/20':
					variant === 'info' && !dot,
				'bg-info-600 text-white': variant === 'info' && dot,

				// Secondary variants
				'bg-surface-elevated text-gray-400 border border-border':
					variant === 'secondary' && !dot,
				'bg-gray-600 text-white': variant === 'secondary' && dot,

				// Dot style
				'w-2 h-2 rounded-full': dot,
			},
		]"
	>
		<slot v-if="!dot" />
	</span>
</template>

<script setup lang="ts">
withDefaults(
	defineProps<{
		variant?: "primary" | "success" | "danger" | "warning" | "info" | "secondary";
		dot?: boolean;
	}>(),
	{
		variant: "secondary",
		dot: false,
	}
);
</script>
