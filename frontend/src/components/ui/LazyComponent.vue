<template>
  <component
    :is="component"
    v-if="loaded"
    v-bind="$attrs"
    v-on="$listeners"
  />
  <div v-else class="flex items-center justify-center min-h-[200px]">
    <slot name="loading">
      <div class="animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent" />
    </slot>
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent, onMounted, watch } from 'vue'

const props = defineProps({
  component: {
    type: [Object, Function],
    required: true,
  },
  loadImmediately: {
    type: Boolean,
    default: false,
  },
  threshold: {
    type: Number,
    default: 0,
  },
})

const loaded = ref(false)
const component = ref<any>(null)

// Load component when needed
const loadComponent = async () => {
  if (loaded.value) return
  
  try {
    // If it's already a component, use it directly
    if (typeof props.component === 'object') {
      component.value = props.component
    } else if (typeof props.component === 'function') {
      // Dynamic import
      component.value = defineAsyncComponent(props.component as () => Promise<any>)
    }
    
    loaded.value = true
  } catch (error) {
    console.error('Failed to load component:', error)
  }
}

// Intersection Observer for lazy loading
const setupIntersectionObserver = () => {
  if (props.loadImmediately) {
    loadComponent()
    return
  }
  
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadComponent()
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: props.threshold }
  )
  
  onMounted(() => {
    const el = document.querySelector('.lazy-component-container')
    if (el) {
      observer.observe(el)
    } else {
      // Fallback: load immediately
      loadComponent()
    }
  })
}

// Watch for immediate load changes
watch(() => props.loadImmediately, (value) => {
  if (value) {
    loadComponent()
  }
})

// Initialize
if (props.loadImmediately) {
  loadComponent()
} else {
  setupIntersectionObserver()
}
</script>

<style scoped>
</style>
