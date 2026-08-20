<template>
  <transition
    enter-active-class="transition-all duration-300 ease-out"
    leave-active-class="transition-all duration-200 ease-in"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
    @after-enter="focusFirstElement"
  >
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      @click.self="closeOnBackdrop ? close() : null"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      
      <!-- Modal Container -->
      <div
        class="relative w-full max-w-lg bg-surface-elevated rounded-2xl shadow-xl animate-slide-up"
        :class="sizeClasses"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        :aria-describedby="description ? 'modal-description' : undefined"
      >
        <!-- Header -->
        <div v-if="title || $slots.header" class="flex items-center justify-between p-6 border-b border-border">
          <div class="flex items-center gap-3">
            <slot name="icon">
              <div v-if="iconVariant" class="w-8 h-8 rounded-xl flex items-center justify-center" :class="iconBackground">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </slot>
            <h2 id="modal-title" class="text-xl font-bold text-white">{{ title }}</h2>
          </div>
          
          <!-- Close Button -->
          <button
            @click="close"
            class="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-surface transition-colors"
            aria-label="Close modal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Content -->
        <div class="p-6" :id="description ? 'modal-description' : undefined">
          <p v-if="description" class="text-sm text-gray-400 mb-4">{{ description }}</p>
          <slot />
        </div>
        
        <!-- Footer -->
        <div v-if="$slots.footer" class="flex items-center justify-end gap-3 p-6 border-t border-border">
          <slot name="footer">
            <Button variant="secondary" @click="close">
              Cancel
            </Button>
            <Button variant="primary" @click="$emit('confirm')">
              Confirm
            </Button>
          </slot>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import Button from './Button.vue'

const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
  description?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
  iconVariant?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}>(), {
  modelValue: false,
  size: 'md',
  closeOnBackdrop: true,
  closeOnEscape: true,
})

const emit = defineEmits(['update:modelValue', 'close', 'confirm'])

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-4xl',
  }
  return sizes[props.size] || sizes.md
})

const iconBackground = computed(() => {
  const colors = {
    primary: 'bg-primary-600',
    success: 'bg-success-600',
    warning: 'bg-warning-600',
    danger: 'bg-danger-600',
    info: 'bg-info-600',
  }
  return colors[props.iconVariant || 'primary']
})

// Focus first focusable element on open
const focusFirstElement = () => {
  nextTick(() => {
    const modal = document.querySelector('[role="dialog"]')
    if (modal) {
      const focusableElements = modal.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      if (focusableElements.length > 0) {
        focusableElements[0].focus()
      }
    }
  })
}

// Close on escape key
const handleEscape = (event: KeyboardEvent) => {
  if (props.closeOnEscape && event.key === 'Escape') {
    close()
  }
}

watch(() => props.modelValue, (value) => {
  if (value) {
    document.addEventListener('keydown', handleEscape)
    document.body.style.overflow = 'hidden'
  } else {
    document.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
  }
})

defineExpose({
  close,
})
</script>

<style scoped>
</style>
