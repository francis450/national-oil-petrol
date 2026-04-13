import axios, { AxiosInstance } from 'axios'
import { FrappeApp } from 'frappe-js-sdk'

// Initialize Frappe JS SDK for session management and auth
const frappe = new FrappeApp(window.location.origin)

// Export Frappe SDK instances
export const frappeCall = frappe.call()
export const frappeAuth = frappe.auth()
export const frappeDB = frappe.db()
export const frappeClient = frappe

let csrfToken = ''

// Extract CSRF token from window (injected by Jinja template) or cookies
const getCsrfToken = (): string => {
	// Priority 1: Use token from window global (injected by Jinja template)
	if ((window as any).csrf_token) {
		csrfToken = (window as any).csrf_token
		return csrfToken
	}

	// Priority 2: Extract from cookies
	const cookies = document.cookie.split(';')
	for (let cookie of cookies) {
		const [name, value] = cookie.trim().split('=')
		if (name === 'csrf_token') {
			csrfToken = decodeURIComponent(value)
			return csrfToken
		}
	}

	return ''
}

// Create axios instance for direct API calls
const apiClient: AxiosInstance = axios.create({
	baseURL: '/',
	timeout: 30000,
	withCredentials: true,
	headers: {
		'Content-Type': 'application/json',
	},
})

// Request interceptor: Attach CSRF token to state-changing requests
apiClient.interceptors.request.use((config) => {
	if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
		const token = getCsrfToken()
		if (token) {
			config.headers['X-Frappe-CSRF-Token'] = token
		}
	}
	return config
}, (error) => Promise.reject(error))

// Response interceptor: Handle auth errors and update CSRF token
apiClient.interceptors.response.use(
	(response) => {
		const token = response.headers['x-frappe-csrf-token']
		if (token) {
			csrfToken = token
		}
		return response
	},
	(error) => {
		if (error.response?.status === 401 || error.response?.status === 403) {
			console.log('Unauthorized: redirecting to login')
			window.location.href = '/petrol#/login'
		}
		return Promise.reject(error)
	}
)

export { apiClient, getCsrfToken }
