<template>
  <div class="bg-gray-900 border-l-4 rounded-lg p-6" :class="borderColor">
    <p class="text-sm text-gray-400 mb-2">{{ label }}</p>
    <p class="text-3xl font-bold text-white mb-2">{{ formattedValue }}</p>
    <div v-if="change !== null" class="flex items-center gap-1">
      <svg v-if="change >= 0" class="w-4 h-4 text-bioluminescent-green" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
      </svg>
      <svg v-else class="w-4 h-4 text-alert-magenta" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M12 13a1 1 0 110 2H7a1 1 0 01-1-1V9a1 1 0 112 0v3.586l4.293-4.293a1 1 0 011.414 1.414L8.414 13H12z" clip-rule="evenodd" />
      </svg>
      <span :class="change >= 0 ? 'text-bioluminescent-green' : 'text-alert-magenta'" class="text-sm font-medium">
        {{ Math.abs(change) }}% {{ change >= 0 ? 'increase' : 'decrease' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [Number, String],
    required: true,
  },
  type: {
    type: String as () => 'currency' | 'number' | 'text',
    default: 'number',
  },
  change: {
    type: Number,
    default: null,
  },
  variant: {
    type: String as () => 'success' | 'warning' | 'danger' | 'info',
    default: 'info',
  },
})

const formattedValue = computed(() => {
  switch (props.type) {
    case 'currency':
      return `KSh ${Number(props.value).toLocaleString()}`
    case 'number':
      return Number(props.value).toLocaleString()
    default:
      return String(props.value)
  }
})

const borderColor = computed(() => {
  const colors = {
    success: 'border-bioluminescent-green',
    warning: 'border-yellow-500',
    danger: 'border-alert-magenta',
    info: 'border-deepseek-blue',
  }
  return colors[props.variant]
})
</script>

<style scoped>
</style>
