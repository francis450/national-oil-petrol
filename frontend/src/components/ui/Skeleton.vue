<template>
	<div
		:class="[
			'bg-gray-700/50 rounded',
			'animate-pulse',
			{
				'h-4 w-full': variant === 'text',
				'h-10 w-full': variant === 'input',
				'h-32 w-full': variant === 'card',
				'h-8 w-8 rounded-full': variant === 'avatar',
				'h-64 w-full': variant === 'chart',
				'h-6 w-24': variant === 'badge',
				'h-12 w-12 rounded-full': variant === 'icon',
				'h-16 w-full': variant === 'header',
			},
		]"
	/>
</template>

<script setup lang="ts">
withDefaults(
	defineProps<{
		variant?: "text" | "input" | "card" | "avatar" | "chart" | "badge" | "icon" | "header";
	}>(),
	{
		variant: "text",
	}
);
</script>
