import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

interface UIState {
  sidebarOpen: boolean
  darkMode: boolean
  activeTab: string
}

export const useUIStore = defineStore('ui', () => {
  // State
  const sidebarOpen = ref<boolean>(true)
  const darkMode = ref<boolean>(true)
  const activeTab = ref<string>('dashboard')

  // Check system preference for dark mode
  const checkSystemPreference = (): boolean => {
    if (typeof window !== 'undefined') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      return prefersDark
    }
    return true // Default to dark mode
  }

  // Initialize dark mode from localStorage or system preference
  const initDarkMode = () => {
    const savedMode = localStorage.getItem('darkMode')
    if (savedMode) {
      darkMode.value = savedMode === 'true'
    } else {
      darkMode.value = checkSystemPreference()
    }
    updateHtmlClass()
  }

  // Update HTML class based on dark mode
  const updateHtmlClass = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', darkMode.value)
    }
  }

  // Toggle sidebar
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  // Toggle dark mode with smooth transition
  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value.toString())
    updateHtmlClass()
  }

  // Set dark mode explicitly
  const setDarkMode = (mode: boolean) => {
    darkMode.value = mode
    localStorage.setItem('darkMode', mode.toString())
    updateHtmlClass()
  }

  // Set active tab
  const setActiveTab = (tab: string) => {
    activeTab.value = tab
  }

  // Watch for dark mode changes
  watch(darkMode, (newMode) => {
    updateHtmlClass()
  })

  // Initialize on store creation
  initDarkMode()

  return {
    sidebarOpen,
    darkMode,
    activeTab,
    toggleSidebar,
    toggleDarkMode,
    setDarkMode,
    setActiveTab,
    initDarkMode,
  }
})
