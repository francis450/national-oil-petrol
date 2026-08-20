<template>
  <div class="space-y-1.5">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-300">
      {{ label }}
      <span v-if="required" class="text-danger-500 ml-1">*</span>
    </label>
    
    <!-- Date Picker Wrapper -->
    <div class="relative">
      <!-- Input Field -->
      <input
        :value="formattedDate"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="true"
        @click="toggleCalendar"
        :class="[
          'w-full px-4 py-2.5 rounded-xl bg-surface-elevated',
          'text-white placeholder-gray-500 cursor-pointer',
          'focus:outline-none focus:ring-2 focus:ring-offset-0',
          'transition-all duration-200',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error ? 'border border-danger-500 focus:ring-danger-500 focus:border-danger-500' :
          'border border-border focus:ring-primary-500 focus:border-primary-500'
        ]"
      />
      
      <!-- Calendar Icon -->
      <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      
      <!-- Calendar Dropdown -->
      <transition
        enter-active-class="transition-all duration-200 ease-out"
        leave-active-class="transition-all duration-150 ease-in"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showCalendar"
          class="absolute top-full left-0 mt-2 z-50 bg-surface-elevated rounded-xl shadow-lg border border-border p-4"
          @click.stop
        >
          <!-- Calendar Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-4">
              <button @click="prevMonth" class="p-1 rounded-lg hover:bg-surface transition-colors">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h3 class="text-lg font-semibold text-white">{{ currentMonthYear }}</h3>
              <button @click="nextMonth" class="p-1 rounded-lg hover:bg-surface transition-colors">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
            <button @click="closeCalendar" class="p-1 rounded-lg hover:bg-surface transition-colors">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Weekdays -->
          <div class="grid grid-cols-7 gap-1 mb-2">
            <div v-for="day in weekdays" :key="day" class="text-center text-xs text-gray-500 font-medium py-1">
              {{ day }}
            </div>
          </div>
          
          <!-- Days -->
          <div class="grid grid-cols-7 gap-1">
            <button
              v-for="day in days"
              :key="day.date"
              @click="selectDate(day)"
              :disabled="day.disabled"
              :class="[
                'aspect-square rounded-lg text-sm transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-primary-500',
                {
                  'bg-primary-600 text-white': day.selected,
                  'bg-surface hover:bg-surface-elevated text-gray-300': !day.selected && !day.disabled,
                  'text-gray-600 cursor-not-allowed': day.disabled,
                  'today border-2 border-primary-500': day.today && !day.selected,
                }
              ]"
            >
              {{ day.day }}
            </button>
          </div>
          
          <!-- Quick Actions -->
          <div class="flex gap-2 mt-4">
            <Button variant="ghost" size="sm" @click="selectToday" class="flex-1">
              Today
            </Button>
            <Button variant="ghost" size="sm" @click="clearDate" class="flex-1">
              Clear
            </Button>
          </div>
        </div>
      </transition>
    </div>
    
    <!-- Error message -->
    <p v-if="error" class="text-sm text-danger-500">{{ error }}</p>
    
    <!-- Hint text -->
    <p v-if="hint && !error" class="text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import Button from './Button.vue'

const props = withDefaults(defineProps<{
  modelValue?: Date | string | null
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: string
  hint?: string
  minDate?: Date | string
  maxDate?: Date | string
}>(), {
  modelValue: null,
  placeholder: 'Select a date',
  disabled: false,
  required: false,
})

const emit = defineEmits(['update:modelValue'])

const showCalendar = ref(false)
const currentDate = ref<Date>(new Date())
const selectedDate = ref<Date | null>(null)

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { 
    month: 'long', 
    year: 'numeric' 
  })
})

const formattedDate = computed(() => {
  if (!selectedDate.value) return ''
  return selectedDate.value.toLocaleDateString('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
})

// Parse min and max dates
const minDate = computed(() => {
  if (!props.minDate) return null
  return props.minDate instanceof Date ? props.minDate : new Date(props.minDate)
})

const maxDate = computed(() => {
  if (!props.maxDate) return null
  return props.maxDate instanceof Date ? props.maxDate : new Date(props.maxDate)
})

// Generate calendar days
const days = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDay = firstDay.getDay()
  const totalDays = lastDay.getDate()
  
  const daysArray: Array<{
    day: number
    date: Date
    selected: boolean
    today: boolean
    disabled: boolean
  }> = []
  
  // Previous month days
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    daysArray.push({
      day: prevMonthLastDay - i,
      date: new Date(year, month - 1, prevMonthLastDay - i),
      selected: false,
      today: false,
      disabled: true,
    })
  }
  
  // Current month days
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  for (let day = 1; day <= totalDays; day++) {
    const date = new Date(year, month, day)
    const isToday = date.getTime() === today.getTime()
    const isSelected = selectedDate.value && date.getTime() === selectedDate.value.getTime()
    
    // Check if date is within min/max range
    let isDisabled = false
    if (minDate.value && date < minDate.value) {
      isDisabled = true
    }
    if (maxDate.value && date > maxDate.value) {
      isDisabled = true
    }
    
    daysArray.push({
      day,
      date,
      selected: isSelected,
      today: isToday,
      disabled: isDisabled,
    })
  }
  
  // Next month days
  const remainingDays = 42 - daysArray.length
  for (let day = 1; day <= remainingDays; day++) {
    daysArray.push({
      day,
      date: new Date(year, month + 1, day),
      selected: false,
      today: false,
      disabled: true,
    })
  }
  
  return daysArray
})

const toggleCalendar = () => {
  if (props.disabled) return
  showCalendar.value = !showCalendar.value
}

const closeCalendar = () => {
  showCalendar.value = false
}

const prevMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1
  )
}

const nextMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1
  )
}

const selectDate = (day: { date: Date, disabled: boolean }) => {
  if (day.disabled) return
  selectedDate.value = day.date
  emit('update:modelValue', day.date)
  closeCalendar()
}

const selectToday = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  selectedDate.value = today
  emit('update:modelValue', today)
  closeCalendar()
}

const clearDate = () => {
  selectedDate.value = null
  emit('update:modelValue', null)
  closeCalendar()
}

// Initialize with modelValue
watch(() => props.modelValue, (value) => {
  if (value) {
    if (value instanceof Date) {
      selectedDate.value = value
      currentDate.value = value
    } else if (typeof value === 'string') {
      selectedDate.value = new Date(value)
      currentDate.value = new Date(value)
    }
  } else {
    selectedDate.value = null
  }
}, { immediate: true })

// Close calendar on outside click
const handleOutsideClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative') && showCalendar.value) {
    closeCalendar()
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.today {
  border-color: #3b82f6;
}
</style>
