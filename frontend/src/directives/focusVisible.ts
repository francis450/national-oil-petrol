import type { Directive } from 'vue'

// Add focus-visible styles globally
const focusVisibleStyles = `
.focus-visible,
:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Remove default focus outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Custom focus styles for dark mode */
.dark .focus-visible,
.dark :focus-visible {
  outline-color: #60a5fa;
}
`

// Directive to add focus-visible class on keyboard focus
export const focusVisible: Directive = {
  mounted(el) {
    el.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        el.classList.add('keyboard-focused')
      }
    })
    
    el.addEventListener('mousedown', () => {
      el.classList.remove('keyboard-focused')
    })
  },
  unmounted(el) {
    el.removeEventListener('keydown', () => {})
    el.removeEventListener('mousedown', () => {})
  },
}

export { focusVisibleStyles }
