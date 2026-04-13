import { defineStore } from 'pinia'
import { ref } from 'vue'

interface UIState {
  sidebarOpen: boolean
  darkMode: boolean
  activeTab: string
}

export const useUIStore = defineStore('ui', () => {
  const sidebarOpen = ref(true)
  const darkMode = ref(true)
  const activeTab = ref('dashboard')

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
  }

  const setActiveTab = (tab: string) => {
    activeTab.value = tab
  }

  return {
    sidebarOpen,
    darkMode,
    activeTab,
    toggleSidebar,
    toggleDarkMode,
    setActiveTab,
  }
})
