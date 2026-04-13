# National Oil — Module Business Logic

> Detailed specification of each module's behavior, validations, workflows, and reports.
> Derived from analysis of the legacy PHP system (`legacy-petrol/`).

---

## Table of Contents

1. [Fuel Operations Module](#1-fuel-operations-module)
2. [Inventory Module](#2-inventory-module)
3. [Sales Module](#3-sales-module)
4. [Receivables Module](#4-receivables-module)
5. [Payables Module](#5-payables-module)
6. [Finance Module](#6-finance-module)
7. [HR Module](#7-hr-module)
8. [Integrations Module](#8-integrations-module)
9. [Dashboards & Reports](#9-dashboards--reports)

---

## 1. Fuel Operations Module

**Module path**: `national_oil/fuel_operations/`

### 1.1 Fuel Purchase

**Source files**: `legacy-petrol/stock.php`, `legacy-petrol/main.php`

#### Purpose
Records each fuel delivery from a supplier. A single delivery can cover one or more fuel types. The document is the authoritative record for stock replenishment and supplier payable creation.

#### Workflow States

```
Draft → Submitted → (Cancelled)
```

Submitted documents are immutable. Cancellation reverses all stock and financial effects.

#### Validations (on Save / Submit)

1. `actual_quantity > 0` — must have a positive delivery quantity
2. `unit_cost > 0` — must have a positive cost
3. `total_cost == unit_cost × actual_quantity` — auto-calculated, block manual override mismatch
4. `amount_paid <= total_cost` — cannot overpay on this document
5. `balance = total_cost − amount_paid` — auto-calculated
6. `code` must be unique across all Fuel Purchase records
7. `dated` cannot be a future date

#### On Submit (Controller Events)

```python
# 1. Update product stock
product = frappe.get_doc("Product", {"fuel_type": self.fuel_type})
product.quantity += self.actual_quantity
product.save()

# 2. Optionally update buying price
fuel_price = frappe.new_doc("Fuel Price")
fuel_price.fuel_type = self.fuel_type
fuel_price.buying_price = self.unit_cost
fuel_price.effective_date = self.dated
fuel_price.save()

# 3. Create supplier payable if balance outstanding
if self.balance > 0:
    credit = frappe.new_doc("Supplier Credit")
    credit.supplier = self.supplier
    credit.total_amount = self.balance
    credit.dated = self.dated
    credit.detail = f"Delivery {self.code}"
    credit.source_document = self.name
    credit.source_doctype = "Fuel Purchase"
    credit.submit()
```

#### On Cancel

- Reverse `Product.quantity` adjustment
- Cancel linked `Supplier Credit` (if status is Open)

---

### 1.2 Pump Reading

**Source**: `legacy-petrol/pumpreadings.php`

#### Purpose
Captures daily opening and closing meter readings for each pump. Used to cross-verify fuel dispensed against sales totals.

#### Validations

1. `closing_reading >= opening_reading`
2. One record per `pump_number` per `dated` (unique constraint)
3. `variance = closing_reading − opening_reading` (auto-calculated)

#### Reconciliation Logic
- Compare `SUM(variance)` for a fuel type on a date against `Sales Entry.amount / Fuel Price.selling_price_retail`
- Flag discrepancies > 1% as warnings in the Pump Reading list view

---

### 1.3 Fuel Price

**Source**: `legacy-petrol/products.php` (price columns in products table)

#### Purpose
Maintains a dated history of buying and selling prices for each fuel type.

#### Rules
- Only one `Fuel Price` record per `fuel_type` per `effective_date`
- The current price is the record with the latest `effective_date <= today`
- Price changes take effect on `effective_date` — old prices are archived, not deleted

---

## 2. Inventory Module

**Module path**: `national_oil/inventory/`

### 2.1 Product

**Source**: `legacy-petrol/products.php`, query `SELECT * FROM products`

#### Purpose
Master list of all products (fuel and non-fuel) with running stock balance.

#### Rules
- `quantity` is system-managed; direct edits are blocked for submitted documents
- Non-fuel products use `Inventory Receipt` for stock-in
- Fuel products use `Fuel Purchase` for stock-in

---

### 2.2 Inventory Receipt

**Source**: `legacy-petrol/inventory table queries`

#### Purpose
Records delivery of non-fuel stock (lubricants, accessories, shop items).

#### Validations

1. `units > 0`
2. `total_cost = units × unit_cost` (auto-calculated)
3. `balance = total_cost − amount_paid`

#### On Submit

```python
product = frappe.get_doc("Product", {"brand": self.brand})
product.quantity += self.units
product.save()

if self.balance > 0:
    # Create Supplier Credit
    ...
```

---

## 3. Sales Module

**Module path**: `national_oil/sales/`

### 3.1 Sales Entry

**Source**: `legacy-petrol/main.php` (sales table), dashboard charts in `Awetstock.php`

#### Purpose
Records daily sales — either wet stock (fuel dispensed) or other shop sales. Departments are the key cost centre.

#### sale_type Values
- **Wet Stock**: Fuel pumped at the forecourt
- **Other**: Shop/lubricant/service sales

#### Validations

1. `amount > 0`
2. `dated <= today`
3. If `payment_method = Credit`, `customer` is required

#### Department Sales Aggregation
The dashboard queries SUM(amount) grouped by department and period. In Frappe this is implemented as a **Query Report** rather than stored aggregations.

---

### 3.2 Department Sales Target

**Source**: `legacy-petrol/performance.php`, dashboard `target` / `hit` / `deviation` columns

#### Purpose
Allows managers to set expected sales targets per department per period. Actual sales are pulled dynamically from Sales Entry.

#### Deviation Calculation
```python
# In Python controller or report
actual = frappe.db.get_value(
    "Sales Entry",
    {"department": self.department, "dated": ["between", [self.period_start, self.period_end]]},
    "SUM(amount)"
)
self.hit_amount = actual or 0
self.deviation = self.hit_amount - self.target_amount
```

---

## 4. Receivables Module

**Module path**: `national_oil/receivables/`

### 4.1 Customer Debt

**Source**: `legacy-petrol/customers.php`, `adddebt.php`, `paydebts.php`, `Adebtors.php`

#### Purpose
Tracks outstanding amounts owed by customers (credit sales, fuel on account).

#### Status Transitions

```
Open → Partially Paid → Settled
     ↓
  Written Off  (manual, manager-only)
```

#### Balance Calculation

```python
# Called after every Debt Payment save/cancel
def update_balance(self):
    paid = frappe.db.get_value(
        "Debt Payment",
        {"customer_debt": self.name, "docstatus": 1},
        "SUM(amount)"
    ) or 0
    self.amount_paid = paid
    self.balance = self.payable_amount - paid
    if self.balance <= 0:
        self.status = "Settled"
    elif self.balance < self.payable_amount:
        self.status = "Partially Paid"
    else:
        self.status = "Open"
    self.db_update()
```

#### Permissions
- Cashier: can add Debt Payment but cannot modify `payable_amount`
- Accountant / Manager: full access

---

### 4.2 Debt Payment

**Source**: `legacy-petrol/paydebts.php`, `debtpayment` table

#### Purpose
Records each payment installment against a Customer Debt.

#### Validations

1. `amount > 0`
2. `amount <= customer_debt.balance` — cannot overpay beyond outstanding
3. `dated >= customer_debt.dated`

#### On Submit
- Calls `Customer Debt.update_balance()`

#### On Cancel
- Calls `Customer Debt.update_balance()`

---

## 5. Payables Module

**Module path**: `national_oil/payables/`

### 5.1 Supplier Credit

**Source**: `legacy-petrol/creditors.php`, `debts` table, `Acreditors.php`

#### Purpose
Tracks amounts owed to suppliers from credit fuel/inventory purchases. Mirrors `Customer Debt` but in the opposite direction.

#### Auto-Creation
- Created automatically by `Fuel Purchase.on_submit()` when `balance > 0`
- Created automatically by `Inventory Receipt.on_submit()` when `balance > 0`

#### Balance Calculation (same pattern as Customer Debt)

```python
def update_balance(self):
    paid = frappe.db.get_value(
        "Credit Payment",
        {"supplier_credit": self.name, "docstatus": 1},
        "SUM(amount)"
    ) or 0
    self.amount_paid = paid
    self.balance = self.total_amount - paid
    if self.balance <= 0:
        self.status = "Settled"
    ...
```

---

### 5.2 Credit Payment

**Source**: `legacy-petrol/paycredit.php`, `creditpaymentmodal.php`

#### Purpose
Records supplier credit payments (cheque, bank transfer, M-Pesa).

#### Validations
- `amount <= supplier_credit.balance`

---

## 6. Finance Module

**Module path**: `national_oil/finance/`

### 6.1 Petty Cash Entry

**Source**: `legacy-petrol/pettycash.php`

#### Purpose
Records small miscellaneous cash outflows not covered by supplier invoices.

#### Validations

1. `amount > 0`
2. `petty_cash_account.current_balance >= amount` before submission (warn, not block)

#### On Submit
- Reduces `Petty Cash Account.current_balance`

#### Reports
- Daily Petty Cash — all entries for today
- Monthly Petty Cash — grouped by description/category
- Annual Petty Cash — trend chart

---

### 6.2 Petty Cash Account

**Source**: `pettycashaccount` table in legacy

#### Purpose
Named cash float accounts (e.g., "Main Float", "Night Float"). Balance auto-calculated from entries.

---

## 7. HR Module

**Module path**: `national_oil/hr/`

**Note**: This module is independent from ERPNext's built-in HR module. DocType naming uses `no_employee` to avoid conflicts if ERPNext is later added.

### 7.1 Employee

**Source**: `legacy-petrol/worker` table, `hr/database.sql`

#### Designation Types
- `Casual` — temporary/contract workers
- `Permanent` — full-time staff

---

### 7.2 Attendance Record

**Source**: `attendance` table

#### Validations
- One record per employee per date (unique index on `employee + dated`)
- `overtime_hours >= 0`

#### Bulk Entry Support
- Monthly attendance sheet: grid view with employees as rows, dates as columns (future enhancement)

---

### 7.3 Leave Request

**Source**: `leaves` table

#### Workflow
```
Submitted by Employee → Pending
     ↓
Approved / Rejected by HR Officer / Manager
```

#### Validations
- `from_date <= to_date`
- `total_days` auto-calculated including weekends (or weekdays only — configurable)
- Overlapping leave requests for the same employee are blocked

---

### 7.4 Performance Review

**Source**: `performance` table

#### Purpose
Tracks each worker's actual performance vs target for a period. Used in the dashboard charts originally built with Morris.js.

#### Dashboard Integration
Performance data is visualised in a Frappe Dashboard with:
- Bar chart: Target vs Hit per employee
- Line chart: Deviation trend over time

---

## 8. Integrations Module

**Module path**: `national_oil/integrations/`

### 8.1 M-Pesa Integration

**Source**: `legacy-petrol/mpesa.php`, `mpesatransactions.php`

#### Flow

```
1. User initiates payment (customer or cashier)
   → POST /api/method/national_oil.integrations.api.initiate_stk_push
   → Daraja STK Push API called
   → M-Pesa Transaction created with status=Pending

2. Customer completes payment on phone

3. Safaricom calls callback URL:
   → POST /api/method/national_oil.integrations.api.mpesa_callback
   → M-Pesa Transaction updated to Confirmed
   → If linked_debt: Debt Payment created automatically
   → Customer Debt balance updated
```

#### API Methods

```python
# national_oil/integrations/api.py

@frappe.whitelist(allow_guest=False)
def initiate_stk_push(customer, amount, phone, debt_name=None):
    """Trigger M-Pesa STK Push for a customer payment."""
    ...

@frappe.whitelist(allow_guest=True)
def mpesa_callback():
    """Webhook handler for Safaricom M-Pesa C2B / STK callback."""
    payload = frappe.request.json
    # Validate, create/update M-Pesa Transaction
    ...
```

#### Security
- Callback endpoint whitelisted for Safaricom IP ranges only (configured in site_config or nginx)
- Consumer key/secret stored encrypted in `M-Pesa Settings` doctype

---

## 9. Dashboards & Reports

### 9.1 Main Dashboard (Manager Workspace)

**Source**: `legacy-petrol/main.php` chart data, `Awetstock.php`

#### Widgets

| Widget | Type | Data Source |
|---|---|---|
| Today's Sales | Number Card | `SUM(Sales Entry.amount) WHERE dated=today` |
| Monthly Sales | Number Card | `SUM(Sales Entry.amount) WHERE month=current` |
| Annual Sales | Number Card | `SUM(Sales Entry.amount) WHERE year=current` |
| Sales Trend (7 days) | Line Chart | Daily SUM(Sales Entry.amount) last 7 days |
| Fuel Stock Levels | Bar Chart | `Product.quantity` per fuel type |
| Open Customer Debts | Number Card | `COUNT(Customer Debt) WHERE status!=Settled` |
| Open Supplier Credits | Number Card | `COUNT(Supplier Credit) WHERE status!=Settled` |
| Employee Attendance | Pie Chart | Present/Absent for today |
| Department Performance | Bar Chart | Target vs Hit from Performance Review |

---

### 9.2 Reports

#### Sales Reports

| Report | Type | Filters |
|---|---|---|
| Daily Sales Summary | Query Report | Date, Department, sale_type |
| Weekly Sales Summary | Query Report | Week, Department |
| Monthly Sales Summary | Query Report | Month/Year, Department |
| Annual Sales Summary | Query Report | Year, Department |
| Wet Stock Sales | Query Report | Period (Daily/Weekly/Monthly/Annual) |
| Other Sales | Query Report | Period |

**Source PDFs**: `dailysalespdf.php`, `monthlysalespdf.php`, etc.

#### Receivables Reports

| Report | Type | Filters |
|---|---|---|
| Customer Debt Ageing | Query Report | As-Of Date, Customer |
| All Customer Debts | Query Report | Status filter |
| Debt Collection Summary | Query Report | Period |

**Source**: `alldebtspdf.php`, `Adebtors.php`

#### Payables Reports

| Report | Type | Filters |
|---|---|---|
| Supplier Payables | Query Report | Supplier, Status |
| All Credits | Query Report | Period, Supplier |

**Source**: `allcreditpdf.php`, `Acreditors.php`

#### Cash Reports

| Report | Type | Filters |
|---|---|---|
| Petty Cash — Daily | Query Report | Date |
| Petty Cash — Monthly | Query Report | Month/Year |
| Petty Cash — Annual | Query Report | Year |
| Wet Stock Cash — Daily | Query Report | Date |
| Wet Stock Cash — Monthly | Query Report | Month/Year |

**Source**: `pettycash.php`, `othercashtodaypdf.php`, etc.

#### HR Reports

| Report | Type | Filters |
|---|---|---|
| Attendance Summary | Query Report | Employee, Month |
| Performance Report | Query Report | Employee, Period |
| Leave Register | Query Report | Employee, Year |

#### Fuel Reports

| Report | Type | Filters |
|---|---|---|
| Fuel Delivery Log | Query Report | Supplier, Date Range |
| Fuel Stock Summary | Script Report | As-of-date stock levels |
| Pump Reading Reconciliation | Script Report | Pump, Date Range |

---

### 9.3 Print Formats

Replace the 25+ `*pdf.php` generators in legacy with Frappe Print Formats:

| Print Format | DocType |
|---|---|
| Fuel Delivery Receipt | Fuel Purchase |
| Customer Debt Statement | Customer Debt |
| Supplier Credit Statement | Supplier Credit |
| Petty Cash Voucher | Petty Cash Entry |
| Attendance Sheet (monthly) | Attendance Record |
| Sales Summary (monthly) | — (Report print) |
