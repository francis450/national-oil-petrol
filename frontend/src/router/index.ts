import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'

const MODULE_BY_PATH_PREFIX: Record<string, string> = {
  '/sales': 'sales',
  '/payables': 'payables',
  '/inventory': 'inventory',
  '/finance': 'finance',
  '/hr': 'hr',
  '/reports': 'reports',
}

// PARKED pending a credit-sales decision (see docs/ERP_REUSE_STRATEGY.md). Blocked for every
// role, not just role-gated like MODULE_BY_PATH_PREFIX above — Receivables has no "allowed" role
// right now. The route definitions stay in the routes array below so they can be restored intact.
const PARKED_PATH_PREFIXES = ['/receivables']

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false, layout: 'auth' },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/HomeView.vue'),
    meta: { requiresAuth: true, layout: 'app' },
  },
  {
    path: '/fuel',
    name: 'Fuel',
    component: () => import('@/views/fuel/FuelLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    children: [
      {
        path: 'purchases',
        name: 'FuelPurchases',
        component: () => import('@/views/fuel/FuelPurchaseListView.vue'),
      },
      {
        path: 'prices',
        name: 'FuelPrices',
        component: () => import('@/views/fuel/FuelPriceListView.vue'),
      },
      {
        path: 'readings',
        name: 'PumpReadings',
        component: () => import('@/views/fuel/PumpReadingListView.vue'),
      },
      {
        path: 'shifts',
        name: 'ShiftAssignments',
        component: () => import('@/views/fuel/ShiftAssignmentListView.vue'),
      },
    ],
  },
  {
    path: '/sales',
    name: 'Sales',
    component: () => import('@/views/sales/SalesLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    children: [
      {
        path: 'entries',
        name: 'SalesEntries',
        component: () => import('@/views/sales/SalesEntryListView.vue'),
      },
      {
        path: 'targets',
        name: 'SalesTargets',
        component: () => import('@/views/sales/SalesTargetListView.vue'),
      },
    ],
  },
  {
    path: '/receivables',
    name: 'Receivables',
    component: () => import('@/views/receivables/ReceivablesLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    children: [
      {
        path: 'debts',
        name: 'CustomerDebts',
        component: () => import('@/views/receivables/CustomerDebtListView.vue'),
      },
      {
        path: 'payments',
        name: 'DebtPayments',
        component: () => import('@/views/receivables/DebtPaymentListView.vue'),
      },
    ],
  },
  {
    path: '/payables',
    name: 'Payables',
    component: () => import('@/views/payables/PayablesLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    children: [
      {
        path: 'credits',
        name: 'SupplierCredits',
        component: () => import('@/views/payables/SupplierCreditListView.vue'),
      },
      {
        path: 'payments',
        name: 'CreditPayments',
        component: () => import('@/views/payables/CreditPaymentListView.vue'),
      },
    ],
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('@/views/inventory/InventoryLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    redirect: '/inventory/receipts',
    children: [
      {
        path: 'receipts',
        name: 'InventoryReceipts',
        component: () => import('@/views/inventory/InventoryReceiptListView.vue'),
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/inventory/ProductListView.vue'),
      },
    ],
  },
  {
    path: '/hr',
    name: 'HR',
    component: () => import('@/views/hr/HrLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    redirect: '/hr/employees',
    children: [
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/hr/EmployeeListView.vue'),
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: () => import('@/views/hr/AttendanceListView.vue'),
      },
      {
        path: 'leave',
        name: 'LeaveApplications',
        component: () => import('@/views/hr/LeaveApplicationListView.vue'),
      },
    ],
  },
  {
    path: '/finance',
    name: 'Finance',
    component: () => import('@/views/finance/FinanceLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    redirect: '/finance/accounts',
    children: [
      {
        path: 'accounts',
        name: 'PettyCashAccounts',
        component: () => import('@/views/finance/PettyCashAccountListView.vue'),
      },
      {
        path: 'entries',
        name: 'PettyCashEntries',
        component: () => import('@/views/finance/PettyCashEntryListView.vue'),
      },
    ],
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/reports/ReportsLayout.vue'),
    meta: { requiresAuth: true, layout: 'app' },
    redirect: '/reports/daily-sales-summary',
    children: [
      {
        path: ':reportSlug',
        name: 'ReportView',
        component: () => import('@/views/reports/ReportView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory('/petrol'),
  routes,
})

// Track if initial auth check has completed
let authCheckDone = false

// Route guard for authentication
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  // On first load, check for existing session
  if (!authCheckDone) {
    authCheckDone = true
    await authStore.checkExistingSession()
  }

  // Receivables is parked for every role — block direct navigation regardless of auth state
  if (PARKED_PATH_PREFIXES.some((prefix) => to.path.startsWith(prefix))) {
    next('/')
  }
  // Redirect unauthenticated users to login
  else if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  }
  // Redirect authenticated users away from login page
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  }
  // Block direct navigation into a module hidden from this user's role
  else if (authStore.isAuthenticated) {
    const { canAccessModule, isPumpAttendantOnly } = usePermissions()
    const restrictedPrefix = Object.keys(MODULE_BY_PATH_PREFIX).find((prefix) => to.path.startsWith(prefix))
    if (restrictedPrefix && !canAccessModule(MODULE_BY_PATH_PREFIX[restrictedPrefix])) {
      next('/')
    } else if (to.path.startsWith('/fuel/shifts') && isPumpAttendantOnly.value) {
      // Shift Assignment management is a manager action, not part of the attendant's own workflow
      next('/')
    } else {
      next()
    }
  }
  // Allow navigation
  else {
    next()
  }
})

export default router
