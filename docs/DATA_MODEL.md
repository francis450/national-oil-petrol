# National Oil — Data Model (DocType Specifications)

> All DocTypes below map to tables in the legacy `bigbroco_petrol` database.
> Field types follow Frappe naming: `Data`, `Link`, `Currency`, `Float`, `Int`, `Date`, `Select`, `Attach`, `Small Text`, `Text`, `Check`.

---

## Table of Contents

1. [Setup & Masters](#1-setup--masters)
2. [Fuel Operations](#2-fuel-operations)
3. [Inventory](#3-inventory)
4. [Sales](#4-sales)
5. [Receivables (Customer Debts)](#5-receivables-customer-debts)
6. [Payables (Supplier Credits)](#6-payables-supplier-credits)
7. [Finance](#7-finance)
8. [HR](#8-hr)
9. [Integrations](#9-integrations)
10. [Entity-Relationship Diagram](#10-entity-relationship-diagram)

---

## 1. Setup & Masters

### 1.1 Department

> Legacy table: `departments`

| Field | Type | Required | Notes |
|---|---|---|---|
| department_name | Data | Yes | Primary display name |
| description | Small Text | No | |

**Naming**: `department_name`
**Referenced by**: Sales Entry, Employee, Petty Cash Entry, Performance Review

---

### 1.2 Fuel Type

> Legacy: implied from `products.fuel` / `brands.brandname`

| Field | Type | Required | Notes |
|---|---|---|---|
| fuel_type_name | Data | Yes | e.g. Petrol, Diesel, Kerosene |
| unit_of_measure | Select | Yes | Litres / Kg |
| description | Small Text | No | |

---

### 1.3 Driver

> Legacy table: `drivers`

| Field | Type | Required | Notes |
|---|---|---|---|
| driver_name | Data | Yes | |
| phone | Data | No | |
| email | Data | No | |
| car_plate | Data | No | Vehicle registration |
| supplier | Link → Supplier | No | Primary supplier this driver works for |
| supplier_contact | Data | No | Direct contact at supplier |

**Naming**: `driver_name`

---

### 1.4 Supplier

> Legacy table: `suppliers`

| Field | Type | Required | Notes |
|---|---|---|---|
| supplier_name | Data | Yes | |
| account_number | Data | No | Bank/payment account |
| phone | Data | No | |
| email | Data | No | |
| address | Small Text | No | |

**Naming**: `supplier_name`
**Referenced by**: Fuel Purchase, Brand, Inventory Receipt, Supplier Credit, Driver

---

### 1.5 Brand

> Legacy table: `brands`

| Field | Type | Required | Notes |
|---|---|---|---|
| brand_name | Data | Yes | Fuel/product brand |
| supplier | Link → Supplier | Yes | |
| brand_identity | Data | No | Auto-computed: `brand_name + supplier` (legacy field) |

**Naming**: `brand_name`

---

### 1.6 Customer

> Legacy table: `customers`

| Field | Type | Required | Notes |
|---|---|---|---|
| customer_name | Data | Yes | |
| email | Data | No | |
| phone | Data | No | |
| address | Small Text | No | |
| customer_photo | Attach | No | ID / photo document |

**Naming**: `customer_name`
**Referenced by**: Customer Debt, Sales Entry (optional credit sale)

---

## 2. Fuel Operations

### 2.1 Fuel Purchase

> Legacy table: `fuel`
> Represents a single fuel delivery from a supplier.

| Field | Type | Required | Notes |
|---|---|---|---|
| **Identification** | | | |
| code | Data | Yes | Unique delivery reference |
| dated | Date | Yes | Delivery date |
| **Supplier & Logistics** | | | |
| supplier | Link → Supplier | Yes | |
| driver | Link → Driver | No | |
| car_plate | Data | No | Delivery vehicle |
| **Product** | | | |
| fuel_type | Link → Fuel Type | Yes | |
| brand | Link → Brand | No | |
| unit_of_measure | Select | Yes | Litres |
| **Dip Measurements** | | | |
| initial_dip | Float | No | Tank level before delivery (cm) |
| final_dip | Float | No | Tank level after delivery (cm) |
| actual_quantity | Float | Yes | Net delivered quantity (litres) |
| temperature | Float | No | Fuel temperature at delivery |
| density | Float | No | Fuel density |
| seal_condition | Select | No | Intact / Broken / Missing |
| **Financials** | | | |
| unit_cost | Currency | Yes | Cost per litre |
| total_cost | Currency | Yes | unit_cost × actual_quantity |
| amount_paid | Currency | No | Amount settled at delivery |
| balance | Currency | No | total_cost − amount_paid |
| payment_method | Select | No | Cash / Cheque / M-Pesa / Bank Transfer |
| **Supporting Docs** | | | |
| receipt | Attach | No | Delivery receipt file |
| comments | Small Text | No | |
| **Status** | | | |
| docstatus | Int | — | 0=Draft, 1=Submitted, 2=Cancelled |

**Controller logic:**
- On Submit: update `Product.quantity` += `actual_quantity`
- On Submit: if `balance > 0` → create `Supplier Credit` linked to this document
- `total_cost` auto-calculated from `unit_cost × actual_quantity`

---

### 2.2 Pump Reading

> Legacy table: `pumpreadings`

| Field | Type | Required | Notes |
|---|---|---|---|
| dated | Date | Yes | |
| pump_number | Data | Yes | Pump identifier |
| fuel_type | Link → Fuel Type | Yes | |
| opening_reading | Float | Yes | Meter at start of day |
| closing_reading | Float | Yes | Meter at end of day |
| variance | Float | No | Auto: closing − opening |
| attendant | Link → Employee | No | |
| department | Link → Department | No | |
| notes | Small Text | No | |

---

### 2.3 Fuel Price

> Legacy: `products.bp`, `products.sp`, `products.spr`, `products.spw`
> Tracks price changes over time.

| Field | Type | Required | Notes |
|---|---|---|---|
| fuel_type | Link → Fuel Type | Yes | |
| effective_date | Date | Yes | |
| buying_price | Currency | Yes | Cost per litre to station |
| selling_price_retail | Currency | Yes | Pump price per litre |
| selling_price_wholesale | Currency | No | Bulk customer rate |
| set_by | Link → User | No | Auto: current user |

---

## 3. Inventory

### 3.1 Product

> Legacy table: `products`
> Live inventory balance per fuel/product type.

| Field | Type | Required | Notes |
|---|---|---|---|
| product_name | Data | Yes | e.g. "Petrol 95", "Diesel", "Engine Oil 1L" |
| fuel_type | Link → Fuel Type | No | Set if fuel product |
| brand | Link → Brand | No | |
| unit_of_measure | Select | Yes | Litres / Pieces / Kg |
| quantity | Float | No | Current stock (updated by system) |
| buying_price | Currency | No | Latest purchase price |
| selling_price | Currency | No | Retail pump/shelf price |
| selling_price_wholesale | Currency | No | |
| is_fuel | Check | No | 1 = fuel product |

---

### 3.2 Inventory Receipt

> Legacy table: `inventory` (non-fuel stock purchases)

| Field | Type | Required | Notes |
|---|---|---|---|
| code | Data | Yes | Receipt reference |
| dated | Date | Yes | |
| brand | Link → Brand | No | |
| supplier | Link → Supplier | Yes | |
| unit_of_measure | Select | Yes | |
| units | Int | Yes | Number of units received |
| subunits_per_unit | Int | No | e.g. 12 bottles per case |
| unit_cost | Currency | Yes | |
| subunit_cost | Currency | No | |
| total_cost | Currency | Yes | Auto: units × unit_cost |
| amount_paid | Currency | No | |
| balance | Currency | No | total_cost − amount_paid |
| payment_method | Select | No | |
| selling_price_retail | Currency | No | |
| selling_price_wholesale | Currency | No | |
| receipt | Attach | No | |
| comments | Small Text | No | |

---

## 4. Sales

### 4.1 Sales Entry

> Legacy table: `sales`
> Daily departmental sales totals. Legacy stores amount + department per row.

| Field | Type | Required | Notes |
|---|---|---|---|
| dated | Date | Yes | |
| department | Link → Department | Yes | |
| amount | Currency | Yes | Total sales for this entry |
| sale_type | Select | Yes | Wet Stock (fuel) / Other |
| customer | Link → Customer | No | Populated for credit sales |
| payment_method | Select | No | Cash / M-Pesa / Credit |
| notes | Small Text | No | |

**Child Table: Sales Item** (for line-item detail — extends legacy model)

| Field | Type | Notes |
|---|---|---|
| product | Link → Product | |
| quantity | Float | |
| unit_price | Currency | |
| total | Currency | Auto: qty × unit_price |

---

### 4.2 Department Sales Target

> Legacy table: `performance` (partially), dashboard metrics in `main.php`

| Field | Type | Required | Notes |
|---|---|---|---|
| department | Link → Department | Yes | |
| period | Select | Yes | Daily / Weekly / Monthly |
| period_start | Date | Yes | |
| target_amount | Currency | Yes | Expected sales |
| hit_amount | Currency | No | Actual sales (auto-linked) |
| deviation | Currency | No | Auto: hit − target |

---

## 5. Receivables (Customer Debts)

### 5.1 Customer Debt

> Legacy table: `customerdebts`

| Field | Type | Required | Notes |
|---|---|---|---|
| code | Data | Yes | Reference code |
| customer | Link → Customer | Yes | |
| dated | Date | Yes | Date debt incurred |
| payable_amount | Currency | Yes | Original amount owed |
| amount_paid | Currency | No | Aggregated from Debt Payments |
| balance | Currency | No | Auto: payable − amount_paid |
| status | Select | No | Open / Partially Paid / Settled |
| receipt | Attach | No | Supporting document |
| notes | Small Text | No | |

**Controller logic:**
- `balance` = `payable_amount` − SUM of linked `Debt Payment.amount`
- Status auto-updates: Settled when `balance == 0`

---

### 5.2 Debt Payment

> Legacy table: `debtpayment`

| Field | Type | Required | Notes |
|---|---|---|---|
| customer_debt | Link → Customer Debt | Yes | |
| customer | Link → Customer | Yes | Auto-filled from Customer Debt |
| dated | Date | Yes | |
| amount | Currency | Yes | Amount paid in this installment |
| payment_method | Select | No | Cash / M-Pesa / Bank |
| reference | Data | No | Cheque/M-Pesa transaction ref |
| receipt | Attach | No | |

**Controller logic:**
- On Save: update `Customer Debt.amount_paid` and `balance`

---

## 6. Payables (Supplier Credits)

### 6.1 Supplier Credit

> Legacy table: `debts` (where `amount < 0` = payable to supplier)

| Field | Type | Required | Notes |
|---|---|---|---|
| code | Data | Yes | Reference code |
| supplier | Link → Supplier | Yes | |
| dated | Date | Yes | |
| detail | Small Text | Yes | Description of the credit |
| total_amount | Currency | Yes | Original credit amount |
| amount_paid | Currency | No | Aggregated from Credit Payments |
| balance | Currency | No | Auto: total − amount_paid |
| status | Select | No | Open / Partially Paid / Settled |
| source_document | Dynamic Link | No | Link to Fuel Purchase / Inventory Receipt |
| source_doctype | Data | No | Source doctype name |

---

### 6.2 Credit Payment

> Legacy table: `debtpayment` (dual-use for supplier credits too)

| Field | Type | Required | Notes |
|---|---|---|---|
| supplier_credit | Link → Supplier Credit | Yes | |
| supplier | Link → Supplier | Yes | Auto-filled |
| dated | Date | Yes | |
| amount | Currency | Yes | |
| payment_method | Select | No | Cash / Cheque / M-Pesa / Bank Transfer |
| reference | Data | No | Cheque number / transaction ID |
| receipt | Attach | No | |

---

## 7. Finance

### 7.1 Petty Cash Entry

> Legacy table: `pettycash`

| Field | Type | Required | Notes |
|---|---|---|---|
| dated | Date | Yes | |
| description | Data | Yes | What the cash was spent on |
| amount | Currency | Yes | |
| department | Link → Department | No | |
| approved_by | Link → User | No | |
| receipt | Attach | No | |
| petty_cash_account | Link → Petty Cash Account | No | |

---

### 7.2 Petty Cash Account

> Legacy table: `pettycashaccount`

| Field | Type | Required | Notes |
|---|---|---|---|
| account_name | Data | Yes | |
| current_balance | Currency | No | Auto-calculated |
| last_replenished | Date | No | |
| department | Link → Department | No | |

---

## 8. HR

### 8.1 Employee

> Legacy table: `worker`
> Named `no_employee` to avoid conflict with ERPNext's built-in Employee doctype if installed alongside.

| Field | Type | Required | Notes |
|---|---|---|---|
| employee_name | Data | Yes | |
| phone | Data | No | |
| address | Small Text | No | |
| location | Data | No | Work station / branch |
| profession | Data | No | Job title / trade |
| designation | Select | Yes | Casual / Permanent |
| department | Link → Department | No | |
| id_document | Attach | No | Passport / National ID scan |
| is_active | Check | No | Default 1 |

---

### 8.2 Attendance Record

> Legacy table: `attendance`

| Field | Type | Required | Notes |
|---|---|---|---|
| employee | Link → Employee | Yes | |
| dated | Date | Yes | |
| status | Select | Yes | Present / Absent / Late |
| overtime_hours | Float | No | |
| notes | Small Text | No | |

**Unique constraint**: `employee` + `dated`

---

### 8.3 Leave Request

> Legacy table: `leaves`

| Field | Type | Required | Notes |
|---|---|---|---|
| employee | Link → Employee | Yes | |
| leave_type | Select | Yes | Annual / Sick / Emergency / Unpaid |
| from_date | Date | Yes | |
| to_date | Date | Yes | |
| total_days | Int | No | Auto: to_date − from_date + 1 |
| reason | Small Text | No | |
| status | Select | No | Pending / Approved / Rejected |
| approved_by | Link → User | No | |

---

### 8.4 Performance Review

> Legacy table: `performance`

| Field | Type | Required | Notes |
|---|---|---|---|
| employee | Link → Employee | Yes | |
| department | Link → Department | No | |
| dated | Date | Yes | |
| period | Select | Yes | Daily / Weekly / Monthly |
| target | Currency | Yes | Sales / output target |
| hit | Currency | Yes | Actual output achieved |
| deviation | Currency | No | Auto: hit − target |
| notes | Small Text | No | |

---

## 9. Integrations

### 9.1 M-Pesa Settings

> Legacy: `mpesa.php` config (hardcoded)

| Field | Type | Required | Notes |
|---|---|---|---|
| consumer_key | Password | Yes | Daraja API consumer key |
| consumer_secret | Password | Yes | Daraja API consumer secret |
| shortcode | Data | Yes | Paybill / Till number |
| passkey | Password | Yes | For STK Push |
| environment | Select | Yes | Sandbox / Production |
| callback_url | Data | No | Frappe webhook endpoint |

---

### 9.2 M-Pesa Transaction

> Legacy table: `mpesatransactions`

| Field | Type | Required | Notes |
|---|---|---|---|
| transaction_id | Data | Yes | Safaricom transaction code |
| dated | Datetime | Yes | |
| phone | Data | Yes | Customer phone number |
| amount | Currency | Yes | |
| status | Select | Yes | Pending / Confirmed / Failed |
| customer | Link → Customer | No | Matched after confirmation |
| linked_debt | Link → Customer Debt | No | Applied to reduce balance |
| raw_payload | Text | No | Full webhook JSON for audit |

---

## 10. Entity-Relationship Diagram

```
                    ┌──────────────┐
                    │  Department  │
                    └──────┬───────┘
                           │ 1:M
         ┌─────────────────┼──────────────────────┐
         │                 │                      │
   ┌─────▼─────┐   ┌───────▼───────┐   ┌─────────▼──────┐
   │  Employee  │   │  Sales Entry  │   │  Petty Cash    │
   └─────┬──────┘   └───────────────┘   │  Entry         │
         │ 1:M                          └────────────────┘
    ┌────┴──────────────┐
    │    │              │
┌───▼──┐ ┌▼──────────┐ ┌▼─────────────┐
│ Att. │ │   Leave   │ │ Performance  │
│Record│ │  Request  │ │   Review     │
└──────┘ └───────────┘ └──────────────┘

┌──────────┐ 1:M  ┌──────────────┐ 1:1  ┌────────────────┐
│ Supplier ├──────► Fuel Purchase├──────► Supplier Credit│
└──────┬───┘      └──────────────┘      └────────┬───────┘
       │ 1:M                                      │ 1:M
       │           ┌──────────┐         ┌─────────▼──────┐
       └───────────► Inventory│         │ Credit Payment │
                   │ Receipt  │         └────────────────┘
                   └──────────┘

┌──────────┐ 1:M  ┌───────────────┐ 1:M  ┌──────────────┐
│ Customer ├──────► Customer Debt ├──────► Debt Payment │
└──────────┘      └───────────────┘      └──────────────┘

┌──────────┐        ┌──────────────┐
│ Fuel Type├────────► Fuel Price   │
└──────┬───┘        └──────────────┘
       │ 1:M
       │    ┌──────────┐
       └────► Product  │
             └──────────┘

┌──────────┐ 1:M  ┌──────────────┐
│  Driver  ├──────► Fuel Purchase│
└──────────┘      └──────────────┘

┌──────────────────┐
│  M-Pesa          │          ┌──────────────────┐
│  Transaction ────┼──────────► Customer Debt    │
└──────────────────┘          └──────────────────┘
```

---

## 11. Legacy Field Mapping Reference

| Legacy Table.Field | DocType.Field |
|---|---|
| `fuel.code` | `Fuel Purchase.code` |
| `fuel.dated` | `Fuel Purchase.dated` |
| `fuel.driver` | `Fuel Purchase.driver` |
| `fuel.car` | `Fuel Purchase.car_plate` |
| `fuel.supplier` | `Fuel Purchase.supplier` |
| `fuel.initdip` | `Fuel Purchase.initial_dip` |
| `fuel.finaldip` | `Fuel Purchase.final_dip` |
| `fuel.actual` | `Fuel Purchase.actual_quantity` |
| `fuel.unitcost` | `Fuel Purchase.unit_cost` |
| `fuel.totalcost` | `Fuel Purchase.total_cost` |
| `fuel.paid` | `Fuel Purchase.amount_paid` |
| `fuel.balance` | `Fuel Purchase.balance` |
| `fuel.temperature` | `Fuel Purchase.temperature` |
| `fuel.density` | `Fuel Purchase.density` |
| `fuel.seal` | `Fuel Purchase.seal_condition` |
| `fuel.receipt` | `Fuel Purchase.receipt` |
| `products.fuel` | `Product.product_name` / `Fuel Type.fuel_type_name` |
| `products.bp` | `Fuel Price.buying_price` |
| `products.sp` | `Fuel Price.selling_price_retail` |
| `products.qnty` | `Product.quantity` |
| `customers.name` | `Customer.customer_name` |
| `customerdebts.customer` | `Customer Debt.customer` |
| `customerdebts.payable` | `Customer Debt.payable_amount` |
| `customerdebts.paid` | `Customer Debt.amount_paid` |
| `customerdebts.balance` | `Customer Debt.balance` |
| `debts.supplier` | `Supplier Credit.supplier` |
| `debts.amount` | `Supplier Credit.total_amount` |
| `debtpayment.code` | `Debt Payment.customer_debt` / `Credit Payment.supplier_credit` |
| `debtpayment.amount` | `Debt Payment.amount` / `Credit Payment.amount` |
| `worker.name` | `Employee.employee_name` |
| `worker.designation` | `Employee.designation` |
| `attendance.name` | `Attendance Record.employee` |
| `attendance.attendance` | `Attendance Record.status` |
| `attendance.overtime` | `Attendance Record.overtime_hours` |
| `performance.name` | `Performance Review.employee` |
| `performance.target` | `Performance Review.target` |
| `performance.hit` | `Performance Review.hit` |
| `performance.deviation` | `Performance Review.deviation` |
| `sales.amount` | `Sales Entry.amount` |
| `sales.department` | `Sales Entry.department` |
| `pettycash.amount` | `Petty Cash Entry.amount` |
| `pettycash.dated` | `Petty Cash Entry.dated` |
