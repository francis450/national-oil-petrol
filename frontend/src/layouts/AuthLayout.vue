<template>
  <div class="min-h-screen bg-chronos-black flex items-center justify-center px-6">
    <div class="w-full max-w-md">
      <div class="card mb-8 text-center">
        <h1 class="text-4xl font-bold text-deepseek-blue mb-2">National Oil</h1>
        <p class="text-gray-400">Petrol Station Management System</p>
      </div>

      <form @submit.prevent="handleLogin" class="card space-y-4">
        <h2 class="text-2xl font-bold mb-6 text-white">Sign In</h2>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Username</label>
          <input
            v-model="username"
            type="text"
            class="input-field"
            placeholder="Enter your username"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Password</label>
          <input
            v-model="password"
            type="password"
            class="input-field"
            placeholder="Enter your password"
            required
          />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>

        <div v-if="error" class="p-4 bg-red-900 border border-red-700 rounded text-red-200">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  const success = await authStore.login(username.value, password.value)

  if (success) {
    router.push('/')
  } else {
    error.value = 'Invalid username or password'
  }

  loading.value = false
}
</script>

<style scoped>
</style>
