# National Oil — Vue.js Frontend Architecture

> Complete SPA architecture for the national_oil Vue.js frontend.
> Replaces the legacy Bootstrap 3 / jQuery PHP-rendered UI.

---

## Table of Contents

1. [Technology Stack](#1-technology-stack)
2. [Project Structure](#2-project-structure)
3. [Routing](#3-routing)
4. [State Management (Pinia)](#4-state-management-pinia)
5. [API Layer](#5-api-layer)
6. [Authentication & Guards](#6-authentication--guards)
7. [Layout System](#7-layout-system)
8. [Design System](#8-design-system)
9. [Component Architecture](#9-component-architecture)
10. [Data Fetching Strategy](#10-data-fetching-strategy)
11. [Real-Time & Polling](#11-real-time--polling)
12. [Form Handling](#12-form-handling)
13. [Build & Deployment](#13-build--deployment)
14. [Related Documents](#14-related-documents)

---

## 1. Technology Stack

| Concern | Library / Tool | Version |
|---|---|---|
| Framework | Vue.js | 3.x (Composition API) |
| Build Tool | Vite | 5.x |
| Routing | Vue Router | 4.x |
| State | Pinia | 2.x |
| HTTP Client | Axios | 1.x |
| Forms | VeeValidate + Zod | 4.x / 3.x |
| UI Components | PrimeVue | 4.x |
| Icons | Heroicons (via @heroicons/vue) | 2.x |
| Charts | Chart.js + vue-chartjs | 4.x / 5.x |
| Tables | TanStack Table (Vue adapter) | 8.x |
| Date Handling | Day.js | 1.x |
| Formatting | Intl (native) | — |
| Notifications | vue-toastification | 2.x |
| CSS | Tailwind CSS | 3.x |
| Type Safety | TypeScript | 5.x |
| Testing | Vitest + Vue Test Utils | — |
| Linting | ESLint + Prettier | — |

---

## 2. Project Structure

```
apps/national_oil/frontend/          # Vue SPA root
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
│
├── src/
│   ├── main.ts                      # App bootstrap
│   ├── App.vue                      # Root component
│   │
│   ├── router/
│   │   └── index.ts                 # All routes (see §3)
│   │
│   ├── stores/                      # Pinia stores (see §4)
│   │   ├── auth.ts
│   │   ├── dashboard.ts
│   │   ├── fuel.ts
│   │   ├── sales.ts
│   │   ├── inventory.ts
│   │   ├── receivables.ts
│   │   ├── payables.ts
│   │   ├── finance.ts
│   │   ├── hr.ts
│   │   └── ui.ts                    # Sidebar open/close, active tab, etc.
│   │
│   ├── api/                         # API layer (see §5)
│   │   ├── client.ts                # Axios instance + interceptors
│   │   ├── auth.ts
│   │   ├── fuel.ts
│   │   ├── sales.ts
│   │   ├── inventory.ts
│   │   ├── receivables.ts
│   │   ├── payables.ts
│   │   ├── finance.ts
│   │   ├── hr.ts
│   │   ├── mpesa.ts
│   │   └── dashboard.ts
│   │
│   ├── layouts/
│   │   ├── AppLayout.vue            # Sidebar + topbar shell
│   │   ├── AuthLayout.vue           # Login / unauthenticated pages
│   │   └── PrintLayout.vue          # Minimal layout for print views
│   │
│   ├── views/                       # One file per route (see UI_SCREENS.md)
│   │   ├── auth/
│   │   │   └── LoginView.vue
│   │   ├── dashboard/
│   │   │   └── DashboardView.vue
│   │   ├── fuel/
│   │   │   ├── FuelPurchaseListView.vue
│   │   │   ├── FuelPurchaseFormView.vue
│   │   │   ├── PumpReadingListView.vue
│   │   │   └── FuelPriceView.vue
│   │   ├── inventory/
│   │   │   ├── InventoryListView.vue
│   │   │   └── InventoryReceiptFormView.vue
│   │   ├── sales/
│   │   │   ├── SalesEntryListView.vue
│   │   │   ├── SalesEntryFormView.vue
│   │   │   └── SalesTargetView.vue
│   │   ├── receivables/
│   │   │   ├── CustomerListView.vue
│   │   │   ├── CustomerFormView.vue
│   │   │   ├── CustomerDebtListView.vue
│   │   │   └── CustomerDebtDetailView.vue
│   │   ├── payables/
│   │   │   ├── SupplierListView.vue
│   │   │   ├── SupplierFormView.vue
│   │   │   ├── SupplierCreditListView.vue
│   │   │   └── SupplierCreditDetailView.vue
│   │   ├── finance/
│   │   │   ├── PettyCashListView.vue
│   │   │   └── PettyCashAccountView.vue
│   │   ├── hr/
│   │   │   ├── EmployeeListView.vue
│   │   │   ├── EmployeeFormView.vue
│   │   │   ├── AttendanceView.vue
│   │   │   ├── LeaveRequestListView.vue
│   │   │   └── PerformanceView.vue
│   │   └── reports/
│   │       ├── SalesReportView.vue
│   │       ├── DebtAgeingView.vue
│   │       ├── SupplierPayablesView.vue
│   │       ├── PettyCashReportView.vue
│   │       ├── FuelDeliveryLogView.vue
│   │       └── AttendanceSummaryView.vue
│   │
│   ├── components/                  # Reusable components (see UI_COMPONENTS.md)
│   │   ├── layout/
│   │   ├── common/
│   │   ├── charts/
│   │   ├── forms/
│   │   └── tables/
│   │
│   ├── composables/                 # Shared logic
│   │   ├── useDocList.ts            # Generic paginated list from Frappe API
│   │   ├── useDocForm.ts            # Load / save / submit a Frappe doc
│   │   ├── useConfirm.ts            # Confirm dialog before destructive actions
│   │   ├── usePrint.ts              # Trigger browser print / download PDF
│   │   ├── useCurrency.ts           # KSh formatting helpers
│   │   └── usePermissions.ts        # Check current user's roles
│   │
│   ├── types/                       # TypeScript interfaces per DocType
│   │   ├── fuel.ts
│   │   ├── sales.ts
│   │   ├── receivables.ts
│   │   ├── payables.ts
│   │   ├── hr.ts
│   │   └── common.ts
│   │
│   └── utils/
│       ├── date.ts                  # Day.js wrappers
│       ├── number.ts                # flt(), currency formatting
│       └── error.ts                 # Extract Frappe error messages
│
└── public/
    └── favicon.ico
```

---

## 3. Routing

```typescript
// src/router/index.ts

const routes: RouteRecordRaw[] = [

  // Auth
  { path: '/login', component: LoginView, meta: { layout: 'auth' } },

  // App shell (requires auth)
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [

      // Dashboard
      { path: '', name: 'dashboard', component: DashboardView },

      // Fuel Operations
      { path: 'fuel/purchases',          name: 'fuel-list',        component: FuelPurchaseListView },
      { path: 'fuel/purchases/new',      name: 'fuel-new',         component: FuelPurchaseFormView },
      { path: 'fuel/purchases/:name',    name: 'fuel-detail',      component: FuelPurchaseFormView },
      { path: 'fuel/pump-readings',      name: 'pump-readings',    component: PumpReadingListView },
      { path: 'fuel/prices',             name: 'fuel-prices',      component: FuelPriceView },

      // Inventory
      { path: 'inventory',               name: 'inventory',        component: InventoryListView },
      { path: 'inventory/receipts/new',  name: 'inventory-new',    component: InventoryReceiptFormView },
      { path: 'inventory/receipts/:name',name: 'inventory-detail', component: InventoryReceiptFormView },

      // Sales
      { path: 'sales',                   name: 'sales-list',       component: SalesEntryListView },
      { path: 'sales/new',               name: 'sales-new',        component: SalesEntryFormView },
      { path: 'sales/:name',             name: 'sales-detail',     component: SalesEntryFormView },
      { path: 'sales/targets',           name: 'sales-targets',    component: SalesTargetView },

      // Receivables
      { path: 'receivables/customers',           name: 'customers',        component: CustomerListView },
      { path: 'receivables/customers/new',       name: 'customer-new',     component: CustomerFormView },
      { path: 'receivables/customers/:name',     name: 'customer-detail',  component: CustomerFormView },
      { path: 'receivables/debts',               name: 'debts',            component: CustomerDebtListView },
      { path: 'receivables/debts/:name',         name: 'debt-detail',      component: CustomerDebtDetailView },

      // Payables
      { path: 'payables/suppliers',              name: 'suppliers',        component: SupplierListView },
      { path: 'payables/suppliers/new',          name: 'supplier-new',     component: SupplierFormView },
      { path: 'payables/suppliers/:name',        name: 'supplier-detail',  component: SupplierFormView },
      { path: 'payables/credits',                name: 'credits',          component: SupplierCreditListView },
      { path: 'payables/credits/:name',          name: 'credit-detail',    component: SupplierCreditDetailView },

      // Finance
      { path: 'finance/petty-cash',              name: 'petty-cash',       component: PettyCashListView },
      { path: 'finance/petty-cash/accounts',     name: 'petty-accounts',   component: PettyCashAccountView },

      // HR
      { path: 'hr/employees',                    name: 'employees',        component: EmployeeListView },
      { path: 'hr/employees/new',                name: 'employee-new',     component: EmployeeFormView },
      { path: 'hr/employees/:name',              name: 'employee-detail',  component: EmployeeFormView },
      { path: 'hr/attendance',                   name: 'attendance',       component: AttendanceView },
      { path: 'hr/leave-requests',               name: 'leave-requests',   component: LeaveRequestListView },
      { path: 'hr/performance',                  name: 'performance',      component: PerformanceView },

      // Reports
      { path: 'reports/sales',           name: 'report-sales',     component: SalesReportView },
      { path: 'reports/debt-ageing',     name: 'report-debt',      component: DebtAgeingView },
      { path: 'reports/payables',        name: 'report-payables',  component: SupplierPayablesView },
      { path: 'reports/petty-cash',      name: 'report-cash',      component: PettyCashReportView },
      { path: 'reports/fuel-deliveries', name: 'report-fuel',      component: FuelDeliveryLogView },
      { path: 'reports/attendance',      name: 'report-attendance',component: AttendanceSummaryView },
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/' }
]
```

### Navigation Guard

```typescript
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})
```

---

## 4. State Management (Pinia)

### auth.ts

```typescript
interface AuthState {
  user: { name: string; full_name: string; roles: string[] } | null
  token: string | null
}

actions:
  login(usr, pwd)        // POST /api/method/login
  logout()               // POST /api/method/logout
  fetchUser()            // GET /api/method/frappe.auth.get_logged_user + roles
  hasRole(role)          // computed check
```

### dashboard.ts

```typescript
interface DashboardState {
  metrics: DashboardMetrics | null
  salesTrend: ChartData | null
  fuelStock: FuelStockItem[]
  loading: boolean
  lastFetched: Date | null
}

actions:
  fetchMetrics()
  fetchSalesTrend(days: 7 | 30 | 365)
  // Auto-refresh every 5 minutes via composable
```

### Pattern for all other stores

```typescript
// Generic pattern applied to: fuel, sales, inventory, receivables, payables, finance, hr
interface ModuleState {
  list: T[]
  current: T | null
  total: number
  loading: boolean
  filters: FilterState
}

actions:
  fetchList(params)      // uses useDocList composable
  fetchOne(name)         // uses useDocForm composable
  save(data)             // POST to Frappe API
  submit(name)           // set docstatus=1
  cancel(name)           // set docstatus=2
  delete(name)
  resetFilters()
```

### ui.ts

```typescript
interface UIState {
  sidebarOpen: boolean
  activeModal: string | null
  modalProps: Record<string, unknown>
}

actions:
  openModal(id, props?)
  closeModal()
  toggleSidebar()
```

---

## 5. API Layer

```typescript
// src/api/client.ts

const client = axios.create({
  baseURL: '/api',
  withCredentials: true,          // send session cookie
  headers: { 'X-Frappe-CSRF-Token': getCsrfToken() }
})

// Request interceptor: refresh CSRF token on mutation
client.interceptors.request.use((config) => {
  if (['post', 'put', 'delete'].includes(config.method ?? '')) {
    config.headers['X-Frappe-CSRF-Token'] = getCsrfToken()
  }
  return config
})

// Response interceptor: unified error normalisation
client.interceptors.response.use(
  (res) => res.data.message ?? res.data,
  (err) => {
    const msg = extractFrappeError(err.response?.data)
    useToast().error(msg)
    if (err.response?.status === 403) useAuthStore().logout()
    return Promise.reject(new Error(msg))
  }
)
```

### Module API example

```typescript
// src/api/receivables.ts

export const receivablesApi = {
  listDebts:    (params) => client.get('/resource/Customer Debt', { params }),
  getDebt:      (name)   => client.get(`/resource/Customer Debt/${name}`),
  createDebt:   (data)   => client.post('/resource/Customer Debt', { data }),
  updateDebt:   (name, data) => client.put(`/resource/Customer Debt/${name}`, { data }),
  recordPayment:(data)   => client.post('/method/national_oil.receivables.api.record_debt_payment', data),
  getBalance:   (customer) => client.get('/method/national_oil.receivables.api.get_customer_balance', { params: { customer } }),
}
```

---

## 6. Authentication & Guards

- Login page is the only unauthenticated route
- `useAuthStore.fetchUser()` called on app mount; if 403 → redirect to `/login`
- Roles stored in Pinia; `usePermissions()` composable exposes `can(doctype, action)`
- CSRF token read from `frappe.csrf_token` injected by Frappe into the page (or fetched via `/api/method/frappe.auth.csrf_token`)

---

## 7. Layout System

### AppLayout.vue

```
┌─────────────────────────────────────────────────────────────┐
│  TopBar                                                     │
│  [≡ Logo]  [Breadcrumbs]         [Notifications] [User ▾]  │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   Sidebar    │   <RouterView />                             │
│   (240px)    │   (scrollable content area)                  │
│              │                                              │
│   nav items  │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

- Sidebar collapses to icon-only strip on mobile (`sidebarOpen` from ui store)
- Topbar shows breadcrumb trail based on current route name
- `<RouterView />` wrapped in `<Transition name="fade">` for page transitions

### AuthLayout.vue

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│          [National Oil Logo]                                │
│                                                             │
│          ┌─────────────────────────┐                        │
│          │   Login Card            │                        │
│          └─────────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Design System

### Colour Tokens (Tailwind config)

```javascript
// tailwind.config.ts
colors: {
  brand: {
    50:  '#fef9ec',
    100: '#fdf0c3',
    500: '#f5a623',      // primary gold/amber — fuel station brand
    600: '#d4891a',
    900: '#7a4a00',
  },
  success:  { DEFAULT: '#16a34a' },
  danger:   { DEFAULT: '#dc2626' },
  warning:  { DEFAULT: '#d97706' },
  info:     { DEFAULT: '#0284c7' },
  surface: {
    DEFAULT: '#ffffff',
    muted:   '#f9fafb',
    border:  '#e5e7eb',
  }
}
```

### Typography

- Font: `Inter` (Google Fonts)
- Base size: 14px
- Headings: 600 weight
- Monospace (amounts, codes): `JetBrains Mono`

### Spacing

Follows Tailwind's 4px grid. Key spacings:
- Card padding: `p-6` (24px)
- Section gap: `gap-4` or `gap-6`
- Form row gap: `gap-3`

### Status Badges

```
Open          → bg-yellow-100 text-yellow-800
Partially Paid→ bg-blue-100   text-blue-800
Settled       → bg-green-100  text-green-800
Cancelled     → bg-red-100    text-red-800
Draft         → bg-gray-100   text-gray-600
Submitted     → bg-indigo-100 text-indigo-800
```

### KSh Currency Formatting

```typescript
// src/utils/number.ts
export function formatKsh(value: number): string {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 2,
  }).format(value)
}
```

---

## 9. Component Architecture

See [UI_COMPONENTS.md](UI_COMPONENTS.md) for full component specifications.

High-level tree:

```
App.vue
└── AppLayout.vue
    ├── AppSidebar.vue
    │   ├── SidebarSection.vue
    │   └── SidebarNavItem.vue
    ├── AppTopBar.vue
    │   ├── Breadcrumbs.vue
    │   ├── NotificationBell.vue
    │   └── UserMenu.vue
    └── RouterView → View.vue
        ├── PageHeader.vue           (title + action buttons)
        ├── StatCard.vue             (dashboard number cards)
        ├── DataTable.vue            (TanStack Table wrapper)
        ├── DocForm.vue              (generic Frappe form fields)
        ├── ModalDialog.vue          (teleport-based modal)
        ├── LineChart.vue / BarChart.vue / PieChart.vue
        ├── FilterBar.vue            (date range + select filters)
        └── EmptyState.vue
```

---

## 10. Data Fetching Strategy

### List Views

```typescript
// src/composables/useDocList.ts
export function useDocList<T>(doctype: string, options?: ListOptions) {
  const list     = ref<T[]>([])
  const total    = ref(0)
  const loading  = ref(false)
  const page     = ref(1)
  const pageSize = ref(20)
  const filters  = ref(options?.defaultFilters ?? [])

  async function fetch() {
    loading.value = true
    const res = await client.get(`/resource/${doctype}`, {
      params: {
        fields: options?.fields,
        filters: JSON.stringify(filters.value),
        limit_start: (page.value - 1) * pageSize.value,
        limit_page_length: pageSize.value,
        order_by: options?.orderBy ?? 'modified desc',
      }
    })
    list.value  = res.data
    total.value = res.total_count ?? res.data.length
    loading.value = false
  }

  watch([page, filters], fetch, { deep: true })
  onMounted(fetch)

  return { list, total, loading, page, pageSize, filters, refresh: fetch }
}
```

### Form Views

```typescript
// src/composables/useDocForm.ts
export function useDocForm<T>(doctype: string, name?: string) {
  const doc     = ref<Partial<T>>({})
  const loading = ref(false)
  const saving  = ref(false)

  async function load(docName: string) { ... }
  async function save() { ... }     // insert or update
  async function submit() { ... }   // docstatus → 1
  async function cancel() { ... }   // docstatus → 2

  if (name) onMounted(() => load(name))

  return { doc, loading, saving, load, save, submit, cancel }
}
```

---

## 11. Real-Time & Polling

Frappe supports Socket.IO (real-time doctype events). For simplicity the initial
implementation uses **polling** with `setInterval` only on the Dashboard:

```typescript
// In DashboardView.vue
onMounted(() => {
  dashboardStore.fetchMetrics()
  const interval = setInterval(dashboardStore.fetchMetrics, 5 * 60 * 1000)  // 5 min
  onUnmounted(() => clearInterval(interval))
})
```

Future: migrate to `frappe.realtime` (Socket.IO) for live pump meter updates.

---

## 12. Form Handling

Forms use **VeeValidate** with **Zod** schemas:

```typescript
// Example: FuelPurchaseFormView.vue
const schema = z.object({
  code:            z.string().min(1),
  dated:           z.string().date(),
  supplier:        z.string().min(1),
  fuel_type:       z.string().min(1),
  actual_quantity: z.number().positive(),
  unit_cost:       z.number().positive(),
  total_cost:      z.number().positive(),
  amount_paid:     z.number().min(0),
})

const { handleSubmit, errors, values } = useForm({ validationSchema: toTypedSchema(schema) })

// Computed total_cost
const totalCost = computed(() => values.actual_quantity * values.unit_cost)
```

### File / Receipt Uploads

```typescript
// Upload to Frappe file API, then store file URL in doc field
async function uploadReceipt(file: File, doctype: string, docname: string) {
  const formData = new FormData()
  formData.append('file',       file)
  formData.append('doctype',    doctype)
  formData.append('docname',    docname)
  formData.append('is_private', '0')
  const res = await client.post('/method/upload_file', formData)
  return res.file_url
}
```

---

## 13. Build & Deployment

### Vite config

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': '/src' } },
  build: {
    outDir: '../national_oil/public/dist',  // served by Frappe
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://national-oil.localhost:8000',
      '/assets': 'http://national-oil.localhost:8000',
    }
  }
})
```

### Frappe Integration

The built SPA is served via a Frappe **Web Page** or custom route that injects:
- CSRF token into window
- Current user info into window
- Frappe assets (CSS) for consistency

```python
# apps/national_oil/national_oil/templates/pages/app.html
{% extends "templates/web.html" %}
{% block title %}National Oil{% endblock %}
{% block page_content %}
<div id="app"></div>
<script>
  window.__frappe_csrf_token__ = "{{ csrf_token }}";
  window.__frappe_user__ = {{ user_info | tojson }};
</script>
<script type="module" src="/assets/national_oil/dist/index.js"></script>
{% endblock %}
```

### Scripts

```json
{
  "dev":   "vite",
  "build": "tsc --noEmit && vite build",
  "test":  "vitest",
  "lint":  "eslint src --fix"
}
```

---

## 14. Related Documents

| Document | Path |
|---|---|
| Screen-by-Screen Specs | [UI_SCREENS.md](UI_SCREENS.md) |
| Component Library | [UI_COMPONENTS.md](UI_COMPONENTS.md) |
| Backend Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| API Endpoints | [API_SPECS.md](API_SPECS.md) |
| Data Model | [DATA_MODEL.md](DATA_MODEL.md) |
