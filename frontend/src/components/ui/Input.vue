<template>
	<div class="space-y-1.5">
		<!-- Label -->
		<label v-if="label" class="block text-sm font-medium text-gray-300">
			{{ label }}
			<span v-if="required" class="text-danger-500 ml-1">*</span>
		</label>

		<!-- Input wrapper -->
		<div class="relative">
			<!-- Prefix icon -->
			<div
				v-if="$slots.prefix || prefixIcon"
				class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
			>
				<slot name="prefix">
					<component :is="prefixIcon" class="w-5 h-5" />
				</slot>
			</div>

			<!-- Input field -->
			<input
				:value="modelValue"
				:type="type"
				:placeholder="placeholder"
				:disabled="disabled"
				:readonly="readonly"
				:required="required"
				@input="handleInput"
				@change="$emit('change', ($event.target as HTMLInputElement).value)"
				@focus="$emit('focus', $event)"
				@blur="$emit('blur', $event)"
				:class="[
					'w-full px-4 py-2.5 rounded-xl bg-surface-elevated',
					'text-white placeholder-gray-500',
					'focus:outline-none focus:ring-2 focus:ring-offset-0',
					'transition-all duration-200',
					'disabled:opacity-50 disabled:cursor-not-allowed',
					{
						// Error state
						'border border-danger-500 focus:ring-danger-500 focus:border-danger-500':
							error,
						// Disabled state
						'border border-border opacity-50 cursor-not-allowed': disabled,
						// Normal state
						'border border-border focus:ring-primary-500 focus:border-primary-500':
							!error && !disabled,
						// With prefix
						'pl-11': $slots.prefix || prefixIcon,
						// With suffix
						'pr-11': $slots.suffix || suffixIcon || error,
					},
				]"
			/>

			<!-- Suffix icon -->
			<div
				v-if="$slots.suffix || suffixIcon"
				class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
			>
				<slot name="suffix">
					<component :is="suffixIcon" class="w-5 h-5" />
				</slot>
			</div>

			<!-- Error icon -->
			<div v-if="error" class="absolute right-3 top-1/2 -translate-y-1/2">
				<svg
					class="w-5 h-5 text-danger-500"
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
		</div>

		<!-- Error message -->
		<p v-if="error" class="text-sm text-danger-500">{{ error }}</p>

		<!-- Hint text -->
		<p v-if="hint && !error" class="text-sm text-gray-500">{{ hint }}</p>
	</div>
</template>

<script setup lang="ts">
import type { Component } from "vue";

const props = withDefaults(
	defineProps<{
		modelValue?: string | number;
		label?: string;
		type?: "text" | "password" | "email" | "number" | "tel" | "url" | "search" | "date";
		placeholder?: string;
		disabled?: boolean;
		readonly?: boolean;
		required?: boolean;
		error?: string;
		hint?: string;
		prefixIcon?: Component;
		suffixIcon?: Component;
	}>(),
	{
		modelValue: "",
		type: "text",
		disabled: false,
		readonly: false,
		required: false,
		error: "",
		hint: "",
	}
);

const emit = defineEmits(["update:modelValue", "change", "focus", "blur"]);

const handleInput = (event: Event) => {
	const target = event.target as HTMLInputElement;
	emit("update:modelValue", target.value);
};
</script>
