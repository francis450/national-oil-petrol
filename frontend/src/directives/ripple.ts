import type { Directive, DirectiveBinding } from 'vue'

interface RippleElement extends HTMLElement {
  ripple?: HTMLSpanElement
  rippleTimeout?: ReturnType<typeof setTimeout>
}

const createRipple = (el: RippleElement, binding: DirectiveBinding) => {
  // Remove existing ripple if any
  if (el.ripple) {
    el.ripple.remove()
  }
  
  // Create ripple element
  const ripple = document.createElement('span')
  ripple.className = 'ripple-effect'
  
  // Apply custom color if provided
  const color = (binding.value as string) || 'rgba(255, 255, 255, 0.3)'
  ripple.style.backgroundColor = color
  
  // Get click position
  const rect = el.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = rect.left + rect.width / 2
  const y = rect.top + rect.height / 2
  
  // Position and style ripple
  ripple.style.width = ripple.style.height = `${size}px`
  ripple.style.left = `${x - size / 2}px`
  ripple.style.top = `${y - size / 2}px`
  ripple.style.transform = 'translate(-50%, -50%) scale(0)'
  
  // Add to DOM
  el.appendChild(ripple)
  el.ripple = ripple
  
  // Animate
  setTimeout(() => {
    ripple.style.transform = 'translate(-50%, -50%) scale(1)'
    ripple.style.opacity = '0'
  }, 10)
  
  // Remove after animation
  el.rippleTimeout = setTimeout(() => {
    ripple.remove()
    el.ripple = undefined
  }, 600)
}

export const ripple: Directive = {
  mounted(el: RippleElement, binding: DirectiveBinding) {
    // Add ripple container styles
    el.classList.add('relative', 'overflow-hidden')
    
    // Handle click
    el.addEventListener('click', (e) => {
      // Only trigger on left mouse button
      if (e.button !== 0) return
      
      // Get click position relative to element
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const size = Math.max(rect.width, rect.height)
      
      // Create ripple at click position
      const ripple = document.createElement('span')
      ripple.className = 'ripple-effect'
      
      // Apply custom color if provided
      const color = (binding.value as string) || 'rgba(255, 255, 255, 0.3)'
      ripple.style.backgroundColor = color
      
      // Position and style ripple
      ripple.style.width = ripple.style.height = `${size}px`
      ripple.style.left = `${x}px`
      ripple.style.top = `${y}px`
      ripple.style.transform = 'translate(-50%, -50%) scale(0)'
      
      // Add to DOM
      el.appendChild(ripple)
      el.ripple = ripple
      
      // Animate
      setTimeout(() => {
        ripple.style.transform = 'translate(-50%, -50%) scale(1)'
        ripple.style.opacity = '0'
      }, 10)
      
      // Remove after animation
      el.rippleTimeout = setTimeout(() => {
        ripple.remove()
        el.ripple = undefined
      }, 600)
    })
  },
  
  unmounted(el: RippleElement) {
    // Cleanup
    if (el.ripple) {
      el.ripple.remove()
    }
    if (el.rippleTimeout) {
      clearTimeout(el.rippleTimeout)
    }
  },
}

// Add global styles for ripple effect
export const rippleStyles = `
.ripple-effect {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%);
  transition: transform 0.6s ease, opacity 0.6s ease;
  z-index: 1;
}
`
