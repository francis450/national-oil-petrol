<template>
  <div class="h-screen bg-chronos-black">
    <!-- App Layout (for authenticated routes) -->
    <AppLayout v-if="currentLayout === 'app'">
      <RouterView />
    </AppLayout>

    <!-- Auth Layout (for login page) -->
    <AuthLayout v-else-if="currentLayout === 'auth'">
      <RouterView />
    </AuthLayout>

    <!-- Fallback (shouldn't normally show) -->
    <RouterView v-else />
  </div>
</template>

<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const route = useRoute()
const authStore = useAuthStore()

const currentLayout = computed(() => {
  return (route.meta.layout as string) || 'app'
})

onMounted(() => {
  authStore.checkExistingSession()
})
</script>

<style scoped>
</style>
