# National Oil — Component Library

> Specification for every reusable Vue component in the national_oil SPA.
> Components are organised by category.

---

## Table of Contents

1. [Layout Components](#1-layout-components)
2. [Common / Shared Components](#2-common--shared-components)
3. [Form Components](#3-form-components)
4. [Table Components](#4-table-components)
5. [Chart Components](#5-chart-components)
6. [Module-Specific Components](#6-module-specific-components)
7. [Component Interaction Patterns](#7-component-interaction-patterns)

---

## 1. Layout Components

### AppSidebar.vue

**Path**: `src/components/layout/AppSidebar.vue`

Navigation sidebar. Collapses to icon-only on screens < 1024px.

**Props**: none (reads `uiStore.sidebarOpen`)

**Navigation structure**:

```typescript
const navSections = [
  {
    label: 'Operations',
    items: [
      { label: 'Dashboard',      icon: HomeIcon,        to: '/' },
      { label: 'Fuel Purchases', icon: BeakerIcon,      to: '/fuel/purchases' },
      { label: 'Pump Readings',  icon: ChartBarIcon,    to: '/fuel/pump-readings' },
      { label: 'Inventory',      icon: CubeIcon,        to: '/inventory' },
      { label: 'Sales',          icon: ShoppingCartIcon,to: '/sales' },
    ]
  },
  {
    label: 'Finance',
    items: [
      { label: 'Customer Debts', icon: UsersIcon,      to: '/receivables/debts' },
      { label: 'Customers',      icon: UserIcon,       to: '/receivables/customers' },
      { label: 'Suppliers',      icon: TruckIcon,      to: '/payables/suppliers' },
      { label: 'Credits',        icon: CreditCardIcon, to: '/payables/credits' },
      { label: 'Petty Cash',     icon: BanknotesIcon,  to: '/finance/petty-cash' },
    ]
  },
  {
    label: 'HR',
    items: [
      { label: 'Employees',      icon: IdentificationIcon, to: '/hr/employees' },
      { label: 'Attendance',     icon: CalendarIcon,       to: '/hr/attendance' },
      { label: 'Leave Requests', icon: PaperAirplaneIcon,  to: '/hr/leave-requests' },
      { label: 'Performance',    icon: TrophyIcon,         to: '/hr/performance' },
    ]
  },
  {
    label: 'Reports',
    items: [
      { label: 'Sales Report',   icon: DocumentChartBarIcon, to: '/reports/sales' },
      { label: 'Debt Ageing',    icon: ClockIcon,            to: '/reports/debt-ageing' },
      { label: 'Payables',       icon: ReceiptPercentIcon,   to: '/reports/payables' },
      { label: 'Petty Cash',     icon: DocumentTextIcon,     to: '/reports/petty-cash' },
      { label: 'Fuel Log',       icon: QueueListIcon,        to: '/reports/fuel-deliveries' },
      { label: 'Attendance',     icon: TableCellsIcon,       to: '/reports/attendance' },
    ]
  }
]
```

**Template sketch**:
```html
<nav :class="['sidebar', { 'sidebar--collapsed': !sidebarOpen }]">
  <div class="sidebar__logo">
    <img src="/assets/national_oil/img/logo.png" alt="National Oil" />
    <span v-if="sidebarOpen">National Oil</span>
  </div>
  <div v-for="section in navSections" :key="section.label">
    <p v-if="sidebarOpen" class="sidebar__section-label">{{ section.label }}</p>
    <SidebarNavItem v-for="item in section.items" v-bind="item" :collapsed="!sidebarOpen" />
  </div>
</nav>
```

---

### SidebarNavItem.vue

**Props**:
| Prop | Type | Default |
|---|---|---|
| `label` | `string` | required |
| `to` | `string` | required |
| `icon` | `Component` | required |
| `collapsed` | `boolean` | `false` |
| `badge` | `number \| null` | `null` |

Renders a `<RouterLink>` with active class, icon, label (hidden when collapsed), and optional badge.

---

### AppTopBar.vue

**Path**: `src/components/layout/AppTopBar.vue`

```html
<header class="topbar">
  <button @click="uiStore.toggleSidebar">
    <Bars3Icon class="w-5 h-5" />
  </button>

  <Breadcrumbs />

  <div class="topbar__actions">
    <NotificationBell />
    <UserMenu />
  </div>
</header>
```

---

### Breadcrumbs.vue

Derives breadcrumb trail from `route.matched` + route meta `breadcrumb` labels.

```typescript
// Route meta example
{ path: '/receivables/debts/:name', meta: { breadcrumb: ['Receivables', 'Debts', ':name'] } }
```

---

### UserMenu.vue

Dropdown showing `authStore.user.full_name`, links to profile, and Logout button.

---

## 2. Common / Shared Components

### PageHeader.vue

**Path**: `src/components/common/PageHeader.vue`

Consistent page title + action slot used on every view.

**Props**:
| Prop | Type |
|---|---|
| `title` | `string` |
| `subtitle` | `string?` |
| `loading` | `boolean?` |

**Slots**:
- `actions` — buttons placed top-right (e.g. `[+ New]`, `[Print]`)

```html
<PageHeader title="Fuel Purchases" subtitle="47 records">
  <template #actions>
    <AppButton variant="primary" @click="router.push('/fuel/purchases/new')">
      + New Purchase
    </AppButton>
  </template>
</PageHeader>
```

---

### StatCard.vue

**Path**: `src/components/common/StatCard.vue`

Dashboard number card.

**Props**:
| Prop | Type |
|---|---|
| `label` | `string` |
| `value` | `number \| string` |
| `format` | `'currency' \| 'number' \| 'text'` |
| `trend` | `{ value: number; direction: 'up' \| 'down' \| 'flat' }?` |
| `icon` | `Component?` |
| `color` | `'brand' \| 'success' \| 'danger' \| 'info'` |
| `loading` | `boolean` |

```html
<StatCard
  label="Today's Sales"
  :value="metrics.today_sales"
  format="currency"
  :trend="{ value: 4.2, direction: 'up' }"
  :icon="ShoppingCartIcon"
  color="brand"
/>
```

---

### AppButton.vue

Wrapper over native `<button>` with variants and loading state.

**Props**:
| Prop | Type | Default |
|---|---|---|
| `variant` | `'primary' \| 'secondary' \| 'danger' \| 'ghost'` | `'secondary'` |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` |
| `loading` | `boolean` | `false` |
| `disabled` | `boolean` | `false` |
| `type` | `'button' \| 'submit'` | `'button'` |

---

### StatusBadge.vue

**Props**: `status: string`

Maps status string → colour class automatically:

```typescript
const colorMap: Record<string, string> = {
  'Open':           'bg-yellow-100 text-yellow-800',
  'Partially Paid': 'bg-blue-100 text-blue-800',
  'Settled':        'bg-green-100 text-green-800',
  'Cancelled':      'bg-red-100 text-red-800',
  'Draft':          'bg-gray-100 text-gray-600',
  'Submitted':      'bg-indigo-100 text-indigo-800',
  'Pending':        'bg-orange-100 text-orange-800',
  'Approved':       'bg-green-100 text-green-800',
  'Rejected':       'bg-red-100 text-red-800',
  'Present':        'bg-green-100 text-green-800',
  'Absent':         'bg-red-100 text-red-800',
}
```

---

### ModalDialog.vue

**Path**: `src/components/common/ModalDialog.vue`

Replaces all legacy Bootstrap modals and PHP `window.open()` popups.

Uses Vue `<Teleport to="body">` so the modal renders outside the component tree.

**Props**:
| Prop | Type |
|---|---|
| `modelValue` | `boolean` (v-model) |
| `title` | `string` |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl'` |
| `persistent` | `boolean` (block close on backdrop click) |

**Slots**: `default` (body), `footer` (action buttons)

```html
<ModalDialog v-model="showPaymentModal" title="Record Payment" size="md">
  <DebtPaymentForm :debt="currentDebt" @saved="onPaymentSaved" />
  <template #footer>
    <AppButton variant="ghost" @click="showPaymentModal = false">Cancel</AppButton>
    <AppButton variant="primary" type="submit" form="payment-form">Save</AppButton>
  </template>
</ModalDialog>
```

---

### SlideOver.vue

**Path**: `src/components/common/SlideOver.vue`

Slide-in panel from the right. Used for detail views (debt payment, credit payment)
that in the legacy system used `window.open()` popup windows.

**Props**: same as `ModalDialog` but always `size="lg"` equivalent.

**Slots**: `default`, `footer`

---

### ConfirmDialog.vue

Wraps `useConfirm()` composable. Displays a destructive action confirmation dialog.

```typescript
// Usage in a view
const { confirm } = useConfirm()

async function cancelDocument() {
  const ok = await confirm({
    title: 'Cancel Document?',
    message: 'This will reverse all stock and financial effects.',
    confirmLabel: 'Yes, Cancel',
    variant: 'danger',
  })
  if (ok) await fuelStore.cancel(doc.name)
}
```

---

### FilterBar.vue

**Path**: `src/components/common/FilterBar.vue`

Horizontal bar of filter controls. Emits `update:filters` on any change.

**Props**:
| Prop | Type |
|---|---|
| `filters` | `FilterDefinition[]` |
| `modelValue` | `Record<string, unknown>` |

**FilterDefinition types**:
```typescript
type FilterDefinition =
  | { key: string; label: string; type: 'date' }
  | { key: string; label: string; type: 'daterange' }
  | { key: string; label: string; type: 'select'; options: SelectOption[] }
  | { key: string; label: string; type: 'link'; doctype: string }
  | { key: string; label: string; type: 'search' }
```

```html
<FilterBar
  v-model="filters"
  :filters="[
    { key: 'from_date',  label: 'From',     type: 'date' },
    { key: 'to_date',    label: 'To',       type: 'date' },
    { key: 'supplier',   label: 'Supplier', type: 'link', doctype: 'Supplier' },
    { key: 'status',     label: 'Status',   type: 'select', options: statusOptions },
  ]"
/>
```

---

### EmptyState.vue

**Props**: `title: string`, `message: string`, `icon?: Component`

Shown in DataTable when `list.length === 0` and not loading.

---

### LoadingSpinner.vue

Full-page or inline spinner. **Props**: `fullPage: boolean`, `size: 'sm' | 'md' | 'lg'`

---

### AlertBanner.vue

**Props**: `type: 'info' | 'warning' | 'error' | 'success'`, `message: string`, `dismissible: boolean`

Used to surface Frappe validation warnings above forms.

---

## 3. Form Components

All form components use `useField` from VeeValidate and accept `name` prop for validation binding.

### AppInput.vue

**Props**: `name`, `label`, `type` (text/number/email/password), `placeholder`, `required`, `readonly`, `disabled`

---

### AppSelect.vue

**Props**: `name`, `label`, `options: { value, label }[]`, `required`, `disabled`

---

### LinkField.vue

Frappe-style link field with autocomplete search from a DocType.

**Props**:
| Prop | Type |
|---|---|
| `name` | `string` |
| `label` | `string` |
| `doctype` | `string` |
| `required` | `boolean` |
| `disabled` | `boolean` |
| `quickCreate` | `boolean` (shows `[+]` icon to open create modal inline) |

**Behaviour**:
- On input: debounced `GET /api/resource/{doctype}?filters=[["name","like","…%"]]`
- Shows dropdown of matches with name + optional subtitle
- On select: sets `modelValue` to the selected doc name (Frappe link field convention)

```html
<LinkField
  name="supplier"
  label="Supplier"
  doctype="Supplier"
  :required="true"
  :quick-create="true"
/>
```

---

### CurrencyInput.vue

Number input formatted as KSh with thousands separator.

**Props**: `name`, `label`, `required`, `readonly`, `min`

Internally stores raw number, displays as formatted string.

---

### DatePicker.vue

Wraps PrimeVue's Calendar for consistent date input.

**Props**: `name`, `label`, `required`, `maxDate`, `minDate`

---

### FileUpload.vue

Replaces legacy `<input type="file">` receipt upload.

**Props**:
| Prop | Type |
|---|---|
| `name` | `string` |
| `label` | `string` |
| `accept` | `string` (e.g. `'image/*,.pdf'`) |
| `doctype` | `string` (for Frappe file association) |
| `docname` | `string` |
| `modelValue` | `string` (file URL) |

**Behaviour**:
- Drag-and-drop zone or click-to-browse
- Shows thumbnail for images, PDF icon for PDFs
- Uploads via `POST /api/method/upload_file`
- Displays existing file if `modelValue` already set

---

### TextArea.vue

**Props**: `name`, `label`, `rows`, `required`

---

### CheckField.vue

**Props**: `name`, `label`, `trueLabel`, `falseLabel`

---

### RadioGroup.vue

**Props**: `name`, `label`, `options: { value, label }[]`

Used for `sale_type` (Wet Stock / Other) and `designation` (Permanent / Casual).

---

### FormSection.vue

Groups form fields under a collapsible titled section.

```html
<FormSection title="Dip Measurements" collapsible>
  <AppInput name="initial_dip" label="Initial Dip (cm)" type="number" />
  <AppInput name="final_dip"   label="Final Dip (cm)"   type="number" />
  <AppInput name="actual_quantity" label="Actual Qty (L)" type="number" readonly />
</FormSection>
```

---

## 4. Table Components

### DataTable.vue

**Path**: `src/components/tables/DataTable.vue`

Generic paginated table built on **TanStack Table** (Vue adapter).

**Props**:
| Prop | Type | Notes |
|---|---|---|
| `columns` | `ColumnDef<T>[]` | TanStack column definitions |
| `data` | `T[]` | Row data |
| `total` | `number` | Total record count (for server-side pagination) |
| `loading` | `boolean` | Shows skeleton rows |
| `pageSize` | `number` | Default 20 |
| `sortable` | `boolean` | Enable column sort |
| `selectable` | `boolean` | Show checkboxes for bulk actions |
| `emptyMessage` | `string` | Overrides default EmptyState message |

**Slots**: `row-actions` (per-row action buttons), `bulk-actions` (shown when rows selected)

**Column definition helpers**:
```typescript
// src/utils/tableColumns.ts

export const dateCol = (key: string, label: string): ColumnDef =>
  ({ accessorKey: key, header: label, cell: (info) => formatDate(info.getValue()) })

export const currencyCol = (key: string, label: string): ColumnDef =>
  ({ accessorKey: key, header: label, cell: (info) => formatKsh(info.getValue()) })

export const statusCol = (key: string, label = 'Status'): ColumnDef =>
  ({ accessorKey: key, header: label, cell: (info) => h(StatusBadge, { status: info.getValue() }) })
```

**Usage example** (FuelPurchaseListView):

```typescript
const columns: ColumnDef<FuelPurchase>[] = [
  { accessorKey: 'code',       header: 'Code' },
  dateCol('dated',             'Date'),
  { accessorKey: 'supplier',   header: 'Supplier' },
  { accessorKey: 'fuel_type',  header: 'Fuel Type' },
  currencyCol('actual_quantity','Qty (L)'),
  currencyCol('total_cost',    'Total Cost'),
  currencyCol('balance',       'Balance'),
  statusCol('status'),
]
```

---

### AttendanceGrid.vue

**Path**: `src/components/tables/AttendanceGrid.vue`

Special calendar-style grid for the Attendance view (replaces the day-by-day rows idea
with a month-at-a-glance grid).

**Props**: `employees: Employee[]`, `month: number`, `year: number`, `records: AttendanceRecord[]`

**Emits**: `update:record(employee, date, status)` — enables inline editing by clicking cells.

---

### SummaryBar.vue

Horizontal summary row above a DataTable showing key totals.

**Props**: `items: { label: string; value: number | string; format?: 'currency' | 'number' }[]`

---

## 5. Chart Components

All chart components wrap **Chart.js** via **vue-chartjs**. They are responsive by default.

### LineChart.vue

**Path**: `src/components/charts/LineChart.vue`

**Props**:
| Prop | Type |
|---|---|
| `labels` | `string[]` |
| `datasets` | `{ name: string; values: number[]; color?: string }[]` |
| `height` | `number` |
| `yFormat` | `'currency' \| 'number'` |
| `loading` | `boolean` |

Used for: Sales Trend, Deviation Trend, Debt Collection Trend.

---

### BarChart.vue

**Props**: same as `LineChart` plus:
| Prop | Type |
|---|---|
| `grouped` | `boolean` (grouped vs stacked) |
| `horizontal` | `boolean` |

Used for: Fuel Stock Levels, Department Performance, Attendance %, Target vs Hit.

---

### PieChart.vue / DonutChart.vue

**Props**:
| Prop | Type |
|---|---|
| `labels` | `string[]` |
| `values` | `number[]` |
| `colors` | `string[]?` |
| `loading` | `boolean` |

Used for: Today's Attendance (Present/Absent donut).

---

### ChartCard.vue

Wrapper that adds a card shell, title, and optional period switcher tabs around a chart.

**Props**:
| Prop | Type |
|---|---|
| `title` | `string` |
| `periods` | `{ label: string; value: string }[]?` |
| `activePeriod` | `string?` |
| `loading` | `boolean` |

**Slots**: `default` (the chart component), `actions` (export button etc.)

---

## 6. Module-Specific Components

### DebtAlertCard.vue

Dashboard alert card showing open customer debt count and total outstanding.
Links to `/receivables/debts?status=Open`.

**Props**: `count: number`, `total: number`, `loading: boolean`

---

### DebtPaymentForm.vue

Reusable form for recording a payment (used in Customer Debt Detail slide-over
AND in the Customer Debt List inline Pay button).

**Props**: `debtName: string`, `maxAmount: number`, `customer: string`

**Emits**: `saved(paymentName: string)`

```html
<form id="payment-form" @submit="handleSubmit(onSubmit)">
  <CurrencyInput name="amount" label="Amount" :required="true" />
  <AppSelect     name="payment_method" label="Payment Method" :options="paymentMethods" />
  <AppInput      name="reference" label="Reference (M-Pesa / Cheque No.)" />
  <DatePicker    name="dated" label="Date" :required="true" />
  <FileUpload    name="receipt" label="Receipt" accept="image/*,.pdf" />

  <!-- M-Pesa shortcut when payment_method === 'M-Pesa' -->
  <MpesaStkButton v-if="isMpesa" :customer="customer" :amount="values.amount" :debt-name="debtName" />
</form>
```

---

### MpesaStkButton.vue

Button that initiates an M-Pesa STK Push and polls for confirmation.

**Props**: `customer: string`, `amount: number`, `debtName: string`, `phone: string`

**States**: Idle → Sending → Waiting for customer → Confirmed / Failed

```html
<AppButton
  variant="primary"
  :loading="status === 'sending' || status === 'waiting'"
  @click="initiatePush"
>
  <template v-if="status === 'idle'">
    <DevicePhoneMobileIcon class="w-4 h-4 mr-1" /> Send to {{ phone }}
  </template>
  <template v-else-if="status === 'waiting'">
    Waiting for payment…
  </template>
  <template v-else-if="status === 'confirmed'">
    ✓ Confirmed ({{ mpesaRef }})
  </template>
</AppButton>
```

---

### FuelDipCalculator.vue

Helper embedded in the Fuel Purchase form. When both `initial_dip` and `final_dip`
are entered, calculates and proposes `actual_quantity`.

**Props**: `initialDip: number`, `finalDip: number`, `tankCapacity: number`

**Emits**: `suggest(qty: number)`

---

### BulkAttendanceModal.vue

Opens a modal with all employees listed. Toggle each between Present/Absent.
Submits all records in one `bulk_mark_attendance` API call.

**Props**: `date: string`

**Emits**: `saved`

---

### PrintButton.vue

Triggers browser `window.print()` or PDF export via Frappe Print Format.

**Props**: `doctype: string`, `name: string`, `printFormat: string?`

```typescript
// Uses Frappe's built-in print URL
const url = `/printview?doctype=${doctype}&name=${name}&format=${printFormat}&no_letterhead=0`
window.open(url, '_blank')
```

---

### ExportExcelButton.vue

Exports current report/table data as XLSX via Frappe's built-in export.

**Props**: `doctype: string`, `filters: FrappeFilter[]`, `fields: string[]`

---

## 7. Component Interaction Patterns

### Pattern A: List → Slide-over Detail

Used by: Customer Debt, Supplier Credit

```
CustomerDebtListView
  └── DataTable
        └── row action [Pay] → opens SlideOver
              └── DebtPaymentForm (emits 'saved')
                    → refreshes table (useDocList.refresh())
```

### Pattern B: List → Full Page Form

Used by: Fuel Purchase, Sales Entry, Employee

```
FuelPurchaseListView
  └── [+ New] button → router.push('/fuel/purchases/new')
        FuelPurchaseFormView (new)
        FuelPurchaseFormView (edit, loads :name)
          → submit → router.push('/fuel/purchases')
```

### Pattern C: Inline Modal Create

Used by: LinkField with quickCreate, Pump Reading inline row

```
FuelPurchaseFormView
  └── LinkField (doctype="Supplier")
        └── [+] icon → ModalDialog
              └── SupplierFormMini (minimal create form)
                    → saved → parent LinkField auto-selects new record
```

### Pattern D: Dashboard Polling

```
DashboardView (onMounted)
  ├── dashboardStore.fetchMetrics()   → immediate
  └── setInterval(fetchMetrics, 300_000)   → every 5 minutes
        (cleared on onUnmounted)
```

### Pattern E: Form with Computed Fields

Used by: Fuel Purchase (total_cost, balance), Inventory Receipt

```typescript
// In FuelPurchaseFormView.vue
const totalCost = computed(() => values.actual_quantity * values.unit_cost)
const balance   = computed(() => totalCost.value - (values.amount_paid ?? 0))

// Set in form with setFieldValue so validation sees updated values
watch(totalCost, (v) => setFieldValue('total_cost', v))
watch(balance,   (v) => setFieldValue('balance', v))
```

### Pattern F: Confirm Before Submit / Cancel

```typescript
async function submitDocument() {
  const ok = await confirm({
    title: 'Submit Fuel Purchase?',
    message: balance.value > 0
      ? `A Supplier Credit of ${formatKsh(balance.value)} will be created.`
      : 'This will update fuel stock.',
  })
  if (!ok) return
  await fuelStore.submit(doc.value.name)
  toast.success('Fuel Purchase submitted.')
}
```

---

## Appendix: Component File Reference

```
src/components/
├── layout/
│   ├── AppSidebar.vue
│   ├── SidebarNavItem.vue
│   ├── AppTopBar.vue
│   ├── Breadcrumbs.vue
│   └── UserMenu.vue
│
├── common/
│   ├── PageHeader.vue
│   ├── StatCard.vue
│   ├── AppButton.vue
│   ├── StatusBadge.vue
│   ├── ModalDialog.vue
│   ├── SlideOver.vue
│   ├── ConfirmDialog.vue
│   ├── FilterBar.vue
│   ├── EmptyState.vue
│   ├── LoadingSpinner.vue
│   ├── AlertBanner.vue
│   ├── SummaryBar.vue
│   ├── PrintButton.vue
│   └── ExportExcelButton.vue
│
├── forms/
│   ├── AppInput.vue
│   ├── AppSelect.vue
│   ├── LinkField.vue
│   ├── CurrencyInput.vue
│   ├── DatePicker.vue
│   ├── FileUpload.vue
│   ├── TextArea.vue
│   ├── CheckField.vue
│   ├── RadioGroup.vue
│   └── FormSection.vue
│
├── tables/
│   ├── DataTable.vue
│   ├── AttendanceGrid.vue
│   └── SummaryBar.vue
│
├── charts/
│   ├── LineChart.vue
│   ├── BarChart.vue
│   ├── PieChart.vue
│   ├── DonutChart.vue
│   └── ChartCard.vue
│
└── modules/
    ├── DebtAlertCard.vue
    ├── DebtPaymentForm.vue
    ├── MpesaStkButton.vue
    ├── FuelDipCalculator.vue
    ├── BulkAttendanceModal.vue
    └── CreditPaymentForm.vue
```
