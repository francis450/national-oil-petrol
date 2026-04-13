# National Oil — Screen Specifications

> Every view in the Vue.js SPA, with layout, components used, data sources,
> and the legacy PHP screen it replaces.

---

## Table of Contents

1. [Login](#1-login)
2. [Dashboard](#2-dashboard)
3. [Fuel Operations](#3-fuel-operations)
   - 3.1 Fuel Purchase List
   - 3.2 Fuel Purchase Form
   - 3.3 Pump Readings
   - 3.4 Fuel Prices
4. [Inventory](#4-inventory)
5. [Sales](#5-sales)
6. [Receivables](#6-receivables)
   - 6.1 Customer List
   - 6.2 Customer Form
   - 6.3 Customer Debt List
   - 6.4 Customer Debt Detail
7. [Payables](#7-payables)
   - 7.1 Supplier List
   - 7.2 Supplier Form
   - 7.3 Supplier Credit List
   - 7.4 Supplier Credit Detail
8. [Finance](#8-finance)
9. [HR](#9-hr)
   - 9.1 Employee List
   - 9.2 Employee Form
   - 9.3 Attendance
   - 9.4 Leave Requests
   - 9.5 Performance
10. [Reports](#10-reports)

---

## 1. Login

**Route**: `/login`  
**Legacy**: `index.php`  
**Layout**: `AuthLayout`

### Layout

```
┌──────────────────────────────────────────┐
│                                          │
│        [National Oil Logo]               │
│        Petrol Station Management         │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │  Username  [_____________________]│   │
│   │  Password  [_____________________]│   │
│   │            [     Sign In        ]│   │
│   │                                  │   │
│   │  Error message (if any)          │   │
│   └──────────────────────────────────┘   │
│                                          │
└──────────────────────────────────────────┘
```

### Behaviour

- On submit → `authStore.login(usr, pwd)` → redirects to `?redirect` query param or `/`
- Show spinner on button while request in flight
- Display Frappe error message on 401

---

## 2. Dashboard

**Route**: `/`  
**Legacy**: `main.php`, `Awetstock.php`  
**Layout**: `AppLayout`

### Layout

```
PageHeader: "Dashboard"        [Refresh icon]  [Date: Today]

── Row 1: Stat Cards ──────────────────────────────────────────
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐
│ Today Sales  │ │ Month Sales  │ │ Year Sales   │ │ Fuel Stock  │
│ KSh 45,200   │ │ KSh 1.25M   │ │ KSh 8.5M    │ │ 4,250 L     │
│ ↑ 4% vs yday │ │              │ │              │ │ Petrol      │
└──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘

── Row 2: Main Charts ─────────────────────────────────────────
┌────────────────────────────────────┐ ┌───────────────────────┐
│  Sales Trend (Line Chart)          │ │  Stock Levels          │
│  Wet Stock vs Other — 7 days       │ │  (Horizontal Bar)      │
│                                    │ │  Petrol  ████░░  4250L │
│  [7D] [30D] [1Y]  tab switcher     │ │  Diesel  ████████ 8100L│
└────────────────────────────────────┘ └───────────────────────┘

── Row 3: Alerts & Performance ────────────────────────────────
┌────────────────────────────────────┐ ┌───────────────────────┐
│  Outstanding Debts                 │ │  Today's Attendance    │
│  14 open customer debts            │ │  (Donut Chart)         │
│  KSh 124,500 total outstanding     │ │  10 Present / 2 Absent │
│  [View All →]                      │ │                        │
└────────────────────────────────────┘ └───────────────────────┘

── Row 4: Performance vs Target ───────────────────────────────
┌──────────────────────────────────────────────────────────────┐
│  Department Performance — This Month  (Grouped Bar Chart)    │
│  [Forecourt]  Target: 900K  Hit: 940K  +40K ↑               │
│  [Shop]       Target: 200K  Hit: 185K  -15K ↓               │
└──────────────────────────────────────────────────────────────┘
```

### Data Sources

| Widget | API call |
|---|---|
| Stat cards | `GET /method/national_oil.api.dashboard.get_dashboard_metrics` |
| Sales trend | `GET /method/national_oil.api.dashboard.get_sales_trend?days=7` |
| Fuel stock | Embedded in metrics response |
| Attendance | Embedded in metrics response |
| Performance | `GET /resource/Performance Review` filtered to current month |

### Components Used

`StatCard`, `LineChart`, `BarChart`, `PieChart`, `DebtAlertCard`

---

## 3. Fuel Operations

### 3.1 Fuel Purchase List

**Route**: `/fuel/purchases`  
**Legacy**: `stock.php` (fuel tab), `Awetstock.php`

```
PageHeader: "Fuel Purchases"           [+ New Purchase]

FilterBar:
  [Date From ___] [Date To ___] [Supplier ▾] [Status ▾]  [Search...]

DataTable columns:
  Code | Date | Supplier | Fuel Type | Qty (L) | Total Cost | Paid | Balance | Status | Actions
  ─────────────────────────────────────────────────────────────────────────────────────
  FP-001 | 10 Apr 2026 | Total Kenya | Petrol | 10,000 L | KSh 1.85M | 1.85M | 0 | ● Paid   [View]
  FP-002 | 09 Apr 2026 | Vivo Energy  | Diesel | 15,000 L | KSh 2.25M | 1.5M | 750K | ● Open  [View]

Pagination: Showing 1–20 of 47          [< 1 2 3 >]
```

**Row actions**: View, Cancel (submitted only, manager role)

---

### 3.2 Fuel Purchase Form

**Route**: `/fuel/purchases/new` and `/fuel/purchases/:name`  
**Legacy**: `stock.php` Add Fuel modal + inline editing

```
PageHeader: "Fuel Purchase · FP-001"       [Draft ▾]      [Submit] [Cancel]

── Section: Delivery Details ──────────────────────────────────
  Code *          [FP-001________________]
  Date *          [10/04/2026____________]
  Supplier *      [Total Kenya    ▾______]   [+ Add Supplier]
  Driver          [James Mwangi   ▾______]   [+ Add Driver]
  Car Plate       [KCB 123X______________]

── Section: Fuel & Quantities ─────────────────────────────────
  Fuel Type *     [Petrol         ▾______]
  Initial Dip (cm)[145____________________]
  Final Dip (cm)  [235____________________]
  Actual Qty (L)* [10,000_________________]  ← auto from dip if both filled
  Temperature (°C)[25.4___________________]
  Density         [0.735__________________]
  Seal Condition  [Intact          ▾_____]

── Section: Financials ────────────────────────────────────────
  Unit Cost *     [KSh 185.00_____________]
  Total Cost      [KSh 1,850,000__________]  ← read-only, auto-calculated
  Amount Paid     [KSh 1,850,000__________]
  Balance         [KSh 0__________________]  ← read-only
  Payment Method  [Bank Transfer   ▾_____]

── Section: Documents ─────────────────────────────────────────
  Receipt         [📎 Upload receipt_______]
  Comments        [________________________]
                  [________________________]
```

**Behaviour**:
- `Total Cost` = `Actual Qty × Unit Cost` (computed, readonly)
- `Balance` = `Total Cost − Amount Paid` (computed, readonly)
- If `Balance > 0` on submit: toast warning "A Supplier Credit will be created for KSh X"
- Dip fields: if both `initial_dip` and `final_dip` filled, offer to auto-fill `actual_quantity` (using a density factor or simply `final−initial × tank_factor`)
- Submitted form: all fields read-only, action buttons change to [Cancel Document]

---

### 3.3 Pump Readings

**Route**: `/fuel/pump-readings`  
**Legacy**: `pumpreadings.php`

```
PageHeader: "Pump Readings"         [+ Add Reading]

FilterBar: [Date ___] [Pump ▾] [Fuel Type ▾]

DataTable:
  Date | Pump | Fuel Type | Opening | Closing | Variance (L) | Attendant | Variance %
  ────────────────────────────────────────────────────────────────────────────────────
  11 Apr | Pump 1 | Petrol | 45,230 | 47,850 | 2,620 L | Peter K. | 0.8% ✓
  11 Apr | Pump 2 | Diesel | 12,100 | 14,350 | 2,250 L | Mary N.  | 1.5% ⚠

Legend: ✓ = within 1% tolerance  ⚠ = above threshold
```

**Inline add**: clicking [+ Add Reading] expands an inline row form at the top of the table (no full-page navigation needed).

---

### 3.4 Fuel Prices

**Route**: `/fuel/prices`  
**Legacy**: price columns on `products` table, edited via `stock.php` Edit Product modal

```
PageHeader: "Fuel Prices"               [+ Set New Price]

Current Prices card:
  ┌────────────────────────────────────────────────────────────┐
  │  Fuel Type  │ Buying Price │ Retail Price │ Wholesale Price │ Effective │
  │  Petrol     │ KSh 185.00  │ KSh 210.00  │ KSh 205.00      │ 01 Apr    │
  │  Diesel     │ KSh 150.00  │ KSh 175.00  │ KSh 170.00      │ 01 Apr    │
  └────────────────────────────────────────────────────────────┘

Price History (collapsible):
  Tabular list of all historical Fuel Price records, sorted by effective_date desc
```

**Set New Price modal**: `fuel_type`, `effective_date`, `buying_price`, `selling_price_retail`, `selling_price_wholesale`

---

## 4. Inventory

**Route**: `/inventory`  
**Legacy**: `stock.php` (inventory/products tab), `creditors.php`

```
PageHeader: "Inventory"     [+ Receive Stock]

── Current Stock Levels ───────────────────────────────────────
DataTable:
  Product | Brand | Supplier | UoM | In Stock | Buying Price | Retail | Wholesale | Actions
  ────────────────────────────────────────────────────────────────────────────────────────
  Engine Oil 1L | Castrol | Total | Pieces | 240 | KSh 750 | KSh 950 | KSh 900 | [Edit Price]
  Engine Oil 4L | Castrol | Total | Pieces | 60  | KSh 2800 | KSh 3400 | KSh 3200 | [Edit Price]

── Recent Receipts ────────────────────────────────────────────
DataTable:
  Ref | Date | Brand | Supplier | Units | Total Cost | Paid | Balance | Status | Actions
```

**Inventory Receipt Form** (`/inventory/receipts/:name`):
```
  Code *          [IR-001_____________]
  Date *          [10/04/2026_________]
  Brand           [Castrol        ▾__]  [+ Add Brand]
  Supplier *      [Total Kenya    ▾__]
  UoM *           [Pieces          ▾__]
  Units *         [24________________]
  Sub-Units/Unit  [12________________]  (e.g. 12 bottles per case)
  Unit Cost *     [KSh 750____________]
  Sub-Unit Cost   [KSh 62.50__________]  ← auto
  Total Cost      [KSh 18,000_________]  ← read-only
  Amount Paid     [KSh 18,000_________]
  Balance         [KSh 0______________]  ← read-only
  Payment Method  [Cash           ▾__]
  Retail Price    [KSh 950____________]
  Wholesale Price [KSh 900____________]
  Receipt         [📎 Upload__________]
  Comments        [__________________]
```

---

## 5. Sales

### 5.1 Sales Entry List

**Route**: `/sales`  
**Legacy**: multiple report pages (daily/weekly/monthly/annual tabs in `main.php`, `Awetstock.php`)

```
PageHeader: "Sales"              [+ New Entry]

FilterBar: [Date From] [Date To] [Department ▾] [Type ▾: Wet Stock / Other] [Payment ▾]

Summary bar (above table):
  Total: KSh 1,250,000   |  Wet Stock: KSh 980,000   |  Other: KSh 270,000

DataTable:
  Date | Department | Sale Type | Amount | Payment Method | Customer | Notes | Actions
```

### 5.2 Sales Entry Form

**Route**: `/sales/new`, `/sales/:name`

```
PageHeader: "Sales Entry · SE-0042"

  Date *          [11/04/2026_________]
  Department *    [Forecourt      ▾__]
  Sale Type *     [● Wet Stock  ○ Other]
  Amount *        [KSh 45,200__________]
  Payment Method  [Cash          ▾____]
  Customer        [_____________  ▾___]  ← required only when Payment = Credit
  Notes           [___________________]

── Line Items (optional, for itemised entries) ─────────────────
  + Add Item
  [Product ▾] [Qty] [Unit Price] [Total]  [×]
                              Subtotal: KSh 45,200
```

### 5.3 Sales Targets

**Route**: `/sales/targets`  
**Legacy**: `performance` table targets, dashboard deviation metrics

```
PageHeader: "Sales Targets"            [+ Set Target]

Current Period selector: [● Daily  ○ Weekly  ○ Monthly]

DataTable:
  Department | Period Start | Target | Actual | Deviation | Variance %
  ──────────────────────────────────────────────────────────────────────
  Forecourt  | Apr 2026    | 900,000| 940,000| +40,000   | +4.4% ↑
  Shop       | Apr 2026    | 200,000| 185,000| -15,000   | -7.5% ↓

Bar chart below table: Target vs Actual per department (current period)
```

---

## 6. Receivables

### 6.1 Customer List

**Route**: `/receivables/customers`  
**Legacy**: `customers.php` (first table — customer master)

```
PageHeader: "Customers"                [+ New Customer]

FilterBar: [Search name/phone...]

DataTable:
  Name | Phone | Email | Open Debts | Total Outstanding | Actions
  ──────────────────────────────────────────────────────────────────
  John Kamau  | 0712-XXX | j@g.com | 2 debts | KSh 7,000  | [View] [Add Debt]
  Mary Wanjiku| 0722-XXX | —       | 0 debts | KSh 0      | [View]
```

### 6.2 Customer Form

**Route**: `/receivables/customers/new`, `/receivables/customers/:name`

```
PageHeader: "Customer · John Kamau"

  Customer Name * [John Kamau__________]
  Phone           [0712345678__________]
  Email           [john@gmail.com_______]
  Address         [Nairobi, Karen_______]
  Photo           [📎 Upload ID/Photo___]

── Debt Summary (read-only, shown only on existing customers) ──
  Total Payable:  KSh 15,000
  Total Paid:     KSh 8,000
  Balance:        KSh 7,000

  [View Debt History →]
```

### 6.3 Customer Debt List

**Route**: `/receivables/debts`  
**Legacy**: `Adebtors.php` (Daily/Weekly/Monthly/Annual tabs), `customers.php` debts table

```
PageHeader: "Customer Debts"           [+ New Debt]

FilterBar: [Status ▾] [Customer ▾] [Date From] [Date To]

Summary bar:
  Total Payable: KSh 850,000  |  Total Paid: KSh 726,000  |  Outstanding: KSh 124,000

DataTable:
  Ref | Customer | Date | Payable | Paid | Balance | Status      | Actions
  ────────────────────────────────────────────────────────────────────────────
  DEBT-001 | John K. | 15 Mar | 7,000 | 0      | 7,000 | ● Open         | [View] [Pay]
  DEBT-002 | Amos O. | 10 Mar | 5,000 | 5,000  | 0     | ● Settled      | [View]
  DEBT-003 | Jane N. | 08 Mar | 10,000| 4,000  | 6,000 | ● Partial      | [View] [Pay]
```

### 6.4 Customer Debt Detail

**Route**: `/receivables/debts/:name`  
**Legacy**: `paydebts.php` popup window (window.open 900×700)

```
PageHeader: "Customer Debt · DEBT-001"                   [● Open]

── Debt Info ───────────────────────────────────────────────────
  Reference Code  DEBT-001
  Customer        John Kamau                 → [View Customer]
  Date Incurred   15 Mar 2026
  Payable Amount  KSh 7,000
  Amount Paid     KSh 0
  Balance         KSh 7,000
  Receipt         [📄 receipt.pdf]

── Payment History ─────────────────────────────────────────────
  Date       | Amount    | Method   | Reference    | Actions
  ──────────────────────────────────────────────────────────────
  (no payments yet)

  [+ Record Payment]  ← opens slide-over / modal

── Record Payment (slide-over panel) ───────────────────────────
  Amount *        [KSh 7,000___________]
  Payment Method  [Cash           ▾___]
  Reference       [___________________]  (M-Pesa code, cheque no.)
  Date            [11/04/2026_________]
  Receipt         [📎 Upload__________]
  [Save Payment]
```

**M-Pesa quick-pay button**: if `payment_method = M-Pesa` and customer has a phone number:
`[Send STK Push to 0712345678]` → triggers API call and shows pending state.

---

## 7. Payables

### 7.1 Supplier List

**Route**: `/payables/suppliers`  
**Legacy**: `creditors.php` (supplier master tab)

```
PageHeader: "Suppliers"                [+ New Supplier]

DataTable:
  Name | Account | Phone | Email | Open Credits | Total Outstanding | Actions
  ──────────────────────────────────────────────────────────────────────────────
  Total Kenya  | ACC-001 | 0700-XXX | — | 2 | KSh 750,000 | [View] [Add Credit]
```

### 7.2 Supplier Form

**Route**: `/payables/suppliers/:name`

```
  Supplier Name * [Total Kenya_________]
  Account Number  [ACC-001_____________]
  Phone           [0700000000__________]
  Email           [info@total.co.ke____]
  Address         [Westlands, Nairobi__]

── Credit Summary ──────────────────────────────────────────────
  Total Credit: KSh 2,000,000  |  Paid: KSh 1,250,000  |  Outstanding: KSh 750,000
  [View Credits →]
```

### 7.3 Supplier Credit List

**Route**: `/payables/credits`  
**Legacy**: `Acreditors.php` (Today/Week/Month/Year/All Time tabs)

Mirror of Customer Debt List, with suppliers instead of customers.

```
DataTable:
  Ref | Supplier | Date | Total | Paid | Balance | Status | Source Doc | Actions
```

### 7.4 Supplier Credit Detail

**Route**: `/payables/credits/:name`

Mirror of Customer Debt Detail. Record Payment slide-over applies credit payments.

---

## 8. Finance

### 8.1 Petty Cash List

**Route**: `/finance/petty-cash`  
**Legacy**: `pettycash.php`, `Aexpenses.php`

```
PageHeader: "Petty Cash"               [+ New Entry]

FilterBar: [Date ___] [Account ▾] [Department ▾]

Summary bar:
  Today: KSh 3,450  |  This Month: KSh 42,300  |  This Year: KSh 384,000

DataTable:
  Date | Description | Amount | Department | Account | Approved By | Actions
  ──────────────────────────────────────────────────────────────────────────────
  11 Apr | Fuel for generator | KSh 2,000 | Maintenance | Main Float | J. Manager | [View]
  11 Apr | Stationery         | KSh 1,450 | Office       | Main Float | J. Manager | [View]
```

**New Entry inline form** (modal):
```
  Date *          [11/04/2026_________]
  Description *   [Fuel for generator_]
  Amount *        [KSh 2,000__________]
  Department      [Maintenance    ▾__]
  Account *       [Main Float     ▾__]
  Receipt         [📎 Upload__________]
```

### 8.2 Petty Cash Accounts

**Route**: `/finance/petty-cash/accounts`

```
PageHeader: "Petty Cash Accounts"      [+ New Account]

DataTable:
  Account Name | Balance | Last Replenished | Department | Actions
  ──────────────────────────────────────────────────────────────────
  Main Float   | KSh 15,000 | 01 Apr 2026  | —          | [Edit] [Replenish]
  Night Float  | KSh 5,000  | 05 Apr 2026  | Night Shift| [Edit] [Replenish]
```

---

## 9. HR

### 9.1 Employee List

**Route**: `/hr/employees`  
**Legacy**: `main.php` worker section

```
PageHeader: "Employees"                [+ New Employee]

FilterBar: [Search name...] [Designation ▾: Casual/Permanent] [Department ▾] [Status ▾]

DataTable:
  Name | Phone | Designation | Department | Location | Status | Actions
  ──────────────────────────────────────────────────────────────────────────
  Peter Kamau | 0712-XXX | Permanent | Forecourt | Pump 1 | ● Active | [View]
  Mary Njoki  | 0722-XXX | Casual    | Shop       | —      | ● Active | [View]
```

### 9.2 Employee Form

**Route**: `/hr/employees/:name`

```
  Employee Name * [Peter Kamau_________]
  Phone           [0712345678__________]
  Address         [Nairobi_____________]
  Location        [Pump 1______________]  (work station)
  Profession      [Pump Attendant______]
  Designation *   [● Permanent  ○ Casual]
  Department      [Forecourt      ▾___]
  ID Document     [📎 Upload ID copy___]
  Active          [☑]

── Quick Stats (read-only, existing employees) ─────────────────
  Attendance this month: 22/24 days (91.7%)
  Leave days taken:      4 days
  Last performance hit:  KSh 47,200 vs KSh 45,000 target
```

### 9.3 Attendance

**Route**: `/hr/attendance`  
**Legacy**: `attendance` table, viewed in `main.php` sidebar

```
PageHeader: "Attendance"               [Bulk Mark Attendance]

── View controls ───────────────────────────────────────────────
  [Month: April 2026 ◄ ►]    [● Grid View  ○ List View]

── Grid View (calendar-style) ──────────────────────────────────
         | 1  | 2  | 3  | ... | 30 | 31
─────────┼────┼────┼────┼─────┼────┼────
Peter K. | ✓  | ✓  | ✗  | ... | ✓  |  —
Mary N.  | ✓  | —  | ✓  | ... | ✓  |  —
James W. | ✗  | ✓  | ✓  | ... | ✓  |  —

Legend: ✓ Present  ✗ Absent  — Not a working day

[Export to Excel]
```

**Bulk Mark modal**: select date → mark all employees present → exceptions can be toggled.

### 9.4 Leave Requests

**Route**: `/hr/leave-requests`

```
PageHeader: "Leave Requests"           [+ New Request]

FilterBar: [Status ▾] [Employee ▾] [Leave Type ▾] [Date Range]

DataTable:
  Employee | Leave Type | From | To | Days | Status   | Approved By | Actions
  ──────────────────────────────────────────────────────────────────────────────
  James W. | Annual   | 20 Apr | 25 Apr | 5 | ● Pending  | —      | [Approve] [Reject]
  Mary N.  | Sick     | 09 Apr | 10 Apr | 2 | ● Approved | Manager| [View]
```

### 9.5 Performance

**Route**: `/hr/performance`  
**Legacy**: `performance` table, Morris.js charts in `main.php` / `Awetstock.php`

```
PageHeader: "Performance Reviews"      [+ Add Review]

FilterBar: [Period ▾: Daily/Weekly/Monthly] [Employee ▾] [Department ▾] [Month/Year]

── Summary Chart ───────────────────────────────────────────────
  Grouped Bar Chart: Target vs Hit per employee (current period)

── Deviation Trend ─────────────────────────────────────────────
  Line Chart: deviation over last 30 days (positive = above target)

── Detail Table ────────────────────────────────────────────────
  Employee | Date | Target | Hit | Deviation | Variance %
  ────────────────────────────────────────────────────────────────
  Peter K. | Apr 2026 | 45,000 | 47,200 | +2,200 | +4.9% ↑
  Mary N.  | Apr 2026 | 30,000 | 28,500 | -1,500 | -5.0% ↓
```

---

## 10. Reports

All reports share a common layout pattern:

```
PageHeader: "[Report Name]"            [Print / PDF]  [Export Excel]

FilterBar:  [period-specific filters]

Summary Numbers (stat cards)

Data Table (paginated, sortable)
```

### 10.1 Sales Report (`/reports/sales`)

**Legacy**: `dailysalespdf.php`, `monthlysalespdf.php`, `annualsalespdf.php`, wet stock + other variants

```
Period tabs: [Today] [This Week] [This Month] [This Year] [Custom Range]

Filters: [Department ▾] [Sale Type ▾]

Summary cards:
  Total Sales  |  Wet Stock Sales  |  Other Sales  |  No. of Entries

Line Chart: Sales per day in selected period

Table:
  Date | Department | Sale Type | Amount | Payment Method | Cumulative Total
```

### 10.2 Customer Debt Ageing (`/reports/debt-ageing`)

**Legacy**: `Adebtors.php`, `alldebtspdf.php`

```
As-of Date: [11/04/2026]   Customer Filter: [All ▾]

Summary:
  Current (0–30 days) | 31–60 days | 61–90 days | 90+ days | Total

Table:
  Customer | Reference | Invoice Date | Age (days) | Current | 31-60d | 61-90d | 90+d | Total
```

### 10.3 Supplier Payables (`/reports/payables`)

**Legacy**: `Acreditors.php`, `allcreditpdf.php`

Same structure as Debt Ageing but for suppliers.

### 10.4 Petty Cash Report (`/reports/petty-cash`)

**Legacy**: `Aexpenses.php`, `othercashtodaypdf.php`, `othercashmonthpdf.php`

```
Period tabs: [Today] [This Month] [This Year]

Table:
  Date | Description | Account | Department | Amount | Approved By

Footer total: Total expenditure: KSh X
```

### 10.5 Fuel Delivery Log (`/reports/fuel-deliveries`)

```
Filters: [Supplier ▾] [Fuel Type ▾] [Date From] [Date To]

Table:
  Ref | Date | Supplier | Driver | Fuel Type | Qty (L) | Unit Cost | Total | Paid | Balance

Footer: Total Volume: X L  |  Total Value: KSh Y
```

### 10.6 Attendance Summary (`/reports/attendance`)

**Legacy**: `hr/database.sql` queries

```
Filters: [Employee ▾] [Month ▾] [Year ▾]

Table:
  Employee | Days Present | Days Absent | Overtime Hours | Attendance %

Bar Chart: Attendance % per employee
```

---

## Appendix: Legacy Screen → Vue View Mapping

| Legacy PHP File | Vue Route |
|---|---|
| `index.php` | `/login` |
| `main.php` (dashboard section) | `/` |
| `main.php` (worker section) | `/hr/employees` |
| `Awetstock.php` | `/` (dashboard) + `/reports/sales` |
| `stock.php` (fuel tab) | `/fuel/purchases` |
| `stock.php` (inventory tab) | `/inventory` |
| `pumpreadings.php` | `/fuel/pump-readings` |
| `customers.php` | `/receivables/customers` + `/receivables/debts` |
| `customeredit.php` | `/receivables/customers/:name` |
| `adddebt.php` | `/receivables/debts/new` (modal) |
| `paydebts.php` (popup window) | `/receivables/debts/:name` (slide-over) |
| `Adebtors.php` | `/reports/debt-ageing` |
| `alldebtspdf.php` | `/reports/debt-ageing` (print) |
| `creditors.php` | `/payables/suppliers` + `/payables/credits` |
| `paycredit.php` | `/payables/credits/:name` (slide-over) |
| `Acreditors.php` | `/reports/payables` |
| `allcreditpdf.php` | `/reports/payables` (print) |
| `pettycash.php` | `/finance/petty-cash` |
| `Aexpenses.php` | `/reports/petty-cash` |
| `dailysalespdf.php` | `/reports/sales` (print, daily filter) |
| `monthlysalespdf.php` | `/reports/sales` (print, monthly filter) |
| `annualsalespdf.php` | `/reports/sales` (print, annual filter) |
| `wetstocksalestodaypdf.php` | `/reports/sales` (Wet Stock + Today) |
| `mpesa.php` / `mpesatransactions.php` | Customer Debt detail (STK push button) |
