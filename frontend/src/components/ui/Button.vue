<template>
  <button
    v-ripple="rippleColor"
    :class="[
      'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl',
      'font-medium transition-all duration-200 ease-in-out',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface',
      'disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden',
      {
        // Primary variant
        'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800': 
          variant === 'primary' && !disabled,
        'focus:ring-primary-500': variant === 'primary' && !disabled,
        
        // Success variant
        'bg-success-600 text-white hover:bg-success-700 active:bg-success-800': 
          variant === 'success' && !disabled,
        'focus:ring-success-500': variant === 'success' && !disabled,
        
        // Danger variant
        'bg-danger-600 text-white hover:bg-danger-700 active:bg-danger-800': 
          variant === 'danger' && !disabled,
        'focus:ring-danger-500': variant === 'danger' && !disabled,
        
        // Warning variant
        'bg-warning-600 text-white hover:bg-warning-700 active:bg-warning-800': 
          variant === 'warning' && !disabled,
        'focus:ring-warning-500': variant === 'warning' && !disabled,
        
        // Secondary variant
        'bg-surface-elevated text-gray-300 border border-border hover:bg-surface active:bg-surface-elevated': 
          variant === 'secondary' && !disabled,
        'focus:ring-border': variant === 'secondary' && !disabled,
        
        // Ghost variant
        'bg-transparent text-gray-300 hover:text-white hover:bg-surface-elevated/50 active:bg-surface-elevated/80': 
          variant === 'ghost' && !disabled,
        'focus:ring-gray-500': variant === 'ghost' && !disabled,
        
        // Size variants
        'px-3 py-1.5 text-sm': size === 'sm',
        'px-4 py-2 text-base': size === 'md',
        'px-6 py-3 text-lg': size === 'lg',
        
        // Full width
        'w-full': fullWidth,
        
        // Loading state
        'opacity-70 cursor-wait': loading,
      }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <!-- Loading spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-5 w-5"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
    
    <!-- Icon slot -->
    <slot v-else name="icon" />
    
    <!-- Text content -->
    <span>
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'primary' | 'success' | 'danger' | 'warning' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  noRipple?: boolean
}>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  fullWidth: false,
  noRipple: false,
})

const emit = defineEmits(['click'])

// Compute ripple color based on variant
const rippleColor = computed(() => {
  if (props.noRipple) return ''
  
  const colors = {
    primary: 'rgba(255, 255, 255, 0.3)',
    success: 'rgba(255, 255, 255, 0.3)',
    danger: 'rgba(255, 255, 255, 0.3)',
    warning: 'rgba(255, 255, 255, 0.3)',
    secondary: 'rgba(255, 255, 255, 0.1)',
    ghost: 'rgba(255, 255, 255, 0.1)',
  }
  
  return colors[props.variant] || colors.primary
})
</script>

<style scoped>
</style>
