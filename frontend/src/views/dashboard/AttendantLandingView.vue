<template>
  <div class="max-w-xl mx-auto space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Welcome{{ authStore.user?.full_name ? `, ${authStore.user.full_name}` : '' }}</h1>
      <p class="text-gray-400">Your current shift and pump readings.</p>
    </div>

    <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading your shift...</div>

    <div v-else-if="!shiftContext.shift" class="p-4 rounded-lg border border-yellow-800 bg-yellow-900 bg-opacity-20 text-yellow-200 text-sm">
      No active Shift Assignment found for your account today — ask your manager to assign you a shift.
    </div>

    <template v-else>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-wider text-gray-500">Shift</p>
            <p class="text-lg font-semibold text-white">{{ shiftContext.shift.name }} &middot; {{ shiftContext.shift.shift_type }}</p>
          </div>
          <span
            class="px-3 py-1 rounded-full text-xs font-medium"
            :class="shiftContext.shift.reconciliation_status === 'Closed' ? 'bg-bioluminescent-green bg-opacity-20 text-bioluminescent-green' : 'bg-deepseek-blue bg-opacity-20 text-deepseek-blue'"
          >
            {{ shiftContext.shift.reconciliation_status }}
          </span>
        </div>
        <p class="text-sm text-gray-400">
          {{ shiftContext.open_readings.length }} pump{{ shiftContext.open_readings.length === 1 ? '' : 's' }} currently open
        </p>
      </div>

      <button
        v-if="shiftContext.open_readings.length === 0"
        @click="goToPumpReadings"
        class="w-full px-4 py-4 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-base font-semibold"
      >
        Open a Pump Reading
      </button>
      <button
        v-else
        @click="goToPumpReadings"
        class="w-full px-4 py-4 bg-deepseek-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-base font-semibold"
      >
        Close a Pump Reading
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fuelApi, type MyShiftContext } from '@/api/fuel'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const shiftContext = ref<MyShiftContext>({ employee: null, shift: null, open_readings: [] })

const loadShiftContext = async () => {
  loading.value = true
  try {
    shiftContext.value = await fuelApi.getMyShiftContext()
  } catch (error) {
    // Non-fatal — the page still renders with the "no active shift" state.
  } finally {
    loading.value = false
  }
}

const goToPumpReadings = () => {
  router.push('/fuel/readings')
}

onMounted(loadShiftContext)
</script>
