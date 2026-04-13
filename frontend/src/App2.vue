<template>
  <component :is="layout" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const route = useRoute()

const layout = computed(() => {
  const layoutName = route.meta.layout as string || 'app'
  return layoutName === 'auth' ? AuthLayout : AppLayout
})
</script>
