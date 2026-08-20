<template>
  <div class="space-y-1.5">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-300">
      {{ label }}
      <span v-if="required" class="text-danger-500 ml-1">*</span>
    </label>
    
    <!-- Upload Area -->
    <div
      @click="triggerFileInput"
      @dragover.prevent="dragover = true"
      @dragleave.prevent="dragover = false"
      @drop.prevent="handleDrop"
      :class="[
        'relative border-2 border-dashed rounded-xl transition-all duration-200',
        'cursor-pointer',
        dragover ? 'border-primary-500 bg-primary-600/10' : 'border-border bg-surface-elevated/50',
        disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-primary-500',
        error ? 'border-danger-500' : ''
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        @change="handleFileChange"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      
      <!-- Content -->
      <div class="p-6 text-center">
        <div class="w-12 h-12 mx-auto mb-4 rounded-xl bg-primary-600/10 flex items-center justify-center">
          <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
        </div>
        
        <p class="text-sm text-gray-300 mb-1">
          <span v-if="dragover" class="text-primary-400">Drop files here</span>
          <span v-else>Click to upload or drag and drop</span>
        </p>
        
        <p class="text-xs text-gray-500">
          {{ accept ? accept.replace(/\./g, ', ') : 'All file types' }}
          {{ multiple ? ' (Multiple files allowed)' : '' }}
        </p>
        
        <!-- File size limit -->
        <p v-if="maxSize" class="text-xs text-gray-500 mt-1">
          Max size: {{ formatFileSize(maxSize) }}
        </p>
      </div>
      
      <!-- Preview for single file -->
      <div v-if="!multiple && previewUrl" class="p-4 border-t border-border">
        <div class="flex items-center gap-4">
          <img
            v-if="isImage"
            :src="previewUrl"
            class="w-16 h-16 rounded-xl object-cover"
          />
          <div v-else class="w-16 h-16 rounded-xl bg-surface-elevated flex items-center justify-center">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white truncate">{{ fileName }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(fileSize) }}</p>
          </div>
          <Button variant="ghost" size="sm" @click.stop="clearFiles">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </Button>
        </div>
      </div>
      
      <!-- File list for multiple files -->
      <div v-if="multiple && files.length > 0" class="p-4 border-t border-border max-h-40 overflow-y-auto">
        <div v-for="(file, index) in files" :key="index" class="flex items-center gap-3 p-2 rounded-lg hover:bg-surface transition-colors">
          <div class="w-8 h-8 rounded-lg bg-surface-elevated flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white truncate">{{ file.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
          </div>
          <Button variant="ghost" size="sm" @click.stop="removeFile(index)" class="flex-shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
    
    <!-- Error message -->
    <p v-if="error" class="text-sm text-danger-500">{{ error }}</p>
    
    <!-- Hint text -->
    <p v-if="hint && !error" class="text-sm text-gray-500">{{ hint }}</p>
    
    <!-- File count -->
    <p v-if="multiple && files.length > 0" class="text-xs text-gray-500">
      {{ files.length }} file(s) selected
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from './Button.vue'

const props = withDefaults(defineProps<{
  modelValue?: File | File[] | null
  label?: string
  accept?: string
  multiple?: boolean
  disabled?: boolean
  required?: boolean
  error?: string
  hint?: string
  maxSize?: number // in bytes
}>(), {
  modelValue: null,
  accept: '*/*',
  multiple: false,
  disabled: false,
  required: false,
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref<HTMLInputElement | null>(null)
const files = ref<File[]>([])
const dragover = ref(false)
const previewUrl = ref<string | null>(null)
const internalError = ref<string | null>(null)

const fileName = computed(() => {
  return files.value[0]?.name || ''
})

const fileSize = computed(() => {
  return files.value[0]?.size || 0
})

const isImage = computed(() => {
  if (!files.value[0]) return false
  return files.value[0].type.startsWith('image/')
})

const triggerFileInput = () => {
  if (props.disabled) return
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    handleFiles(input.files)
  }
}

const handleDrop = (event: DragEvent) => {
  dragover.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    handleFiles(event.dataTransfer.files)
  }
}

const handleFiles = (fileList: FileList) => {
  internalError.value = null
  
  // Check file count for multiple
  if (!props.multiple && fileList.length > 1) {
    internalError.value = 'Only single file upload is allowed'
    return
  }
  
  // Check max size
  const newFiles = Array.from(fileList)
  for (const file of newFiles) {
    if (props.maxSize && file.size > props.maxSize) {
      internalError.value = `File ${file.name} exceeds maximum size of ${formatFileSize(props.maxSize)}`
      return
    }
  }
  
  files.value = newFiles
  
  // Create preview for single file
  if (!props.multiple && newFiles.length > 0) {
    createPreview(newFiles[0])
  } else {
    previewUrl.value = null
  }
  
  // Emit value
  if (props.multiple) {
    emit('update:modelValue', newFiles)
  } else if (newFiles.length > 0) {
    emit('update:modelValue', newFiles[0])
  } else {
    emit('update:modelValue', null)
  }
}

const createPreview = (file: File) => {
  if (!file.type.startsWith('image/')) {
    previewUrl.value = null
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const removeFile = (index: number) => {
  files.value.splice(index, 1)
  
  if (!props.multiple && files.value.length === 0) {
    previewUrl.value = null
    emit('update:modelValue', null)
  } else if (props.multiple) {
    emit('update:modelValue', files.value)
  } else if (files.value.length > 0) {
    createPreview(files.value[0])
    emit('update:modelValue', files.value[0])
  }
}

const clearFiles = () => {
  files.value = []
  previewUrl.value = null
  emit('update:modelValue', props.multiple ? [] : null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Initialize with modelValue
onMounted(() => {
  if (props.modelValue) {
    if (Array.isArray(props.modelValue)) {
      files.value = props.modelValue
    } else {
      files.value = [props.modelValue]
      if (props.modelValue.type.startsWith('image/')) {
        createPreview(props.modelValue)
      }
    }
  }
})
</script>

<style scoped>
</style>
