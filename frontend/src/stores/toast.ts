import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Toast {
  id: string
  message: string
  subtitle?: string
  variant: 'info' | 'success' | 'warning' | 'error'
  duration?: number
  persistent?: boolean
}

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<Toast[]>([])
  let toastId = 0

  /**
   * Show a toast notification
   */
  const showToast = (
    message: string,
    options?: Partial<Omit<Toast, 'id' | 'message'>>
  ) => {
    const id = `toast-${toastId++}`
    
    const toast: Toast = {
      id,
      message,
      variant: 'info',
      duration: 5000,
      persistent: false,
      ...options,
    }
    
    toasts.value.push(toast)
    
    // Auto-remove if not persistent
    if (!toast.persistent) {
      setTimeout(() => {
        removeToast(id)
      }, toast.duration)
    }
    
    return id
  }

  /**
   * Show success toast
   */
  const success = (
    message: string,
    options?: Partial<Omit<Toast, 'id' | 'message' | 'variant'>>
  ) => {
    return showToast(message, { variant: 'success', ...options })
  }

  /**
   * Show error toast
   */
  const error = (
    message: string,
    options?: Partial<Omit<Toast, 'id' | 'message' | 'variant'>>
  ) => {
    return showToast(message, { variant: 'error', ...options })
  }

  /**
   * Show warning toast
   */
  const warning = (
    message: string,
    options?: Partial<Omit<Toast, 'id' | 'message' | 'variant'>>
  ) => {
    return showToast(message, { variant: 'warning', ...options })
  }

  /**
   * Show info toast
   */
  const info = (
    message: string,
    options?: Partial<Omit<Toast, 'id' | 'message' | 'variant'>>
  ) => {
    return showToast(message, { variant: 'info', ...options })
  }

  /**
   * Remove a toast by ID
   */
  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  /**
   * Clear all toasts
   */
  const clearAll = () => {
    toasts.value = []
  }

  return {
    toasts,
    showToast,
    success,
    error,
    warning,
    info,
    removeToast,
    clearAll,
  }
})
