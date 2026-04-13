# National Oil — Complete Implementation Reference

> **Single source of truth before any code is written.**
> Covers every DocType, every field (with exact Frappe properties), naming series,
> workflows, permissions, controller hooks, client scripts, reports, and build order.
>
> App: `national_oil` | Framework: Frappe 15 | DB: MariaDB

---

## Table of Contents

1. [DocType Inventory & Build Order](#1-doctype-inventory--build-order)
2. [Naming Series Conventions](#2-naming-series-conventions)
3. [Roles & Permission Matrix](#3-roles--permission-matrix)
4. [Setup / Master DocTypes](#4-setup--master-doctypes)
   - 4.1 Department
   - 4.2 Fuel Type
   - 4.3 Supplier
   - 4.4 Brand
   - 4.5 Customer
   - 4.6 Driver
5. [Fuel Operations DocTypes](#5-fuel-operations-doctypes)
   - 5.1 Fuel Purchase
   - 5.2 Pump Reading
   - 5.3 Fuel Price
6. [Inventory DocTypes](#6-inventory-doctypes)
   - 6.1 Product
   - 6.2 Inventory Receipt
7. [Sales DocTypes](#7-sales-doctypes)
   - 7.1 Sales Entry
   - 7.2 Sales Item *(child)*
   - 7.3 Department Sales Target
8. [Receivables DocTypes](#8-receivables-doctypes)
   - 8.1 Customer Debt
   - 8.2 Debt Payment
9. [Payables DocTypes](#9-payables-doctypes)
   - 9.1 Supplier Credit
   - 9.2 Credit Payment
10. [Finance DocTypes](#10-finance-doctypes)
    - 10.1 Petty Cash Account
    - 10.2 Petty Cash Entry
11. [HR DocTypes](#11-hr-doctypes)
    - 11.1 NO Employee
    - 11.2 Attendance Record
    - 11.3 Leave Request
    - 11.4 Performance Review
12. [Integration DocTypes](#12-integration-doctypes)
    - 12.1 M-Pesa Settings
    - 12.2 M-Pesa Transaction
13. [Workflow Definitions](#13-workflow-definitions)
14. [Controller Logic Summary](#14-controller-logic-summary)
15. [Client Script Summary](#15-client-script-summary)
16. [Custom Methods (Whitelisted APIs)](#16-custom-methods-whitelisted-apis)
17. [Reports](#17-reports)
18. [Print Formats](#18-print-formats)
19. [Scheduled Tasks](#19-scheduled-tasks)
20. [Workspace Configuration](#20-workspace-configuration)
21. [hooks.py Reference](#21-hookspy-reference)

---

## 1. DocType Inventory & Build Order

DocTypes must be created in dependency order — a DocType cannot link to one that doesn't exist yet.

### Build Order

```
WAVE 1 — No dependencies (pure masters)
  1.  Department
  2.  Fuel Type

WAVE 2 — Depends on Wave 1
  3.  Supplier          (no deps)
  4.  Customer          (no deps)
  5.  Brand             → Supplier
  6.  Petty Cash Account → Department
  7.  NO Employee       → Department
  8.  Product           → Fuel Type, Brand

WAVE 3 — Depends on Wave 2
  9.  Driver            → Supplier
  10. Fuel Price         → Fuel Type
  11. Sales Item (child) → Product          [child doctype, no own table per se]

WAVE 4 — Transactional DocTypes
  12. Fuel Purchase      → Supplier, Driver, Fuel Type, Brand, Product
  13. Inventory Receipt  → Brand, Supplier, Product
  14. Sales Entry        → Department, Customer  [+ child: Sales Item]
  15. Customer Debt      → Customer
  16. Supplier Credit    → Supplier            [Dynamic Link source]
  17. Petty Cash Entry   → Department, Petty Cash Account
  18. Attendance Record  → NO Employee
  19. Leave Request      → NO Employee
  20. Performance Review → NO Employee, Department
  21. Pump Reading       → Fuel Type, NO Employee, Department
  22. Department Sales Target → Department

WAVE 5 — Depends on Wave 4
  23. Debt Payment       → Customer Debt, Customer
  24. Credit Payment     → Supplier Credit, Supplier

WAVE 6 — Integrations
  25. M-Pesa Settings    (singleton)
  26. M-Pesa Transaction → Customer, Customer Debt
```

### Summary Table

| # | DocType | Module Dir | Type | Is Child | Submittable |
|---|---|---|---|---|---|
| 1 | Department | setup | Master | No | No |
| 2 | Fuel Type | setup | Master | No | No |
| 3 | Supplier | setup | Master | No | No |
| 4 | Customer | setup | Master | No | No |
| 5 | Brand | setup | Master | No | No |
| 6 | Driver | setup | Master | No | No |
| 7 | Product | inventory | Master | No | No |
| 8 | Petty Cash Account | finance | Master | No | No |
| 9 | NO Employee | hr | Master | No | No |
| 10 | Fuel Price | fuel_operations | Master | No | No |
| 11 | Fuel Purchase | fuel_operations | Transaction | No | Yes |
| 12 | Pump Reading | fuel_operations | Transaction | No | No |
| 13 | Inventory Receipt | inventory | Transaction | No | Yes |
| 14 | Sales Entry | sales | Transaction | No | Yes |
| 15 | Sales Item | sales | Child | Yes | — |
| 16 | Department Sales Target | sales | Master | No | No |
| 17 | Customer Debt | receivables | Transaction | No | Yes |
| 18 | Debt Payment | receivables | Transaction | No | Yes |
| 19 | Supplier Credit | payables | Transaction | No | Yes |
| 20 | Credit Payment | payables | Transaction | No | Yes |
| 21 | Petty Cash Entry | finance | Transaction | No | Yes |
| 22 | Attendance Record | hr | Transaction | No | No |
| 23 | Leave Request | hr | Transaction | No | No |
| 24 | Performance Review | hr | Transaction | No | No |
| 25 | M-Pesa Settings | integrations | Singleton | No | No |
| 26 | M-Pesa Transaction | integrations | Transaction | No | No |

**Total: 26 DocTypes** (25 tables + 1 child)

---

## 2. Naming Series Conventions

| DocType | autoname | Example |
|---|---|---|
| Department | `field:department_name` | `Forecourt` |
| Fuel Type | `field:fuel_type_name` | `Petrol` |
| Supplier | `field:supplier_name` | `Total Kenya` |
| Customer | `field:customer_name` | `John Kamau` |
| Brand | `field:brand_name` | `Castrol` |
| Driver | `field:driver_name` | `James Mwangi` |
| Product | `field:product_name` | `Petrol 95` |
| NO Employee | `NOE-.####` | `NOE-0001` |
| Petty Cash Account | `field:account_name` | `Main Float` |
| Fuel Price | `hash` | (system generated) |
| Fuel Purchase | `NOF-PUR-.YYYY.-.####` | `NOF-PUR-2026-0001` |
| Pump Reading | `NOF-PMP-.YYYY.-.####` | `NOF-PMP-2026-0001` |
| Inventory Receipt | `NOF-INV-.YYYY.-.####` | `NOF-INV-2026-0001` |
| Sales Entry | `NOF-SAL-.YYYY.-.####` | `NOF-SAL-2026-0001` |
| Department Sales Target | `NOF-DST-.YYYY.-.####` | `NOF-DST-2026-0001` |
| Customer Debt | `NOF-DBT-.YYYY.-.####` | `NOF-DBT-2026-0001` |
| Debt Payment | `NOF-DPT-.YYYY.-.####` | `NOF-DPT-2026-0001` |
| Supplier Credit | `NOF-CRD-.YYYY.-.####` | `NOF-CRD-2026-0001` |
| Credit Payment | `NOF-CPT-.YYYY.-.####` | `NOF-CPT-2026-0001` |
| Petty Cash Entry | `NOF-PCE-.YYYY.-.####` | `NOF-PCE-2026-0001` |
| Attendance Record | `NOF-ATT-.YYYY.-.####` | `NOF-ATT-2026-0001` |
| Leave Request | `NOF-LVE-.YYYY.-.####` | `NOF-LVE-2026-0001` |
| Performance Review | `NOF-PRF-.YYYY.-.####` | `NOF-PRF-2026-0001` |
| M-Pesa Settings | `M-Pesa Settings` (singleton) | — |
| M-Pesa Transaction | `NOF-MPT-.YYYY.-.####` | `NOF-MPT-2026-0001` |

---

## 3. Roles & Permission Matrix

### Roles to Create

```
System Manager      (built-in Frappe)
Station Manager
Pump Attendant
Cashier
Store Keeper
HR Officer
Accountant
Driver
```

### Permission Key
`R` = Read | `W` = Write | `C` = Create | `D` = Delete | `S` = Submit | `X` = Cancel | `A` = Amend | `P` = Print | `E` = Export

### Permissions Matrix

| DocType | System Mgr | Station Mgr | Pump Att. | Cashier | Store Keeper | HR Officer | Accountant | Driver |
|---|---|---|---|---|---|---|---|---|
| **Department** | RWCD | R | R | R | R | R | R | — |
| **Fuel Type** | RWCD | R | R | — | R | — | R | — |
| **Supplier** | RWCD | RWCD | — | — | RWCD | — | RW | — |
| **Customer** | RWCD | RWCD | — | RWCD | — | — | RW | — |
| **Brand** | RWCD | RWCD | — | — | RWCD | — | R | — |
| **Driver** | RWCD | RWCD | — | — | RW | — | R | R (own) |
| **Product** | RWCD | RWCD | R | R | RWCD | — | R | — |
| **Petty Cash Account** | RWCD | RWCD | — | — | — | — | RW | — |
| **NO Employee** | RWCD | RWCD | — | — | — | RWCD | R | R (own) |
| **Fuel Price** | RWCD | RWCD | — | — | — | — | R | — |
| **Fuel Purchase** | RWCDSX | RWCDSX | — | — | RWCDS | — | R | — |
| **Pump Reading** | RWCD | RWCD | RWCD | — | — | — | R | — |
| **Inventory Receipt** | RWCDSX | RWCDSX | — | — | RWCDS | — | R | — |
| **Sales Entry** | RWCDSX | RWCDSX | RWCS | RWCS | — | — | R | — |
| **Department Sales Target** | RWCD | RWCD | — | — | — | — | R | — |
| **Customer Debt** | RWCDSX | RWCDSX | — | RCS | — | — | RWCS | — |
| **Debt Payment** | RWCDSX | RWCDSX | — | RWCS | — | — | RWCS | — |
| **Supplier Credit** | RWCDSX | RWCDSX | — | — | — | — | RWCS | — |
| **Credit Payment** | RWCDSX | RWCDSX | — | — | — | — | RWCS | — |
| **Petty Cash Entry** | RWCDSX | RWCDSX | — | RWCS | — | — | RWCS | — |
| **Attendance Record** | RWCD | RWCD | — | — | — | RWCD | R | — |
| **Leave Request** | RWCD | RWCDX | — | — | — | RWCD | R | RC (own) |
| **Performance Review** | RWCD | RWCD | — | — | — | RWCD | R | — |
| **M-Pesa Settings** | RWCD | R | — | — | — | — | — | — |
| **M-Pesa Transaction** | RWCD | RCD | — | R | — | — | R | — |

> **Note on "own" rows**: Use Frappe's `if_owner` flag on the role permission row.

---

## 4. Setup / Master DocTypes

### 4.1 Department

**Module**: `national_oil/setup/`
**Is Single**: No | **Is Submittable**: No | **Track Changes**: No
**autoname**: `field:department_name`
**Title Field**: `department_name`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `department_name` | Department Name | Data | — | 1 | 1 | 1 | |
| 2 | `description` | Description | Small Text | — | 0 | 0 | 0 | |

**Indexes**: `department_name` (unique enforced by autoname)

---

### 4.2 Fuel Type

**Module**: `national_oil/setup/`
**autoname**: `field:fuel_type_name`
**Title Field**: `fuel_type_name`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `fuel_type_name` | Fuel Type Name | Data | — | 1 | 1 | e.g. Petrol, Diesel, Kerosene |
| 2 | `unit_of_measure` | Unit of Measure | Select | Litres\nKg\nCubic Metres | 1 | 1 | |
| 3 | `description` | Description | Small Text | — | 0 | 0 | |

---

### 4.3 Supplier

**Module**: `national_oil/setup/`
**autoname**: `field:supplier_name`
**Title Field**: `supplier_name`
**Search Fields**: `supplier_name, phone, email`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `supplier_name` | Supplier Name | Data | — | 1 | 1 | 1 | |
| 2 | `col_break_1` | — | Column Break | — | — | — | — | Layout |
| 3 | `account_number` | Account Number | Data | — | 0 | 0 | 0 | Bank/payment account |
| 4 | `section_contact` | Contact Details | Section Break | — | — | — | — | |
| 5 | `phone` | Phone | Data | — | 0 | 1 | 0 | |
| 6 | `email` | Email | Data | — | 0 | 0 | 0 | |
| 7 | `col_break_2` | — | Column Break | — | — | — | — | |
| 8 | `address` | Address | Small Text | — | 0 | 0 | 0 | |

---

### 4.4 Brand

**Module**: `national_oil/setup/`
**autoname**: `field:brand_name`
**Title Field**: `brand_name`
**Search Fields**: `brand_name, supplier`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `brand_name` | Brand Name | Data | — | 1 | 1 | |
| 2 | `supplier` | Supplier | Link | Supplier | 1 | 1 | |
| 3 | `brand_identity` | Brand Identity | Data | — | 0 | 0 | Auto-set: `brand_name – supplier`; read_only=1 |

**Unique constraint**: `brand_name` per `supplier` (validate in controller)

---

### 4.5 Customer

**Module**: `national_oil/setup/`
**autoname**: `field:customer_name`
**Title Field**: `customer_name`
**Search Fields**: `customer_name, phone, email`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `customer_name` | Customer Name | Data | — | 1 | 1 | 1 | |
| 2 | `phone` | Phone | Data | — | 0 | 1 | 0 | |
| 3 | `col_break_1` | — | Column Break | — | — | — | — | |
| 4 | `email` | Email | Data | — | 0 | 0 | 0 | |
| 5 | `section_details` | — | Section Break | — | — | — | — | |
| 6 | `address` | Address | Small Text | — | 0 | 0 | 0 | |
| 7 | `col_break_2` | — | Column Break | — | — | — | — | |
| 8 | `customer_photo` | Photo / ID | Attach Image | — | 0 | 0 | 0 | |

---

### 4.6 Driver

**Module**: `national_oil/setup/`
**autoname**: `field:driver_name`
**Title Field**: `driver_name`
**Search Fields**: `driver_name, phone, car_plate`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `driver_name` | Driver Name | Data | — | 1 | 1 | |
| 2 | `phone` | Phone | Data | — | 0 | 1 | |
| 3 | `col_break_1` | — | Column Break | — | — | — | |
| 4 | `email` | Email | Data | — | 0 | 0 | |
| 5 | `car_plate` | Vehicle Registration | Data | — | 0 | 1 | |
| 6 | `section_supplier` | Supplier Details | Section Break | — | — | — | |
| 7 | `supplier` | Associated Supplier | Link | Supplier | 0 | 1 | |
| 8 | `supplier_contact` | Supplier Contact | Data | — | 0 | 0 | Direct contact person at supplier |

---

## 5. Fuel Operations DocTypes

### 5.1 Fuel Purchase

**Module**: `national_oil/fuel_operations/`
**autoname**: `NOF-PUR-.YYYY.-.####`
**Is Submittable**: Yes
**Title Field**: `code`
**Track Changes**: Yes
**Search Fields**: `code, supplier, fuel_type`

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | bold | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **— Section: Delivery Details —** |
| 1 | `code` | Delivery Reference | Data | — | 1 | 0 | 1 | 1 | Unique, no_copy=1 |
| 2 | `dated` | Delivery Date | Date | — | 1 | 0 | 1 | 0 | default=Today |
| 3 | `col_break_1` | — | Column Break | — | — | — | — | — | |
| 4 | `supplier` | Supplier | Link | Supplier | 1 | 0 | 1 | 0 | |
| 5 | `driver` | Driver | Link | Driver | 0 | 0 | 0 | 0 | |
| 6 | `car_plate` | Vehicle Plate | Data | — | 0 | 0 | 0 | 0 | fetch_from=`driver.car_plate` |
| **— Section: Fuel Details —** |
| 7 | `section_fuel` | Fuel & Quantities | Section Break | — | — | — | — | — | |
| 8 | `fuel_type` | Fuel Type | Link | Fuel Type | 1 | 0 | 1 | 0 | |
| 9 | `brand` | Brand | Link | Brand | 0 | 0 | 0 | 0 | |
| 10 | `unit_of_measure` | Unit of Measure | Select | Litres\nKg | 1 | 0 | 0 | 0 | default=Litres |
| 11 | `col_break_2` | — | Column Break | — | — | — | — | — | |
| 12 | `actual_quantity` | Actual Quantity | Float | — | 1 | 0 | 1 | 0 | precision=2 |
| **— Section: Dip Measurements —** |
| 13 | `section_dip` | Dip Measurements | Section Break | — | — | — | — | — | collapsible=1 |
| 14 | `initial_dip` | Initial Dip (cm) | Float | — | 0 | 0 | 0 | 0 | precision=2 |
| 15 | `final_dip` | Final Dip (cm) | Float | — | 0 | 0 | 0 | 0 | precision=2 |
| 16 | `col_break_3` | — | Column Break | — | — | — | — | — | |
| 17 | `temperature` | Temperature (°C) | Float | — | 0 | 0 | 0 | 0 | precision=1 |
| 18 | `density` | Density | Float | — | 0 | 0 | 0 | 0 | precision=4 |
| 19 | `seal_condition` | Seal Condition | Select | Intact\nBroken\nMissing\nNot Checked | 0 | 0 | 0 | 0 | default=Intact |
| **— Section: Financials —** |
| 20 | `section_finance` | Financials | Section Break | — | — | — | — | — | |
| 21 | `unit_cost` | Unit Cost (per Litre) | Currency | — | 1 | 0 | 0 | 0 | precision=4 |
| 22 | `total_cost` | Total Cost | Currency | — | 1 | 1 | 1 | 1 | read_only=1; auto=unit_cost×actual_quantity |
| 23 | `col_break_4` | — | Column Break | — | — | — | — | — | |
| 24 | `amount_paid` | Amount Paid | Currency | — | 0 | 0 | 0 | 0 | default=0 |
| 25 | `balance` | Balance | Currency | — | 0 | 1 | 1 | 0 | read_only=1; auto=total_cost−amount_paid |
| 26 | `payment_method` | Payment Method | Select | Cash\nCheque\nM-Pesa\nBank Transfer\nCredit | 0 | 0 | 0 | 0 | |
| **— Section: Documents —** |
| 27 | `section_docs` | Supporting Documents | Section Break | — | — | — | — | — | collapsible=1 |
| 28 | `receipt` | Receipt / Waybill | Attach | — | 0 | 0 | 0 | 0 | |
| 29 | `comments` | Comments | Small Text | — | 0 | 0 | 0 | 0 | |
| **— Amended From (system) —** |
| 30 | `amended_from` | Amended From | Link | Fuel Purchase | 0 | 1 | 0 | 0 | Frappe standard |

**Unique constraint**: `code` field — add `unique=1` on field.
**Validations** (controller `validate`):
- `actual_quantity > 0`
- `unit_cost > 0`
- `amount_paid <= total_cost`
- `dated <= today`

**on_submit events**:
1. Update `Product.quantity` for matching `fuel_type`
2. If `balance > 0`: create `Supplier Credit`

**on_cancel events**:
1. Reverse `Product.quantity`
2. Cancel linked `Supplier Credit`

---

### 5.2 Pump Reading

**Module**: `national_oil/fuel_operations/`
**autoname**: `NOF-PMP-.YYYY.-.####`
**Is Submittable**: No
**Title Field**: `pump_number`

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 2 | `pump_number` | Pump Number | Data | — | 1 | 0 | 1 | e.g. Pump 1, Pump 2 |
| 3 | `fuel_type` | Fuel Type | Link | Fuel Type | 1 | 0 | 1 | |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `opening_reading` | Opening Reading | Float | — | 1 | 0 | 0 | precision=2 |
| 6 | `closing_reading` | Closing Reading | Float | — | 1 | 0 | 0 | precision=2 |
| 7 | `variance` | Variance (L) | Float | — | 0 | 1 | 1 | read_only=1; auto=closing−opening |
| 8 | `section_staff` | Staff | Section Break | — | — | — | — | collapsible=1 |
| 9 | `attendant` | Attendant | Link | NO Employee | 0 | 0 | 0 | |
| 10 | `department` | Department | Link | Department | 0 | 0 | 0 | |
| 11 | `notes` | Notes | Small Text | — | 0 | 0 | 0 | |

**Unique constraint**: `pump_number` + `dated` (validate in controller)

---

### 5.3 Fuel Price

**Module**: `national_oil/fuel_operations/`
**autoname**: `hash`
**Is Submittable**: No
**Title Field**: `fuel_type`

| # | fieldname | label | fieldtype | options | reqd | in_list_view | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `fuel_type` | Fuel Type | Link | Fuel Type | 1 | 1 | |
| 2 | `effective_date` | Effective Date | Date | — | 1 | 1 | default=Today |
| 3 | `section_prices` | Prices | Section Break | — | — | — | |
| 4 | `buying_price` | Buying Price (per Litre) | Currency | — | 1 | 1 | precision=4 |
| 5 | `selling_price_retail` | Retail Selling Price | Currency | — | 1 | 1 | precision=4 |
| 6 | `col_break_1` | — | Column Break | — | — | — | |
| 7 | `selling_price_wholesale` | Wholesale Price | Currency | — | 0 | 0 | precision=4 |
| 8 | `set_by` | Set By | Link | User | 0 | 0 | read_only=1; default=frappe.session.user |

**Unique constraint**: `fuel_type` + `effective_date` (validate in controller)

---

## 6. Inventory DocTypes

### 6.1 Product

**Module**: `national_oil/inventory/`
**autoname**: `field:product_name`
**Is Submittable**: No
**Title Field**: `product_name`
**Search Fields**: `product_name, fuel_type, brand`

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `product_name` | Product Name | Data | — | 1 | 0 | 1 | |
| 2 | `is_fuel` | Is Fuel Product | Check | — | 0 | 0 | 0 | default=0 |
| 3 | `fuel_type` | Fuel Type | Link | Fuel Type | 0 | 0 | 0 | depends_on=`eval:doc.is_fuel==1` |
| 4 | `brand` | Brand | Link | Brand | 0 | 0 | 1 | |
| 5 | `unit_of_measure` | Unit of Measure | Select | Litres\nPieces\nKg\nBoxes\nCartons | 1 | 0 | 1 | |
| 6 | `col_break_1` | — | Column Break | — | — | — | — | |
| 7 | `quantity` | Current Stock | Float | — | 0 | 1 | 1 | read_only=1; system-managed; precision=2 |
| 8 | `section_pricing` | Pricing | Section Break | — | — | — | — | |
| 9 | `buying_price` | Buying Price | Currency | — | 0 | 0 | 0 | |
| 10 | `selling_price` | Retail Selling Price | Currency | — | 0 | 0 | 1 | |
| 11 | `col_break_2` | — | Column Break | — | — | — | — | |
| 12 | `selling_price_wholesale` | Wholesale Price | Currency | — | 0 | 0 | 0 | |

---

### 6.2 Inventory Receipt

**Module**: `national_oil/inventory/`
**autoname**: `NOF-INV-.YYYY.-.####`
**Is Submittable**: Yes
**Title Field**: `name`
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `code` | Receipt Reference | Data | — | 1 | 0 | 1 | unique=1; no_copy=1 |
| 2 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 3 | `supplier` | Supplier | Link | Supplier | 1 | 0 | 1 | |
| 4 | `brand` | Brand | Link | Brand | 0 | 0 | 0 | |
| 5 | `section_quantities` | Quantities | Section Break | — | — | — | — | |
| 6 | `unit_of_measure` | Unit of Measure | Select | Pieces\nLitres\nKg\nBoxes\nCartons | 1 | 0 | 0 | |
| 7 | `units` | Units Received | Int | — | 1 | 0 | 1 | |
| 8 | `subunits_per_unit` | Sub-Units Per Unit | Int | — | 0 | 0 | 0 | e.g. 12 bottles per case |
| 9 | `col_break_1` | — | Column Break | — | — | — | — | |
| 10 | `unit_cost` | Unit Cost | Currency | — | 1 | 0 | 1 | |
| 11 | `subunit_cost` | Sub-Unit Cost | Currency | — | 0 | 1 | 0 | read_only=1; auto=unit_cost / subunits_per_unit |
| 12 | `total_cost` | Total Cost | Currency | — | 1 | 1 | 1 | read_only=1; auto=units×unit_cost |
| 13 | `section_payment` | Payment | Section Break | — | — | — | — | |
| 14 | `amount_paid` | Amount Paid | Currency | — | 0 | 0 | 0 | default=0 |
| 15 | `balance` | Balance | Currency | — | 0 | 1 | 1 | read_only=1; auto=total_cost−amount_paid |
| 16 | `payment_method` | Payment Method | Select | Cash\nCheque\nM-Pesa\nBank Transfer\nCredit | 0 | 0 | 0 | |
| 17 | `section_pricing` | Sale Pricing | Section Break | — | — | — | — | collapsible=1 |
| 18 | `selling_price_retail` | Retail Price | Currency | — | 0 | 0 | 0 | |
| 19 | `selling_price_wholesale` | Wholesale Price | Currency | — | 0 | 0 | 0 | |
| 20 | `section_docs` | Documents | Section Break | — | — | — | — | collapsible=1 |
| 21 | `receipt` | Receipt | Attach | — | 0 | 0 | 0 | |
| 22 | `comments` | Comments | Small Text | — | 0 | 0 | 0 | |
| 23 | `amended_from` | Amended From | Link | Inventory Receipt | 0 | 1 | 0 | Frappe standard |

**on_submit**: Update `Product.quantity` for matching `brand`; create `Supplier Credit` if `balance > 0`
**on_cancel**: Reverse `Product.quantity`; cancel linked `Supplier Credit`

---

## 7. Sales DocTypes

### 7.1 Sales Entry

**Module**: `national_oil/sales/`
**autoname**: `NOF-SAL-.YYYY.-.####`
**Is Submittable**: Yes
**Title Field**: `name`
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 2 | `department` | Department | Link | Department | 1 | 0 | 1 | |
| 3 | `sale_type` | Sale Type | Select | Wet Stock\nOther | 1 | 0 | 1 | default=Wet Stock |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `amount` | Total Amount | Currency | — | 1 | 0 | 1 | bold=1 |
| 6 | `payment_method` | Payment Method | Select | Cash\nM-Pesa\nCredit\nBank Transfer | 0 | 0 | 1 | default=Cash |
| 7 | `customer` | Customer | Link | Customer | 0 | 0 | 0 | depends_on=`eval:doc.payment_method=='Credit'`; mandatory_depends_on=same |
| 8 | `section_items` | Line Items | Section Break | — | — | — | — | collapsible=1 |
| 9 | `items` | Items | Table | Sales Item | 0 | 0 | 0 | child table |
| 10 | `notes` | Notes | Small Text | — | 0 | 0 | 0 | |
| 11 | `amended_from` | Amended From | Link | Sales Entry | 0 | 1 | 0 | |

**Validations**: `amount > 0`; `dated <= today`; if `payment_method=Credit` then `customer` required

---

### 7.2 Sales Item *(Child DocType)*

**Module**: `national_oil/sales/`
**Is Child Table**: Yes (parent: Sales Entry)
**autoname**: (Frappe manages child naming)

| # | fieldname | label | fieldtype | options | reqd | in_list_view | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `product` | Product | Link | Product | 1 | 1 | |
| 2 | `quantity` | Quantity | Float | — | 1 | 1 | precision=2 |
| 3 | `unit_price` | Unit Price | Currency | — | 1 | 1 | fetch_from=`product.selling_price` |
| 4 | `total` | Total | Currency | — | 0 | 1 | read_only=1; auto=quantity×unit_price |

---

### 7.3 Department Sales Target

**Module**: `national_oil/sales/`
**autoname**: `NOF-DST-.YYYY.-.####`
**Is Submittable**: No

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `department` | Department | Link | Department | 1 | 0 | 1 | |
| 2 | `period` | Period Type | Select | Daily\nWeekly\nMonthly | 1 | 0 | 1 | |
| 3 | `period_start` | Period Start Date | Date | — | 1 | 0 | 1 | |
| 4 | `period_end` | Period End Date | Date | — | 1 | 0 | 0 | auto from period_start + period |
| 5 | `col_break_1` | — | Column Break | — | — | — | — | |
| 6 | `target_amount` | Target Amount | Currency | — | 1 | 0 | 1 | |
| 7 | `hit_amount` | Actual (Hit) | Currency | — | 0 | 1 | 1 | read_only=1; computed via report |
| 8 | `deviation` | Deviation | Currency | — | 0 | 1 | 1 | read_only=1; hit−target |

---

## 8. Receivables DocTypes

### 8.1 Customer Debt

**Module**: `national_oil/receivables/`
**autoname**: `NOF-DBT-.YYYY.-.####`
**Is Submittable**: Yes
**Title Field**: `name`
**Track Changes**: Yes
**Search Fields**: `name, customer, code`

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | bold | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `code` | Reference Code | Data | — | 1 | 0 | 1 | 0 | no_copy=1 |
| 2 | `customer` | Customer | Link | Customer | 1 | 0 | 1 | 1 | |
| 3 | `dated` | Date Incurred | Date | — | 1 | 0 | 1 | 0 | default=Today |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | — | |
| 5 | `status` | Status | Select | Open\nPartially Paid\nSettled\nWritten Off | 0 | 1 | 1 | 0 | read_only=1; system-managed; default=Open |
| 6 | `section_amounts` | Amounts | Section Break | — | — | — | — | — | |
| 7 | `payable_amount` | Payable Amount | Currency | — | 1 | 0 | 1 | 1 | |
| 8 | `amount_paid` | Amount Paid | Currency | — | 0 | 1 | 1 | 0 | read_only=1; auto-aggregated |
| 9 | `balance` | Outstanding Balance | Currency | — | 0 | 1 | 1 | 1 | read_only=1; auto |
| 10 | `section_docs` | Documents | Section Break | — | — | — | — | — | collapsible=1 |
| 11 | `receipt` | Supporting Document | Attach | — | 0 | 0 | 0 | 0 | |
| 12 | `notes` | Notes | Small Text | — | 0 | 0 | 0 | 0 | |
| 13 | `amended_from` | Amended From | Link | Customer Debt | 0 | 1 | 0 | 0 | |

**`status` is always read_only — set programmatically.**
**Permissions note**: Cashier role has `permlevel=1` on `payable_amount` (read-only after creation).

---

### 8.2 Debt Payment

**Module**: `national_oil/receivables/`
**autoname**: `NOF-DPT-.YYYY.-.####`
**Is Submittable**: Yes
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `customer_debt` | Customer Debt | Link | Customer Debt | 1 | 0 | 1 | |
| 2 | `customer` | Customer | Link | Customer | 1 | 1 | 1 | read_only=1; fetch_from=`customer_debt.customer` |
| 3 | `dated` | Payment Date | Date | — | 1 | 0 | 1 | default=Today |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `amount` | Amount Paid | Currency | — | 1 | 0 | 1 | bold=1 |
| 6 | `payment_method` | Payment Method | Select | Cash\nM-Pesa\nBank Transfer\nCheque | 0 | 0 | 1 | default=Cash |
| 7 | `reference` | Reference | Data | — | 0 | 0 | 0 | M-Pesa code / cheque no. |
| 8 | `section_docs` | — | Section Break | — | — | — | — | collapsible=1 |
| 9 | `receipt` | Receipt | Attach | — | 0 | 0 | 0 | |
| 10 | `amended_from` | Amended From | Link | Debt Payment | 0 | 1 | 0 | |

**Validations**: `amount > 0`; `amount <= customer_debt.balance`; `dated >= customer_debt.dated`
**on_submit**: call `customer_debt.update_balance()`
**on_cancel**: call `customer_debt.update_balance()`

---

## 9. Payables DocTypes

### 9.1 Supplier Credit

**Module**: `national_oil/payables/`
**autoname**: `NOF-CRD-.YYYY.-.####`
**Is Submittable**: Yes
**Track Changes**: Yes
**Search Fields**: `name, supplier, code`

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `code` | Reference Code | Data | — | 1 | 0 | 1 | no_copy=1 |
| 2 | `supplier` | Supplier | Link | Supplier | 1 | 0 | 1 | bold=1 |
| 3 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 4 | `status` | Status | Select | Open\nPartially Paid\nSettled | 0 | 1 | 1 | read_only=1; default=Open |
| 5 | `detail` | Description | Small Text | — | 1 | 0 | 0 | |
| 6 | `section_amounts` | Amounts | Section Break | — | — | — | — | |
| 7 | `total_amount` | Total Credit Amount | Currency | — | 1 | 0 | 1 | bold=1 |
| 8 | `amount_paid` | Amount Paid | Currency | — | 0 | 1 | 1 | read_only=1; auto-aggregated |
| 9 | `balance` | Outstanding Balance | Currency | — | 0 | 1 | 1 | read_only=1 |
| 10 | `section_source` | Source Document | Section Break | — | — | — | — | collapsible=1 |
| 11 | `source_doctype` | Source DocType | Data | — | 0 | 1 | 0 | read_only=1; system-set |
| 12 | `source_document` | Source Document | Dynamic Link | source_doctype | 0 | 1 | 0 | read_only=1; system-set |
| 13 | `amended_from` | Amended From | Link | Supplier Credit | 0 | 1 | 0 | |

---

### 9.2 Credit Payment

**Module**: `national_oil/payables/`
**autoname**: `NOF-CPT-.YYYY.-.####`
**Is Submittable**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `supplier_credit` | Supplier Credit | Link | Supplier Credit | 1 | 0 | 1 | |
| 2 | `supplier` | Supplier | Link | Supplier | 1 | 1 | 1 | read_only=1; fetch_from=`supplier_credit.supplier` |
| 3 | `dated` | Payment Date | Date | — | 1 | 0 | 1 | default=Today |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `amount` | Amount Paid | Currency | — | 1 | 0 | 1 | bold=1 |
| 6 | `payment_method` | Payment Method | Select | Cash\nCheque\nM-Pesa\nBank Transfer | 0 | 0 | 1 | |
| 7 | `reference` | Reference | Data | — | 0 | 0 | 0 | |
| 8 | `section_docs` | — | Section Break | — | — | — | — | collapsible=1 |
| 9 | `receipt` | Receipt | Attach | — | 0 | 0 | 0 | |
| 10 | `amended_from` | Amended From | Link | Credit Payment | 0 | 1 | 0 | |

**Validations**: `amount > 0`; `amount <= supplier_credit.balance`
**on_submit**: call `supplier_credit.update_balance()`
**on_cancel**: call `supplier_credit.update_balance()`

---

## 10. Finance DocTypes

### 10.1 Petty Cash Account

**Module**: `national_oil/finance/`
**autoname**: `field:account_name`
**Is Submittable**: No

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `account_name` | Account Name | Data | — | 1 | 0 | 1 | |
| 2 | `current_balance` | Current Balance | Currency | — | 0 | 1 | 1 | read_only=1; computed from entries |
| 3 | `col_break_1` | — | Column Break | — | — | — | — | |
| 4 | `last_replenished` | Last Replenished | Date | — | 0 | 0 | 1 | |
| 5 | `department` | Department | Link | Department | 0 | 0 | 0 | |

---

### 10.2 Petty Cash Entry

**Module**: `national_oil/finance/`
**autoname**: `NOF-PCE-.YYYY.-.####`
**Is Submittable**: Yes
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 2 | `description` | Description | Data | — | 1 | 0 | 1 | |
| 3 | `amount` | Amount | Currency | — | 1 | 0 | 1 | bold=1 |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `petty_cash_account` | Petty Cash Account | Link | Petty Cash Account | 1 | 0 | 1 | |
| 6 | `department` | Department | Link | Department | 0 | 0 | 1 | |
| 7 | `section_approval` | Approval | Section Break | — | — | — | — | collapsible=1 |
| 8 | `approved_by` | Approved By | Link | User | 0 | 0 | 0 | |
| 9 | `section_docs` | — | Section Break | — | — | — | — | collapsible=1 |
| 10 | `receipt` | Receipt | Attach | — | 0 | 0 | 0 | |
| 11 | `amended_from` | Amended From | Link | Petty Cash Entry | 0 | 1 | 0 | |

**Validations**: `amount > 0`; warn (not block) if `petty_cash_account.current_balance < amount`
**on_submit**: decrement `Petty Cash Account.current_balance` by `amount`
**on_cancel**: increment `Petty Cash Account.current_balance` by `amount`

---

## 11. HR DocTypes

### 11.1 NO Employee

**Module**: `national_oil/hr/`
**autoname**: `NOE-.####`
**Is Submittable**: No
**Title Field**: `employee_name`
**Search Fields**: `employee_name, phone, designation`

> Named `NO Employee` (prefix avoids clash with ERPNext `Employee` if later installed).

| # | fieldname | label | fieldtype | options | reqd | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `employee_name` | Employee Name | Data | — | 1 | 1 | 1 | |
| 2 | `designation` | Designation | Select | Permanent\nCasual | 1 | 1 | 1 | |
| 3 | `department` | Department | Link | Department | 0 | 1 | 1 | |
| 4 | `is_active` | Active | Check | — | 0 | 1 | 1 | default=1 |
| 5 | `section_contact` | Contact | Section Break | — | — | — | — | |
| 6 | `phone` | Phone | Data | — | 0 | 1 | 0 | |
| 7 | `col_break_1` | — | Column Break | — | — | — | — | |
| 8 | `address` | Address | Small Text | — | 0 | 0 | 0 | |
| 9 | `section_work` | Work Details | Section Break | — | — | — | — | |
| 10 | `location` | Work Location / Station | Data | — | 0 | 0 | 0 | |
| 11 | `profession` | Profession / Job Title | Data | — | 0 | 0 | 0 | |
| 12 | `section_docs` | Documents | Section Break | — | — | — | — | collapsible=1 |
| 13 | `id_document` | National ID / Passport | Attach | — | 0 | 0 | 0 | |

---

### 11.2 Attendance Record

**Module**: `national_oil/hr/`
**autoname**: `NOF-ATT-.YYYY.-.####`
**Is Submittable**: No

| # | fieldname | label | fieldtype | options | reqd | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `employee` | Employee | Link | NO Employee | 1 | 1 | 1 | |
| 2 | `dated` | Date | Date | — | 1 | 1 | 0 | default=Today |
| 3 | `status` | Status | Select | Present\nAbsent\nLate\nHalf Day | 1 | 1 | 1 | default=Present |
| 4 | `col_break_1` | — | Column Break | — | — | — | — | |
| 5 | `overtime_hours` | Overtime Hours | Float | — | 0 | 0 | 0 | default=0; precision=1 |
| 6 | `notes` | Notes | Small Text | — | 0 | 0 | 0 | |

**Unique constraint**: `employee` + `dated` (validate in controller; show friendly error)

---

### 11.3 Leave Request

**Module**: `national_oil/hr/`
**autoname**: `NOF-LVE-.YYYY.-.####`
**Is Submittable**: No
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | in_standard_filter | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `employee` | Employee | Link | NO Employee | 1 | 0 | 1 | 1 | |
| 2 | `leave_type` | Leave Type | Select | Annual\nSick\nEmergency\nUnpaid\nMaternity\nPaternity | 1 | 0 | 1 | 1 | |
| 3 | `status` | Status | Select | Pending\nApproved\nRejected | 0 | 0 | 1 | 1 | default=Pending |
| 4 | `section_dates` | Dates | Section Break | — | — | — | — | — | |
| 5 | `from_date` | From Date | Date | — | 1 | 0 | 1 | 0 | |
| 6 | `to_date` | To Date | Date | — | 1 | 0 | 1 | 0 | |
| 7 | `total_days` | Total Days | Int | — | 0 | 1 | 1 | 0 | read_only=1; auto=to_date−from_date+1 |
| 8 | `col_break_1` | — | Column Break | — | — | — | — | — | |
| 9 | `reason` | Reason | Small Text | — | 0 | 0 | 0 | 0 | |
| 10 | `section_approval` | Approval | Section Break | — | — | — | — | — | collapsible=1 |
| 11 | `approved_by` | Approved / Rejected By | Link | User | 0 | 0 | 0 | 0 | |
| 12 | `approval_notes` | Approval Notes | Small Text | — | 0 | 0 | 0 | 0 | |

**Validations**: `from_date <= to_date`; no overlapping approved leaves for same employee.

---

### 11.4 Performance Review

**Module**: `national_oil/hr/`
**autoname**: `NOF-PRF-.YYYY.-.####`
**Is Submittable**: No

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `employee` | Employee | Link | NO Employee | 1 | 0 | 1 | |
| 2 | `department` | Department | Link | Department | 0 | 0 | 1 | fetch_from=`employee.department` |
| 3 | `dated` | Date | Date | — | 1 | 0 | 1 | default=Today |
| 4 | `period` | Period | Select | Daily\nWeekly\nMonthly | 1 | 0 | 1 | default=Daily |
| 5 | `col_break_1` | — | Column Break | — | — | — | — | |
| 6 | `target` | Target | Currency | — | 1 | 0 | 1 | |
| 7 | `hit` | Actual (Hit) | Currency | — | 1 | 0 | 1 | |
| 8 | `deviation` | Deviation | Currency | — | 0 | 1 | 1 | read_only=1; auto=hit−target |
| 9 | `notes` | Notes | Small Text | — | 0 | 0 | 0 | |

---

## 12. Integration DocTypes

### 12.1 M-Pesa Settings

**Module**: `national_oil/integrations/`
**Is Single**: Yes (singleton — one global config record)
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | Notes |
|---|---|---|---|---|---|---|
| 1 | `environment` | Environment | Select | Sandbox\nProduction | 1 | default=Sandbox |
| 2 | `shortcode` | Shortcode (Paybill / Till) | Data | — | 1 | |
| 3 | `section_credentials` | API Credentials | Section Break | — | — | |
| 4 | `consumer_key` | Consumer Key | Password | — | 1 | encrypted at rest |
| 5 | `consumer_secret` | Consumer Secret | Password | — | 1 | encrypted at rest |
| 6 | `passkey` | STK Push Passkey | Password | — | 1 | encrypted at rest |
| 7 | `section_urls` | URLs | Section Break | — | — | collapsible=1 |
| 8 | `callback_url` | Callback URL | Data | — | 0 | Auto-generated from site URL |
| 9 | `b2c_initiator_name` | B2C Initiator Name | Data | — | 0 | For future B2C use |

---

### 12.2 M-Pesa Transaction

**Module**: `national_oil/integrations/`
**autoname**: `NOF-MPT-.YYYY.-.####`
**Is Submittable**: No
**Track Changes**: Yes

| # | fieldname | label | fieldtype | options | reqd | read_only | in_list_view | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `transaction_id` | M-Pesa Receipt No. | Data | — | 0 | 0 | 1 | Set on confirmation; unique=1 |
| 2 | `checkout_request_id` | Checkout Request ID | Data | — | 0 | 1 | 0 | Daraja ref; system-set |
| 3 | `dated` | Transaction Date | Datetime | — | 1 | 0 | 1 | default=Now |
| 4 | `status` | Status | Select | Pending\nConfirmed\nFailed\nCancelled | 1 | 0 | 1 | default=Pending; bold=1 |
| 5 | `col_break_1` | — | Column Break | — | — | — | — | |
| 6 | `phone` | Phone Number | Data | — | 1 | 0 | 1 | |
| 7 | `amount` | Amount (KSh) | Currency | — | 1 | 0 | 1 | |
| 8 | `section_links` | Links | Section Break | — | — | — | — | |
| 9 | `customer` | Customer | Link | Customer | 0 | 0 | 0 | Matched after confirmation |
| 10 | `linked_debt` | Linked Debt | Link | Customer Debt | 0 | 0 | 0 | Applied to reduce balance |
| 11 | `section_audit` | Raw Payload | Section Break | — | — | — | — | collapsible=1 |
| 12 | `raw_payload` | Raw Payload (JSON) | Text | — | 0 | 1 | 0 | Full Safaricom response; read_only=1 |

---

## 13. Workflow Definitions

### 13.1 Customer Debt Workflow

**DocType**: Customer Debt
**Field**: `status`
**Note**: `status` is programmatically managed, not via Frappe workflow engine — simpler and avoids email notifications overhead.

| Status | Set By | Condition |
|---|---|---|
| Open | System (on submit) | Initial state |
| Partially Paid | System (after Debt Payment submit) | `0 < balance < payable_amount` |
| Settled | System (after Debt Payment submit) | `balance <= 0` |
| Written Off | Manager manual action | Manager-only button in form |

### 13.2 Leave Request Workflow

**DocType**: Leave Request
**Frappe Workflow**: Yes (uses Frappe Workflow engine for approval routing)

| State | Action | By Role | Next State |
|---|---|---|---|
| Pending | Approve | Station Manager, HR Officer | Approved |
| Pending | Reject | Station Manager, HR Officer | Rejected |
| Approved | Reject | Station Manager | Rejected |

### 13.3 Supplier Credit & Petty Cash Entry

Same programmatic status management as Customer Debt.

---

## 14. Controller Logic Summary

### Python file: `national_oil/fuel_operations/doctype/fuel_purchase/fuel_purchase.py`

```python
class FuelPurchase(Document):
    def validate(self):
        self.total_cost = flt(self.unit_cost) * flt(self.actual_quantity)
        self.balance    = flt(self.total_cost) - flt(self.amount_paid)
        if self.actual_quantity <= 0:
            frappe.throw("Actual Quantity must be greater than zero")
        if self.unit_cost <= 0:
            frappe.throw("Unit Cost must be greater than zero")
        if self.amount_paid > self.total_cost:
            frappe.throw("Amount Paid cannot exceed Total Cost")
        if getdate(self.dated) > getdate(today()):
            frappe.throw("Delivery Date cannot be in the future")

    def on_submit(self):
        if not self.flags.get("migration_mode"):
            self._update_product_stock(+1)
            if self.balance > 0:
                self._create_supplier_credit()

    def on_cancel(self):
        self._update_product_stock(-1)
        self._cancel_supplier_credit()

    def _update_product_stock(self, sign):
        product = frappe.db.get_value("Product",
            {"fuel_type": self.fuel_type}, "name")
        if product:
            frappe.db.set_value("Product", product, "quantity",
                flt(frappe.db.get_value("Product", product, "quantity"))
                + sign * flt(self.actual_quantity))

    def _create_supplier_credit(self):
        credit = frappe.new_doc("Supplier Credit")
        credit.code            = f"SC-{self.name}"
        credit.supplier        = self.supplier
        credit.total_amount    = self.balance
        credit.dated           = self.dated
        credit.detail          = f"Balance from delivery {self.code}"
        credit.source_doctype  = "Fuel Purchase"
        credit.source_document = self.name
        credit.insert(ignore_permissions=True)
        credit.submit()

    def _cancel_supplier_credit(self):
        name = frappe.db.get_value("Supplier Credit",
            {"source_document": self.name, "docstatus": 1})
        if name:
            frappe.get_doc("Supplier Credit", name).cancel()
```

---

### Python file: `national_oil/receivables/doctype/customer_debt/customer_debt.py`

```python
class CustomerDebt(Document):
    def update_balance(self):
        paid = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0)
            FROM `tabDebt Payment`
            WHERE customer_debt=%s AND docstatus=1
        """, self.name)[0][0]
        self.db_set("amount_paid", paid)
        self.db_set("balance", flt(self.payable_amount) - flt(paid))
        if self.balance <= 0:
            self.db_set("status", "Settled")
        elif self.balance < self.payable_amount:
            self.db_set("status", "Partially Paid")
        else:
            self.db_set("status", "Open")
```

---

### Python file: `national_oil/receivables/doctype/debt_payment/debt_payment.py`

```python
class DebtPayment(Document):
    def validate(self):
        debt = frappe.get_doc("Customer Debt", self.customer_debt)
        if self.amount <= 0:
            frappe.throw("Amount must be greater than zero")
        if flt(self.amount) > flt(debt.balance):
            frappe.throw(f"Amount exceeds outstanding balance of {debt.balance}")
        if getdate(self.dated) < getdate(debt.dated):
            frappe.throw("Payment date cannot be earlier than debt date")
        self.customer = debt.customer   # auto-fill

    def on_submit(self):
        frappe.get_doc("Customer Debt", self.customer_debt).update_balance()

    def on_cancel(self):
        frappe.get_doc("Customer Debt", self.customer_debt).update_balance()
```

*(Same pattern for `Supplier Credit` / `Credit Payment`)*

---

### Python file: `national_oil/finance/doctype/petty_cash_entry/petty_cash_entry.py`

```python
class PettyCashEntry(Document):
    def validate(self):
        if self.amount <= 0:
            frappe.throw("Amount must be greater than zero")
        acct = frappe.get_doc("Petty Cash Account", self.petty_cash_account)
        if flt(acct.current_balance) < flt(self.amount):
            frappe.msgprint(
                f"Warning: Account balance ({acct.current_balance}) "
                f"is less than this entry ({self.amount}).",
                indicator="orange", alert=True
            )

    def on_submit(self):
        frappe.db.set_value("Petty Cash Account", self.petty_cash_account,
            "current_balance",
            flt(frappe.db.get_value("Petty Cash Account",
                self.petty_cash_account, "current_balance"))
            - flt(self.amount))

    def on_cancel(self):
        frappe.db.set_value("Petty Cash Account", self.petty_cash_account,
            "current_balance",
            flt(frappe.db.get_value("Petty Cash Account",
                self.petty_cash_account, "current_balance"))
            + flt(self.amount))
```

---

### Python file: `national_oil/hr/doctype/attendance_record/attendance_record.py`

```python
class AttendanceRecord(Document):
    def validate(self):
        exists = frappe.db.exists("Attendance Record", {
            "employee": self.employee,
            "dated": self.dated,
            "name": ["!=", self.name]
        })
        if exists:
            frappe.throw(
                f"Attendance already recorded for {self.employee} on {self.dated}")
```

---

### Python file: `national_oil/hr/doctype/leave_request/leave_request.py`

```python
class LeaveRequest(Document):
    def validate(self):
        if getdate(self.from_date) > getdate(self.to_date):
            frappe.throw("From Date must be before To Date")
        self.total_days = date_diff(self.to_date, self.from_date) + 1
        self._check_overlap()

    def _check_overlap(self):
        overlap = frappe.db.sql("""
            SELECT name FROM `tabLeave Request`
            WHERE employee=%s AND status='Approved'
            AND name != %s
            AND (from_date BETWEEN %s AND %s
                 OR to_date BETWEEN %s AND %s)
        """, (self.employee, self.name or "",
              self.from_date, self.to_date,
              self.from_date, self.to_date))
        if overlap:
            frappe.throw("Approved leave already exists for this date range")
```

---

## 15. Client Script Summary

### Fuel Purchase — client script

```javascript
frappe.ui.form.on("Fuel Purchase", {
    unit_cost(frm)       { calc_totals(frm); },
    actual_quantity(frm) { calc_totals(frm); },
    amount_paid(frm)     { calc_totals(frm); },
    initial_dip(frm)     { suggest_quantity(frm); },
    final_dip(frm)       { suggest_quantity(frm); },
    driver(frm) {
        if (frm.doc.driver) {
            frappe.db.get_value("Driver", frm.doc.driver, "car_plate",
                r => frm.set_value("car_plate", r.car_plate));
        }
    }
});

function calc_totals(frm) {
    const total = flt(frm.doc.unit_cost) * flt(frm.doc.actual_quantity);
    frm.set_value("total_cost", total);
    frm.set_value("balance", total - flt(frm.doc.amount_paid));
}

function suggest_quantity(frm) {
    if (frm.doc.initial_dip && frm.doc.final_dip) {
        const suggested = flt(frm.doc.final_dip) - flt(frm.doc.initial_dip);
        if (suggested > 0 && !frm.doc.actual_quantity) {
            frappe.confirm(
                `Suggest actual quantity of ${suggested} L from dip readings?`,
                () => frm.set_value("actual_quantity", suggested)
            );
        }
    }
}
```

### Inventory Receipt — client script

```javascript
frappe.ui.form.on("Inventory Receipt", {
    unit_cost(frm)          { calc_inv_totals(frm); },
    units(frm)              { calc_inv_totals(frm); },
    subunits_per_unit(frm)  { calc_inv_totals(frm); },
    amount_paid(frm)        { calc_inv_totals(frm); },
});

function calc_inv_totals(frm) {
    const total = flt(frm.doc.units) * flt(frm.doc.unit_cost);
    const sub   = frm.doc.subunits_per_unit
        ? flt(frm.doc.unit_cost) / flt(frm.doc.subunits_per_unit) : 0;
    frm.set_value("total_cost",   total);
    frm.set_value("subunit_cost", sub);
    frm.set_value("balance",      total - flt(frm.doc.amount_paid));
}
```

### Debt Payment — client script

```javascript
frappe.ui.form.on("Debt Payment", {
    customer_debt(frm) {
        if (frm.doc.customer_debt) {
            frappe.db.get_value("Customer Debt", frm.doc.customer_debt,
                ["customer", "balance"],
                r => {
                    frm.set_value("customer", r.customer);
                    frm.set_df_property("amount", "description",
                        `Outstanding: KSh ${format_currency(r.balance, "KES")}`);
                });
        }
    }
});
```

### Sales Entry — client script

```javascript
frappe.ui.form.on("Sales Entry", {
    payment_method(frm) {
        frm.toggle_reqd("customer", frm.doc.payment_method === "Credit");
    }
});

frappe.ui.form.on("Sales Item", {
    quantity(frm, cdt, cdn) { update_row_total(frm, cdt, cdn); },
    unit_price(frm, cdt, cdn) { update_row_total(frm, cdt, cdn); },
    product(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.product) {
            frappe.db.get_value("Product", row.product, "selling_price",
                r => frappe.model.set_value(cdt, cdn, "unit_price", r.selling_price));
        }
    }
});

function update_row_total(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "total",
        flt(row.quantity) * flt(row.unit_price));
    frm.refresh_field("items");
}
```

### Performance Review — client script

```javascript
frappe.ui.form.on("Performance Review", {
    target(frm) { calc_deviation(frm); },
    hit(frm)    { calc_deviation(frm); },
});

function calc_deviation(frm) {
    frm.set_value("deviation", flt(frm.doc.hit) - flt(frm.doc.target));
}
```

---

## 16. Custom Methods (Whitelisted APIs)

All custom Python API methods live in `national_oil/<module>/api.py`.

| Method | Module | Roles | Description |
|---|---|---|---|
| `get_fuel_stock` | fuel_operations | All | Current stock per fuel type |
| `get_current_prices` | fuel_operations | All | Latest Fuel Price records |
| `get_sales_summary` | sales | All | Aggregated sales by period/dept |
| `get_customer_balance` | receivables | All | Debt summary for a customer |
| `record_debt_payment` | receivables | Cashier+ | Create + submit Debt Payment |
| `initiate_stk_push` | integrations | Cashier+ | Trigger M-Pesa STK Push |
| `mpesa_callback` | integrations | Guest (IP-restricted) | Safaricom callback handler |
| `check_transaction_status` | integrations | Cashier+ | Poll MPT status |
| `get_dashboard_metrics` | api.dashboard | All | All dashboard numbers in one call |
| `get_sales_trend` | api.dashboard | All | Chart data: sales per day |
| `bulk_mark_attendance` | hr | HR Officer+ | Create multiple Attendance Records |

---

## 17. Reports

### 17.1 Sales Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Daily Sales Summary | Query | Sales Entry | dated, department, sale_type, amount | dated, department, sale_type |
| Weekly Sales Summary | Query | Sales Entry | YEARWEEK(dated), SUM(amount) | week_start, department |
| Monthly Sales Summary | Query | Sales Entry | month, department, SUM(amount) | month, year, department |
| Annual Sales Summary | Query | Sales Entry | year, department, SUM(amount) | year |
| Wet Stock Sales | Query | Sales Entry | dated, amount (filtered to Wet Stock) | period |
| Other Sales | Query | Sales Entry | dated, amount (filtered to Other) | period |

### 17.2 Receivables Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Customer Debt Ageing | Script | Customer Debt | customer, 0-30, 31-60, 61-90, 90+ | as_of_date, customer |
| All Customer Debts | Query | Customer Debt | customer, payable_amount, amount_paid, balance, status | status, customer |
| Debt Collection Summary | Query | Debt Payment | customer, SUM(amount), period | from_date, to_date |

### 17.3 Payables Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Supplier Payables | Script | Supplier Credit | supplier, total_amount, amount_paid, balance, status | supplier, status |
| All Credits | Query | Supplier Credit | supplier, detail, total_amount, balance | from_date, to_date, supplier |

### 17.4 Cash Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Petty Cash — Daily | Query | Petty Cash Entry | dated, description, amount, department, account | dated |
| Petty Cash — Monthly | Query | Petty Cash Entry | month, SUM(amount), account | month, year |
| Petty Cash — Annual | Query | Petty Cash Entry | year, SUM(amount) | year |

### 17.5 Fuel Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Fuel Delivery Log | Query | Fuel Purchase | code, dated, supplier, fuel_type, actual_quantity, total_cost, balance | supplier, fuel_type, from_date, to_date |
| Fuel Stock Summary | Script | Product | product_name, fuel_type, quantity, selling_price | as_of_date |
| Pump Reading Reconciliation | Script | Pump Reading | dated, pump_number, variance vs sales | pump_number, from_date, to_date |

### 17.6 HR Reports

| Report Name | Type | DocType | Key Fields Shown | Key Filters |
|---|---|---|---|---|
| Attendance Summary | Query | Attendance Record | employee, present_count, absent_count, overtime, attendance_pct | employee, month, year |
| Performance Report | Query | Performance Review | employee, dated, target, hit, deviation | employee, period, from_date, to_date |
| Leave Register | Query | Leave Request | employee, leave_type, from_date, to_date, total_days, status | employee, year, status |

---

## 18. Print Formats

| Print Format Name | DocType | Based On | Key Sections |
|---|---|---|---|
| Fuel Delivery Receipt | Fuel Purchase | Standard | Header (logo, station name), delivery details, dip measurements, financials, supplier signature block |
| Customer Debt Statement | Customer Debt | Standard | Customer info, all linked Debt Payments, outstanding balance |
| Supplier Credit Statement | Supplier Credit | Standard | Supplier info, source document link, all Credit Payments, balance |
| Petty Cash Voucher | Petty Cash Entry | Standard | Date, description, amount in words, approver signature |
| Inventory Delivery Note | Inventory Receipt | Standard | Supplier, items received, quantities, costs |

---

## 19. Scheduled Tasks

Configured in `hooks.py` under `scheduler_events`.

| Task Function | Schedule | Purpose | DocTypes Touched |
|---|---|---|---|
| `national_oil.tasks.daily.auto_settle_debts` | `daily` (00:05) | Set `status=Settled` on Customer Debt / Supplier Credit where `balance=0` | Customer Debt, Supplier Credit |
| `national_oil.tasks.daily.refresh_sales_targets` | `daily` (00:10) | Recalculate `hit_amount` and `deviation` on all Department Sales Targets | Department Sales Target |
| `national_oil.tasks.weekly.send_debt_reminders` | `weekly` | Fetch open Customer Debts; send email/SMS reminder | Customer Debt, Customer |
| `national_oil.tasks.monthly.backup_report_snapshot` | `monthly` | Save monthly aggregates as notes for historical reference | (read-only query) |

---

## 20. Workspace Configuration

**File**: `national_oil/config/desktop.py`

```python
data = {
    "National Oil": {
        "color": "#f5a623",
        "icon": "octicon octicon-flame",
        "type": "module",
        "label": "National Oil",
        "items": [
            # Operations
            {"type": "doctype", "name": "Fuel Purchase",        "label": "Fuel Purchases"},
            {"type": "doctype", "name": "Pump Reading",         "label": "Pump Readings"},
            {"type": "doctype", "name": "Fuel Price",           "label": "Fuel Prices"},
            {"type": "doctype", "name": "Inventory Receipt",    "label": "Inventory"},
            {"type": "doctype", "name": "Sales Entry",          "label": "Sales"},
            # Finance
            {"type": "doctype", "name": "Customer Debt",        "label": "Customer Debts"},
            {"type": "doctype", "name": "Debt Payment",         "label": "Debt Payments"},
            {"type": "doctype", "name": "Supplier Credit",      "label": "Supplier Credits"},
            {"type": "doctype", "name": "Credit Payment",       "label": "Credit Payments"},
            {"type": "doctype", "name": "Petty Cash Entry",     "label": "Petty Cash"},
            # HR
            {"type": "doctype", "name": "NO Employee",          "label": "Employees"},
            {"type": "doctype", "name": "Attendance Record",    "label": "Attendance"},
            {"type": "doctype", "name": "Leave Request",        "label": "Leave Requests"},
            {"type": "doctype", "name": "Performance Review",   "label": "Performance"},
            # Masters
            {"type": "doctype", "name": "Customer",             "label": "Customers"},
            {"type": "doctype", "name": "Supplier",             "label": "Suppliers"},
            # Reports
            {"type": "report",  "name": "Daily Sales Summary",  "label": "Sales Report",        "report_type": "Query Report", "doctype": "Sales Entry"},
            {"type": "report",  "name": "Customer Debt Ageing", "label": "Debt Ageing",         "report_type": "Script Report","doctype": "Customer Debt"},
            {"type": "report",  "name": "Fuel Delivery Log",    "label": "Fuel Delivery Log",   "report_type": "Query Report", "doctype": "Fuel Purchase"},
        ]
    }
}
```

---

## 21. hooks.py Reference

```python
# apps/national_oil/national_oil/hooks.py

app_name            = "national_oil"
app_title           = "National Oil"
app_publisher       = "ERP Kenya"
app_description     = "Petrol station management system for Kenya"
app_email           = "dev@erpkenya.co.ke"
app_license         = "MIT"

# DocType-level hooks
doc_events = {
    "Debt Payment": {
        "on_submit": "national_oil.receivables.doctype.debt_payment.debt_payment.on_submit",
        "on_cancel": "national_oil.receivables.doctype.debt_payment.debt_payment.on_cancel",
    },
    "Credit Payment": {
        "on_submit": "national_oil.payables.doctype.credit_payment.credit_payment.on_submit",
        "on_cancel": "national_oil.payables.doctype.credit_payment.credit_payment.on_cancel",
    },
    "Petty Cash Entry": {
        "on_submit": "national_oil.finance.doctype.petty_cash_entry.petty_cash_entry.on_submit",
        "on_cancel": "national_oil.finance.doctype.petty_cash_entry.petty_cash_entry.on_cancel",
    },
    "Fuel Purchase": {
        "on_submit": "national_oil.fuel_operations.doctype.fuel_purchase.fuel_purchase.on_submit",
        "on_cancel": "national_oil.fuel_operations.doctype.fuel_purchase.fuel_purchase.on_cancel",
    },
    "Inventory Receipt": {
        "on_submit": "national_oil.inventory.doctype.inventory_receipt.inventory_receipt.on_submit",
        "on_cancel": "national_oil.inventory.doctype.inventory_receipt.inventory_receipt.on_cancel",
    },
}

# Scheduled tasks
scheduler_events = {
    "daily": [
        "national_oil.tasks.daily.auto_settle_debts",
        "national_oil.tasks.daily.refresh_sales_targets",
    ],
    "weekly": [
        "national_oil.tasks.weekly.send_debt_reminders",
    ],
    "monthly": [
        "national_oil.tasks.monthly.backup_report_snapshot",
    ],
}

# Fixtures (export these with bench export-fixtures)
fixtures = [
    {"dt": "Role",        "filters": [["name", "in", [
        "Station Manager", "Pump Attendant", "Cashier",
        "Store Keeper", "HR Officer", "Accountant", "Driver"
    ]]]},
    {"dt": "Fuel Type"},
    {"dt": "Department"},
]

# Custom fields (if adding to core doctypes — none required for this app)
# override_doctype_class = {}

# Website route rules (for M-Pesa callback)
website_route_rules = [
    {"from_route": "/api/mpesa/callback", "to_route": "mpesa-callback"},
]
```

---

## Appendix A: Field Type Quick Reference

| Frappe Field Type | Storage | Use Case |
|---|---|---|
| `Data` | VARCHAR(140) | Short text: names, codes, phone |
| `Small Text` | TEXT | Medium text: descriptions, addresses |
| `Text` | LONGTEXT | Long text: notes, raw JSON payloads |
| `Int` | INT | Whole numbers: units, days |
| `Float` | DECIMAL(21,9) | Decimals: quantities, measurements |
| `Currency` | DECIMAL(21,9) | Money values (displayed with KSh) |
| `Percent` | DECIMAL(21,9) | Percentage values |
| `Date` | DATE | Calendar date |
| `Datetime` | DATETIME | Date + time (M-Pesa timestamps) |
| `Select` | VARCHAR(140) | Fixed options (newline-separated in options) |
| `Link` | VARCHAR(140) | FK to another DocType |
| `Dynamic Link` | VARCHAR(140) | FK to any DocType (pair with a Data field naming the doctype) |
| `Table` | — | Child table (in-form grid) |
| `Attach` | TEXT | File URL (any file type) |
| `Attach Image` | TEXT | Image file URL |
| `Check` | INT(1) | Boolean 0/1 |
| `Password` | TEXT | Encrypted storage |
| `Read Only` | — | Display-only computed value |
| `Section Break` | — | Layout: section divider |
| `Column Break` | — | Layout: two-column layout |
| `Heading` | — | Layout: bold label |

---

## Appendix B: Inter-DocType Dependency Graph

```
Fuel Type ──────────────────────► Fuel Price
    │                                  │
    │                                  │ (current price lookup)
    ▼                                  ▼
Product ◄───── Fuel Purchase ──────► Supplier Credit
    ▲               │   │                │
    │           Supplier Driver      Credit Payment
    │               │
Inventory ◄─────────┘
Receipt ──────────────────────────► Supplier Credit

Department ──► Sales Entry ─────► (aggregation) ─► Dept Sales Target
    │
    ├──► NO Employee ──► Attendance Record
    │         │───────► Leave Request
    │         └───────► Performance Review
    │
    └──► Petty Cash Account ──► Petty Cash Entry

Customer ──► Customer Debt ──► Debt Payment
                  ▲
                  │
         M-Pesa Transaction
```

---

## Appendix C: Sensitive Field Handling

| DocType | Field | Handling |
|---|---|---|
| M-Pesa Settings | `consumer_key` | Frappe `Password` field (encrypted in DB) |
| M-Pesa Settings | `consumer_secret` | Frappe `Password` field |
| M-Pesa Settings | `passkey` | Frappe `Password` field |
| M-Pesa Transaction | `raw_payload` | `read_only=1`; only system writes; no export |
| Customer | `customer_photo` | `Attach Image`; stored in private files |
| NO Employee | `id_document` | `Attach`; stored in private files |
| Fuel Purchase | `receipt` | `Attach`; stored in private files |
