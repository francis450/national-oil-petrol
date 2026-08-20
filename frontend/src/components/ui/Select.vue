<template>
	<div class="space-y-1.5">
		<!-- Label -->
		<label v-if="label" class="block text-sm font-medium text-gray-300">
			{{ label }}
			<span v-if="required" class="text-danger-500 ml-1">*</span>
		</label>

		<!-- Select wrapper -->
		<div class="relative">
			<select
				:value="modelValue"
				:disabled="disabled"
				:required="required"
				@change="handleChange"
				@focus="$emit('focus', $event)"
				@blur="$emit('blur', $event)"
				:class="[
					'w-full px-4 py-2.5 rounded-xl bg-surface-elevated',
					'text-white appearance-none',
					'focus:outline-none focus:ring-2 focus:ring-offset-0',
					'transition-all duration-200',
					'disabled:opacity-50 disabled:cursor-not-allowed',
					{
						'border border-danger-500 focus:ring-danger-500 focus:border-danger-500':
							error,
						'border border-border focus:ring-primary-500 focus:border-primary-500':
							!error && !disabled,
						'border border-border opacity-50 cursor-not-allowed': disabled,
					},
				]"
			>
				<!-- Placeholder option -->
				<option v-if="placeholder" value="" disabled selected class="text-gray-500">
					{{ placeholder }}
				</option>

				<!-- Options -->
				<option
					v-for="option in options"
					:key="option.value"
					:value="option.value"
					class="bg-surface-elevated text-gray-300"
				>
					{{ option.label }}
				</option>
			</select>

			<!-- Chevron icon -->
			<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
				<svg
					class="w-5 h-5 text-gray-400"
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
interface SelectOption {
	value: string | number;
	label: string;
}

const props = withDefaults(
	defineProps<{
		modelValue?: string | number;
		label?: string;
		options?: SelectOption[];
		placeholder?: string;
		disabled?: boolean;
		required?: boolean;
		error?: string;
		hint?: string;
	}>(),
	{
		modelValue: "",
		options: () => [],
		disabled: false,
		required: false,
		error: "",
		hint: "",
	}
);

const emit = defineEmits(["update:modelValue", "change", "focus", "blur"]);

const handleChange = (event: Event) => {
	const target = event.target as HTMLSelectElement;
	emit("update:modelValue", target.value);
	emit("change", target.value);
};
</script>
