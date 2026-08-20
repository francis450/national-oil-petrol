import { ref, onMounted, onUnmounted, type Ref } from 'vue'

interface KeyboardNavigationOptions {
  items: Ref<HTMLElement[]>
  activeIndex: Ref<number>
  loop?: boolean
  vertical?: boolean
  onSelect?: (index: number) => void
}

export function useKeyboardNavigation(options: KeyboardNavigationOptions) {
  const { items, activeIndex, loop = true, vertical = true, onSelect } = options

  const handleKeydown = (event: KeyboardEvent) => {
    const currentIndex = activeIndex.value
    const totalItems = items.value.length
    
    if (totalItems === 0) return
    
    let newIndex: number | null = null
    
    if (vertical) {
      // Vertical navigation (up/down arrows)
      if (event.key === 'ArrowDown') {
        newIndex = loop ? (currentIndex + 1) % totalItems : Math.min(currentIndex + 1, totalItems - 1)
      } else if (event.key === 'ArrowUp') {
        newIndex = loop ? (currentIndex - 1 + totalItems) % totalItems : Math.max(currentIndex - 1, 0)
      }
    } else {
      // Horizontal navigation (left/right arrows)
      if (event.key === 'ArrowRight') {
        newIndex = loop ? (currentIndex + 1) % totalItems : Math.min(currentIndex + 1, totalItems - 1)
      } else if (event.key === 'ArrowLeft') {
        newIndex = loop ? (currentIndex - 1 + totalItems) % totalItems : Math.max(currentIndex - 1, 0)
      }
    }
    
    // Enter/space for selection
    if (newIndex !== null && (event.key === 'Enter' || event.key === ' ')) {
      if (onSelect) {
        event.preventDefault()
        onSelect(newIndex)
      }
      return
    }
    
    // Update active index
    if (newIndex !== null) {
      event.preventDefault()
      activeIndex.value = newIndex
      
      // Focus the new active item
      nextTick(() => {
        const newItem = items.value[newIndex]
        if (newItem) {
          newItem.focus()
          newItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        }
      })
    }
    
    // Escape to close/clear
    if (event.key === 'Escape') {
      activeIndex.value = -1
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}

// Helper for tab trap (useful for modals)
export function useTabTrap(active: Ref<boolean>, firstElement: Ref<HTMLElement | null>, lastElement: Ref<HTMLElement | null>) {
  const handleKeydown = (event: KeyboardEvent) => {
    if (!active.value) return
    
    if (event.key === 'Tab') {
      const first = firstElement.value
      const last = lastElement.value
      
      if (!first || !last) return
      
      if (event.shiftKey && document.activeElement === first) {
        // Shift+Tab from first element: focus last
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        // Tab from last element: focus first
        event.preventDefault()
        first.focus()
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}

// Helper for skip links (accessibility)
export function useSkipLink(targetId: string) {
  const skipLink = ref<HTMLElement | null>(null)
  
  const handleClick = (event: Event) => {
    event.preventDefault()
    const target = document.getElementById(targetId)
    if (target) {
      target.setAttribute('tabindex', '-1')
      target.focus()
      target.removeAttribute('tabindex')
    }
  }
  
  return {
    skipLink,
    handleClick,
  }
}
