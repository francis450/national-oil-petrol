import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

// Modules hidden from a user who holds ONLY the Pump Attendant role — anyone who also
// holds an elevated role (Station Manager, System Manager, etc.) keeps full visibility.
const ATTENDANT_RESTRICTED_MODULES = ['sales', 'receivables', 'payables', 'inventory', 'finance', 'hr', 'reports']

const ELEVATED_ROLES = ['System Manager', 'Station Manager', 'Accountant', 'HR Officer', 'Store Keeper', 'Cashier']

export function usePermissions() {
	const auth = useAuthStore()
	const roles = computed(() => auth.user?.roles || [])

	const hasRole = (role: string) => roles.value.includes(role)
	const hasAnyRole = (allowed: string[]) => allowed.some((role) => roles.value.includes(role))

	const isPumpAttendantOnly = computed(() => hasRole('Pump Attendant') && !hasAnyRole(ELEVATED_ROLES))

	/** UX-level nav gating only — the server is the real permission boundary. */
	const canAccessModule = (moduleKey: string) => {
		if (isPumpAttendantOnly.value && ATTENDANT_RESTRICTED_MODULES.includes(moduleKey)) {
			return false
		}
		return true
	}

	return {
		roles,
		hasRole,
		hasAnyRole,
		isPumpAttendantOnly,
		canAccessModule,
	}
}
