<template>
  <div class="bg-gray-900 border border-gray-800 rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <span class="flex-1">{{ title }}</span>
      <div v-if="legend" class="flex gap-4 text-xs">
        <div v-for="(item, idx) in legend" :key="idx" class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full" :class="item.color"></div>
          <span class="text-gray-400">{{ item.label }}</span>
        </div>
      </div>
    </h3>

    <!-- Simple Bar Chart (visual approximation) -->
    <div v-if="type === 'bar'" class="space-y-3">
      <div v-for="(item, idx) in data" :key="idx" class="space-y-1">
        <div class="flex justify-between text-xs">
          <span class="text-gray-400">{{ item.label }}</span>
          <span class="text-white font-medium">{{ item.value.toLocaleString() }}</span>
        </div>
        <div class="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="item.color || 'bg-deepseek-blue'"
            :style="{ width: ((item.value / (maxValue || 1)) * 100) + '%' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Simple Line Chart (ascii-like) -->
    <div v-if="type === 'line'" class="text-center py-12">
      <svg class="w-full h-40 text-deepseek-blue opacity-50" viewBox="0 0 400 150">
        <polyline
          :points="chartPoints"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          vector-effect="non-scaling-stroke"
        />
      </svg>
      <p class="text-xs text-gray-500 mt-2">{{ subtitle }}</p>
    </div>

    <!-- Simple Pie/Donut Chart -->
    <div v-if="type === 'pie'" class="flex items-center justify-center py-8">
      <div class="relative w-32 h-32">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            v-for="(item, idx) in getPieSegments()"
            :key="idx"
            cx="50"
            cy="50"
            r="40"
            :fill="'none'"
            :stroke="item.color"
            :stroke-width="item.strokeWidth"
            :stroke-dasharray="item.dasharray"
            :stroke-dashoffset="item.offset"
            stroke-linecap="round"
          />
        </svg>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center">
            <p class="text-2xl font-bold text-white">{{ total }}</p>
            <p class="text-xs text-gray-400">Total</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ChartData {
  label: string
  value: number
  color?: string
}

interface LegendItem {
  label: string
  color: string
}

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  type: {
    type: String as () => 'bar' | 'line' | 'pie',
    default: 'bar',
  },
  data: {
    type: Array as () => ChartData[],
    required: true,
  },
  legend: {
    type: Array as () => LegendItem[],
    default: null,
  },
  subtitle: {
    type: String,
    default: 'Chart visualization',
  },
})

const maxValue = computed(() => {
  return Math.max(...props.data.map(d => d.value))
})

const total = computed(() => {
  return props.data.reduce((sum, item) => sum + item.value, 0)
})

const colors = [
  'bg-deepseek-blue',
  'bg-bioluminescent-green',
  'bg-yellow-500',
  'bg-pink-500',
  'bg-purple-500',
]

const chartPoints = computed(() => {
  const width = 400
  const height = 150
  const padding = 20
  const pointWidth = (width - padding * 2) / (props.data.length - 1)
  
  return props.data.map((item, idx) => {
    const x = padding + idx * pointWidth
    const y = height - padding - (item.value / (maxValue.value || 1)) * (height - padding * 2)
    return `${x},${y}`
  }).join(' ')
})

const getPieSegments = () => {
  if (props.type !== 'pie') return []
  
  const radius = 40
  const circumference = 2 * Math.PI * radius
  let offset = 0
  
  return props.data.map((item, idx) => {
    const percentage = item.value / total.value
    const strokeWidth = circumference * percentage
    const currentOffset = offset
    offset += strokeWidth
    
    return {
      color: colors[idx % colors.length],
      strokeWidth: Math.max(8, circumference * percentage),
      dasharray: `${strokeWidth} ${circumference}`,
      offset: -currentOffset,
    }
  })
}
</script>

<style scoped>
</style>
