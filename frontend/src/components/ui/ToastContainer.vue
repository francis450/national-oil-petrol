<template>
	<div class="fixed top-0 right-0 z-50 p-4 space-y-3 pointer-events-none">
		<Toast
			v-for="toast in toasts"
			:key="toast.id"
			v-bind="toast"
			@close="removeToast(toast.id)"
			@dismissed="removeToast(toast.id)"
			class="pointer-events-auto"
		/>
	</div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useToastStore } from "@/stores/toast";
import Toast from "./Toast.vue";

const toastStore = useToastStore();

const toasts = computed(() => toastStore.toasts);

const removeToast = (id: string) => {
	toastStore.removeToast(id);
};
</script>

<style scoped></style>
