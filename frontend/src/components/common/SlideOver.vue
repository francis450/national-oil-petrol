<template>
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 z-50 flex justify-end">
      <div class="absolute inset-0 bg-black/60" @click="close" />
      <div class="relative w-full max-w-lg bg-gray-900 border-l border-gray-800 shadow-2xl flex flex-col h-full slideover-panel">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800 shrink-0">
          <h2 class="text-lg font-semibold text-white">{{ title }}</h2>
          <button @click="close" class="p-1 text-gray-400 hover:text-white rounded transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-5">
          <slot />
        </div>
        <div class="px-6 py-4 border-t border-gray-800 flex items-center justify-end gap-3 shrink-0">
          <slot name="footer">
            <button @click="close" class="px-4 py-2 text-sm text-gray-300 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors">
              Close
            </button>
          </slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{ modelValue: boolean; title: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()
const close = () => emit('update:modelValue', false)
</script>

<style scoped>
.slideover-panel {
  animation: slide-in 0.2s ease-out;
}
@keyframes slide-in {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
