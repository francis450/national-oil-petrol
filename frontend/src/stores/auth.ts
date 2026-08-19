import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { frappeAuth, apiClient } from '@/api/client'

interface User {
	name: string
	email: string
	full_name?: string
	roles?: string[]
	employee?: string | null
}

export const useAuthStore = defineStore('auth', () => {
	const user = ref<User | null>(null)
	const isAuthenticated = computed(() => !!user.value)
	const isCheckingAuth = ref(false)

	const fetchPetrolContext = async () => {
		try {
			const response = await apiClient.get('/api/method/national_oil.api.auth.get_petrol_user_context')
			const context = response.data.message
			if (user.value && context) {
				user.value.roles = context.roles || []
				user.value.employee = context.employee || null
			}
		} catch (error) {
			// Non-fatal — role-based UI just falls back to showing nothing extra.
		}
	}

	/**
	 * Check if user has existing ERPNext session (e.g., from Jinja template)
	 * Called on app initialization
	 */
	const checkExistingSession = async () => {
		isCheckingAuth.value = true
		try {
			// Use frappe-js-sdk to detect logged-in user
			const currentUser = await frappeAuth.getLoggedInUser()
			
			if (currentUser && currentUser !== 'Guest') {
				console.log('✓ Existing session detected:', currentUser)
				
				// Fetch full user details
				const userDoc = await apiClient.get(`/api/resource/User/${currentUser}?fields=["name","email","full_name"]`)
				if (userDoc.data.data) {
					user.value = {
						name: userDoc.data.data.name,
						email: userDoc.data.data.email,
						full_name: userDoc.data.data.full_name,
					}
					await fetchPetrolContext()
					return true
				}
			} else {
				console.log('No existing session found')
				user.value = null
				return false
			}
		} catch (error: any) {
			console.warn('Session check failed:', error?.message)
			user.value = null
			return false
		} finally {
			isCheckingAuth.value = false
		}
	}

	/**
	 * Authenticate user with username/password
	 * Works for both ERPNext users and independent petrol users
	 */
	const login = async (username: string, password: string) => {
		try {
			// Use frappe-js-sdk auth to login
			await frappeAuth.loginWithUsernamePassword({ username, password })

			// Login response only confirms the session; fetch full user details separately
			const currentUser = await frappeAuth.getLoggedInUser()
			const userDoc = await apiClient.get(`/api/resource/User/${currentUser}?fields=["name","email","full_name"]`)

			if (userDoc.data.data) {
				user.value = {
					name: userDoc.data.data.name,
					email: userDoc.data.data.email,
					full_name: userDoc.data.data.full_name,
				}
				await fetchPetrolContext()
				console.log('✓ Login successful:', user.value.name)
				return true
			} else {
				console.error('Unexpected user response:', userDoc)
				return false
			}
		} catch (error: any) {
			const errorMsg = error?.response?.data?.exc || error?.message || 'Login failed'
			console.error('Login error:', errorMsg)
			throw new Error(errorMsg)
		}
	}

	/**
	 * Logout current user
	 */
	const logout = async () => {
		try {
			await frappeAuth.logout()
			user.value = null
			console.log('Logout successful')
		} catch (error: any) {
			console.error('Logout failed:', error?.message)
			throw error
		}
	}

	return {
		user,
		isAuthenticated,
		isCheckingAuth,
		checkExistingSession,
		login,
		logout,
		fetchPetrolContext,
	}
})

