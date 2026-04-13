<template>
  <div>
    <button
      @click="$emit('toggle')"
      :class="[
        'w-full group flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
        expanded 
          ? 'bg-gray-800 text-deepseek-blue' 
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-300'
      ]"
    >
      <svg 
        v-if="expanded"
        class="w-5 h-5 mr-3 transition-transform" 
        fill="currentColor" 
        viewBox="0 0 20 20"
      >
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
      <svg 
        v-else
        class="w-5 h-5 mr-3 transition-transform" 
        fill="currentColor" 
        viewBox="0 0 20 20"
      >
        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
      </svg>
      {{ label }}
    </button>

    <!-- Submenu items -->
    <transition
      enter-active-class="transition-all duration-200"
      leave-active-class="transition-all duration-150"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-96"
      leave-from-class="opacity-100 max-h-96"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="expanded" class="overflow-hidden">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
defineProps({
  label: {
    type: String,
    required: true,
  },
  expanded: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle'])
</script>

<style scoped>
</style>
