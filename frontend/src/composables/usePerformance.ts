import { ref, onMounted, onUnmounted, type Ref } from 'vue'

/**
 * Debounce a function call
 */
export function useDebounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    timeoutId = setTimeout(() => {
      func(...args)
    }, delay)
  }
}

/**
 * Throttle a function call
 */
export function useThrottle<T extends (...args: any[]) => any>(
  func: T,
  limit: number = 100
): (...args: Parameters<T>) => void {
  let inThrottle = false
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * Track component mount time for performance monitoring
 */
export function useMountTime() {
  const mountTime = ref<number | null>(null)
  const startTime = performance.now()
  
  onMounted(() => {
    mountTime.value = performance.now() - startTime
  })
  
  return { mountTime }
}

/**
 * Lazy load images with Intersection Observer
 */
export function useLazyImage(imgRef: Ref<HTMLImageElement | null>) {
  const loaded = ref(false)
  const error = ref(false)
  
  const loadImage = () => {
    if (!imgRef.value) return
    
    const img = imgRef.value
    const src = img.dataset.src
    const srcset = img.dataset.srcset
    
    if (!src) return
    
    img.src = src
    if (srcset) {
      img.srcset = srcset
    }
    
    img.addEventListener('load', () => {
      loaded.value = true
    })
    
    img.addEventListener('error', () => {
      error.value = true
    })
  }
  
  const setupObserver = () => {
    if (!imgRef.value) return
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.1 }
    )
    
    observer.observe(imgRef.value)
    
    onUnmounted(() => {
      observer.disconnect()
    })
  }
  
  onMounted(setupObserver)
  
  return { loaded, error }
}

/**
 * Virtual scrolling for large lists
 */
export function useVirtualScroll<T>(
  items: Ref<T[]>,
  itemHeight: number = 50,
  buffer: number = 5
) {
  const visibleItems = ref<T[]>([])
  const scrollTop = ref(0)
  const containerHeight = ref(0)
  
  const updateVisibleItems = () => {
    const startIndex = Math.max(0, Math.floor(scrollTop.value / itemHeight) - buffer)
    const endIndex = Math.min(
      items.value.length,
      Math.ceil((scrollTop.value + containerHeight.value) / itemHeight) + buffer
    )
    
    visibleItems.value = items.value.slice(startIndex, endIndex)
  }
  
  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    scrollTop.value = target.scrollTop
    containerHeight.value = target.clientHeight
    updateVisibleItems()
  }
  
  // Initialize
  updateVisibleItems()
  
  return {
    visibleItems,
    scrollTop,
    containerHeight,
    handleScroll,
    updateVisibleItems,
  }
}

/**
 * Memoize expensive computations
 */
export function useMemoize<T extends (...args: any[]) => any>(func: T): T {
  const cache = new Map<string, ReturnType<T>>()
  
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args)
    
    if (cache.has(key)) {
      return cache.get(key)!
    }
    
    const result = func(...args)
    cache.set(key, result)
    
    return result
  }) as T
}

/**
 * Preload resources (images, scripts, etc.)
 */
export function usePreload() {
  const preloadImage = (url: string) => {
    const img = new Image()
    img.src = url
  }
  
  const preloadScript = (url: string) => {
    const script = document.createElement('script')
    script.src = url
    script.async = true
    document.body.appendChild(script)
  }
  
  const preloadLink = (url: string, as: 'style' | 'script' | 'font' | 'image' = 'style') => {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = url
    link.as = as
    document.head.appendChild(link)
  }
  
  return {
    preloadImage,
    preloadScript,
    preloadLink,
  }
}

/**
 * Check if user prefers reduced motion
 */
export function useReducedMotion() {
  const reducedMotion = ref(false)
  
  onMounted(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    reducedMotion.value = mediaQuery.matches
    
    mediaQuery.addEventListener('change', (e) => {
      reducedMotion.value = e.matches
    })
  })
  
  return { reducedMotion }
}
