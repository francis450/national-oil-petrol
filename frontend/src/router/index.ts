import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
    component: () => import('@/views/dashboard/DashboardView.vue'),
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

  // Redirect unauthenticated users to login
  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  }
  // Redirect authenticated users away from login page
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  }
  // Allow navigation
  else {
    next()
  }
})

export default router
