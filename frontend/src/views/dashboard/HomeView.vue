<template>
  <AttendantLandingView v-if="isPumpAttendantOnly" />
  <DashboardView v-else />
</template>

<script setup lang="ts">
import { usePermissions } from '@/composables/usePermissions'
import DashboardView from './DashboardView.vue'
import AttendantLandingView from './AttendantLandingView.vue'

const { isPumpAttendantOnly } = usePermissions()
</script>
