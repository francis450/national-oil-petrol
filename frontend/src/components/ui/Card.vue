<template>
	<div
		:class="[
			'bg-surface-elevated border border-border rounded-2xl',
			'shadow-soft transition-all duration-200',
			{
				'p-4': padding === 'sm',
				'p-6': padding === 'md',
				'p-8': padding === 'lg',
				'hover:shadow-lg hover:border-border-subtle': hoverable,
				'border-0': noBorder,
			},
		]"
	>
		<!-- Header slot -->
		<div v-if="$slots.header || title" class="mb-4">
			<slot name="header">
				<div class="flex items-center justify-between">
					<h3 v-if="title" class="text-lg font-semibold text-white">{{ title }}</h3>
					<slot name="header-actions" />
				</div>
			</slot>
		</div>

		<!-- Default content -->
		<slot />

		<!-- Footer slot -->
		<div v-if="$slots.footer" class="mt-4 pt-4 border-t border-border">
			<slot name="footer" />
		</div>
	</div>
</template>

<script setup lang="ts">
withDefaults(
	defineProps<{
		title?: string;
		padding?: "sm" | "md" | "lg";
		hoverable?: boolean;
		noBorder?: boolean;
	}>(),
	{
		padding: "md",
		hoverable: false,
		noBorder: false,
	}
);
</script>
