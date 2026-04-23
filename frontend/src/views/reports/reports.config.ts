export type FilterType = 'Date' | 'Int' | 'Select' | 'Link' | 'Data'

export interface ReportFilter {
  name: string
  label: string
  type: FilterType
  /** Link: doctype name  |  Select: newline-separated options (first may be blank) */
  options?: string
  default?: string | number
  required?: boolean
}

export interface ReportConfig {
  slug: string
  name: string      // exact Frappe report_name
  category: string
  filters: ReportFilter[]
}

const today = () => new Date().toISOString().slice(0, 10)
const monthStart = () => new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10)
const thisYear = () => new Date().getFullYear()
const thisMonth = () => new Date().getMonth() + 1

export const REPORTS: ReportConfig[] = [
  // ── Sales ─────────────────────────────────────────────────
  {
    slug: 'daily-sales-summary',
    name: 'Daily Sales Summary',
    category: 'Sales',
    filters: [
      { name: 'dated', label: 'Date', type: 'Date', default: today() },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
      { name: 'sale_type', label: 'Sale Type', type: 'Select', options: '\nWet Stock\nOther' },
    ],
  },
  {
    slug: 'weekly-sales-summary',
    name: 'Weekly Sales Summary',
    category: 'Sales',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
    ],
  },
  {
    slug: 'monthly-sales-summary',
    name: 'Monthly Sales Summary',
    category: 'Sales',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear() },
      { name: 'month', label: 'Month', type: 'Select', options: '\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12' },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
    ],
  },
  {
    slug: 'annual-sales-summary',
    name: 'Annual Sales Summary',
    category: 'Sales',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear() },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
    ],
  },
  {
    slug: 'wet-stock-sales',
    name: 'Wet Stock Sales',
    category: 'Sales',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
    ],
  },
  {
    slug: 'other-sales',
    name: 'Other Sales',
    category: 'Sales',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'department', label: 'Department', type: 'Link', options: 'Department' },
    ],
  },

  // ── Receivables ────────────────────────────────────────────
  {
    slug: 'customer-debt-ageing',
    name: 'Customer Debt Ageing',
    category: 'Receivables',
    filters: [
      { name: 'as_of_date', label: 'As Of Date', type: 'Date', default: today(), required: true },
      { name: 'customer', label: 'Customer', type: 'Link', options: 'Customer' },
    ],
  },
  {
    slug: 'all-customer-debts',
    name: 'All Customer Debts',
    category: 'Receivables',
    filters: [
      { name: 'customer', label: 'Customer', type: 'Link', options: 'Customer' },
      { name: 'status', label: 'Status', type: 'Select', options: '\nOpen\nPartial\nSettled' },
    ],
  },
  {
    slug: 'debt-collection-summary',
    name: 'Debt Collection Summary',
    category: 'Receivables',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'customer', label: 'Customer', type: 'Link', options: 'Customer' },
    ],
  },

  // ── Payables ───────────────────────────────────────────────
  {
    slug: 'supplier-payables',
    name: 'Supplier Payables',
    category: 'Payables',
    filters: [
      { name: 'supplier', label: 'Supplier', type: 'Link', options: 'Supplier' },
      { name: 'status', label: 'Status', type: 'Select', options: '\nOpen\nPartial\nSettled' },
    ],
  },
  {
    slug: 'all-credits',
    name: 'All Credits',
    category: 'Payables',
    filters: [
      { name: 'supplier', label: 'Supplier', type: 'Link', options: 'Supplier' },
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
    ],
  },

  // ── Finance ────────────────────────────────────────────────
  {
    slug: 'petty-cash-daily',
    name: 'Petty Cash — Daily',
    category: 'Finance',
    filters: [
      { name: 'dated', label: 'Date', type: 'Date', default: today(), required: true },
    ],
  },
  {
    slug: 'petty-cash-monthly',
    name: 'Petty Cash — Monthly',
    category: 'Finance',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear() },
      { name: 'month', label: 'Month', type: 'Select', options: '\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12', default: thisMonth() },
    ],
  },
  {
    slug: 'petty-cash-annual',
    name: 'Petty Cash — Annual',
    category: 'Finance',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear() },
    ],
  },

  // ── Fuel Operations ────────────────────────────────────────
  {
    slug: 'fuel-delivery-log',
    name: 'Fuel Delivery Log',
    category: 'Fuel',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'supplier', label: 'Supplier', type: 'Link', options: 'Supplier' },
      { name: 'fuel_type', label: 'Fuel Type', type: 'Link', options: 'Fuel Type' },
    ],
  },
  {
    slug: 'fuel-stock-summary',
    name: 'Fuel Stock Summary',
    category: 'Fuel',
    filters: [
      { name: 'fuel_type', label: 'Fuel Type', type: 'Link', options: 'Fuel Type' },
    ],
  },
  {
    slug: 'pump-reading-reconciliation',
    name: 'Pump Reading Reconciliation',
    category: 'Fuel',
    filters: [
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
      { name: 'pump_number', label: 'Pump Number', type: 'Data' },
      { name: 'fuel_type', label: 'Fuel Type', type: 'Link', options: 'Fuel Type' },
    ],
  },

  // ── HR ─────────────────────────────────────────────────────
  {
    slug: 'attendance-summary',
    name: 'Attendance Summary',
    category: 'HR',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear(), required: true },
      {
        name: 'month',
        label: 'Month',
        type: 'Select',
        options: '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',
        default: thisMonth(),
        required: true,
      },
      { name: 'employee', label: 'Employee', type: 'Link', options: 'NO Employee' },
    ],
  },
  {
    slug: 'performance-report',
    name: 'Performance Report',
    category: 'HR',
    filters: [
      { name: 'employee', label: 'Employee', type: 'Link', options: 'NO Employee' },
      { name: 'from_date', label: 'From Date', type: 'Date', default: monthStart() },
      { name: 'to_date', label: 'To Date', type: 'Date', default: today() },
    ],
  },
  {
    slug: 'leave-register',
    name: 'Leave Register',
    category: 'HR',
    filters: [
      { name: 'year', label: 'Year', type: 'Int', default: thisYear() },
      { name: 'employee', label: 'Employee', type: 'Link', options: 'NO Employee' },
      { name: 'status', label: 'Status', type: 'Select', options: '\nPending\nApproved\nRejected' },
    ],
  },
]

export const REPORT_BY_SLUG = Object.fromEntries(REPORTS.map((r) => [r.slug, r]))

export const CATEGORIES = [...new Set(REPORTS.map((r) => r.category))]

export const REPORTS_BY_CATEGORY = CATEGORIES.reduce<Record<string, ReportConfig[]>>(
  (acc, cat) => {
    acc[cat] = REPORTS.filter((r) => r.category === cat)
    return acc
  },
  {}
)
