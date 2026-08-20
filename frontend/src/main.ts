import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/styles/index.css'
import { ripple, rippleStyles } from '@/directives/ripple'
import { focusVisible, focusVisibleStyles } from '@/directives/focusVisible'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register global directives
app.directive('ripple', ripple)
app.directive('focusVisible', focusVisible)

// Add directive styles to head
const rippleStyleElement = document.createElement('style')
rippleStyleElement.textContent = rippleStyles
document.head.appendChild(rippleStyleElement)

const focusStyleElement = document.createElement('style')
focusStyleElement.textContent = focusVisibleStyles
document.head.appendChild(focusStyleElement)

app.use(createPinia())
app.use(router)

// Initialize dark mode on app mount
app.mount('#app')
