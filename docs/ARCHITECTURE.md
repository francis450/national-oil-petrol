# National Oil — System Architecture

> Migration target for the legacy `bigbroco_petrol` PHP system.
> App: `national_oil` | Framework: Frappe | Author: ERP Kenya

---

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frappe Desk (UI)                         │
│         Role-based workspace per user type / department         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                    Frappe Web Server (Gunicorn)                  │
│  REST API  ·  Form Server  ·  Report Engine  ·  Scheduler       │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Fuel Ops    │  Finance     │  HR          │  Inventory         │
│  Module      │  Module      │  Module      │  Module            │
└──────────────┴──────────────┴──────────────┴────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      MariaDB (managed by    │
              │      Frappe bench)          │
              └─────────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │  External Integrations      │
              │  • M-Pesa STK Push/C2B      │
              │  • File / Document Store    │
              └─────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Legacy (PHP) | National Oil (Frappe) |
|---|---|---|
| Language | PHP 5.6 procedural | Python 3.10+ |
| Web Framework | Raw PHP + MySQLi | Frappe 15 |
| Frontend | Bootstrap 3 + jQuery | Frappe Desk (Vue/jQuery) |
| Database | MariaDB (raw queries) | MariaDB via Frappe ORM |
| Auth | PHP sessions | Frappe Role-Based Access |
| API | None (form POST) | Auto-generated REST + RPC |
| Scheduler | None | Frappe Scheduler (Redis) |
| File Storage | Local filesystem | Frappe File doctype |
| Audit Trail | None | Frappe Version History |
| Reporting | PHPExcel + custom PDF | Frappe Query Report / Print Format |
| Queue | None | RQ (Redis Queue) |
| Tests | None | `frappe.tests` / pytest |

---

## 3. Module Breakdown

| Module | Frappe Module Dir | Primary DocTypes |
|---|---|---|
| Fuel Operations | `national_oil/fuel_operations/` | Fuel Purchase, Pump Reading, Fuel Price |
| Sales | `national_oil/sales/` | Sales Entry, Sales Item, Department Sales Target |
| Inventory | `national_oil/inventory/` | Product, Brand, Inventory Receipt |
| Receivables | `national_oil/receivables/` | Customer, Customer Debt, Debt Payment |
| Payables | `national_oil/payables/` | Supplier, Supplier Credit, Credit Payment |
| Finance | `national_oil/finance/` | Petty Cash Entry, Petty Cash Account |
| HR | `national_oil/hr/` | Employee, Attendance, Leave Request, Performance Review |
| Integrations | `national_oil/integrations/` | M-Pesa Transaction, M-Pesa Config |
| Setup | `national_oil/setup/` | Department, Driver, Fuel Type |

---

## 4. Frappe App Directory Structure (Target)

```
apps/national_oil/
├── national_oil/
│   ├── __init__.py
│   ├── hooks.py                         # App-level hooks & config
│   ├── config/
│   │   ├── __init__.py
│   │   └── desktop.py                   # Workspace icons
│   ├── fuel_operations/
│   │   ├── doctype/
│   │   │   ├── fuel_purchase/
│   │   │   ├── pump_reading/
│   │   │   └── fuel_price/
│   │   └── report/
│   │       ├── fuel_stock_summary/
│   │       └── fuel_delivery_log/
│   ├── sales/
│   │   ├── doctype/
│   │   │   ├── sales_entry/
│   │   │   └── department_sales_target/
│   │   └── report/
│   │       ├── daily_sales_summary/
│   │       ├── monthly_sales_summary/
│   │       └── annual_sales_summary/
│   ├── inventory/
│   │   ├── doctype/
│   │   │   ├── product/
│   │   │   ├── brand/
│   │   │   └── inventory_receipt/
│   │   └── report/
│   │       └── stock_balance/
│   ├── receivables/
│   │   ├── doctype/
│   │   │   ├── customer/
│   │   │   ├── customer_debt/
│   │   │   └── debt_payment/
│   │   └── report/
│   │       └── customer_debt_ageing/
│   ├── payables/
│   │   ├── doctype/
│   │   │   ├── supplier/
│   │   │   ├── supplier_credit/
│   │   │   └── credit_payment/
│   │   └── report/
│   │       └── supplier_payables/
│   ├── finance/
│   │   ├── doctype/
│   │   │   ├── petty_cash_entry/
│   │   │   └── petty_cash_account/
│   │   └── report/
│   │       └── petty_cash_summary/
│   ├── hr/
│   │   ├── doctype/
│   │   │   ├── no_employee/
│   │   │   ├── attendance_record/
│   │   │   ├── leave_request/
│   │   │   └── performance_review/
│   │   └── report/
│   │       ├── attendance_summary/
│   │       └── performance_report/
│   ├── integrations/
│   │   ├── doctype/
│   │   │   ├── mpesa_transaction/
│   │   │   └── mpesa_settings/
│   │   └── api.py                       # Webhook endpoints (M-Pesa STK/C2B)
│   ├── setup/
│   │   └── doctype/
│   │       ├── department/
│   │       ├── driver/
│   │       └── fuel_type/
│   └── templates/
│       ├── pages/
│       └── print_formats/
├── docs/                                # This folder
├── pyproject.toml
└── README.md
```

---

## 5. User Roles

| Role | Access |
|---|---|
| System Manager | Full access, configuration |
| Station Manager | All modules read/write, reports |
| Pump Attendant | Pump readings, sales entry |
| Cashier | Sales, petty cash, debt payments |
| Store Keeper | Inventory receipts, fuel purchases |
| HR Officer | Employee, attendance, leave, performance |
| Accountant | Finance, receivables, payables, all reports |
| Driver | Own records only |
| Customer Portal | Own debt statement (web view) |

---

## 6. Key Business Flows

### 6.1 Fuel Delivery Flow

```
Supplier → Driver → Fuel Purchase (doctype submitted)
       ↓
   Dip measurements recorded (initial / final / actual)
       ↓
   Product stock updated (qty += actual delivered)
       ↓
   If balance > 0  → Supplier Credit created (payable)
   If fully paid   → No payable created
       ↓
   Fuel Price optionally updated
```

### 6.2 Customer Debt Flow

```
Credit Sale created → Customer Debt record opened
       ↓
   Partial or full Debt Payment recorded
       ↓
   Balance recalculated (payable - SUM(payments))
       ↓
   Debt marked Settled when balance = 0
```

### 6.3 Supplier Payables Flow

```
Fuel Purchase with balance > 0 → Supplier Credit opened
       ↓
   Credit Payment recorded
       ↓
   Outstanding balance updated
       ↓
   Credit closed when balance = 0
```

### 6.4 M-Pesa Payment Flow

```
Customer initiates payment (STK Push or C2B)
       ↓
   M-Pesa Transaction record created (pending)
       ↓
   Webhook callback received → record confirmed
       ↓
   Linked to Customer Debt → balance reduced
```

---

## 7. Scheduled Tasks

| Task | Frequency | Purpose |
|---|---|---|
| `calculate_daily_targets` | Daily 00:01 | Reset/create daily department sales targets |
| `send_debt_reminders` | Weekly | Email/SMS customers with outstanding debts |
| `auto_close_settled_debts` | Daily | Mark debts with zero balance as Settled |
| `backup_report_snapshots` | Monthly | Archive monthly summary data |

---

## 8. Integration Points

### M-Pesa (Safaricom Daraja API)
- **STK Push**: Initiate payment requests to customers
- **C2B Webhook**: Receive payment confirmations
- **Config DocType**: `M-Pesa Settings` (consumer key, secret, shortcode, passkey)

### File / Document Storage
- Frappe's built-in `File` doctype handles:
  - Delivery receipts (fuel purchase)
  - Customer photo/ID uploads
  - Employee passport/ID documents
  - Contract documents

---

## 9. Security Improvements over Legacy

| Concern | Legacy | National Oil |
|---|---|---|
| SQL Injection | Vulnerable (raw queries) | ORM-protected |
| XSS | No sanitization | Frappe auto-escapes |
| CSRF | None | Frappe CSRF token |
| Auth | Weak session | Frappe JWT + session |
| Passwords | Plaintext in PHP file | Environment / site_config |
| File Upload | No validation | Frappe file type whitelist |
| Audit Trail | None | Automatic version history |
| Role-Based Access | None | Frappe permission system |

---

## 10. Related Documents

| Document | Path |
|---|---|
| Data Model (DocType specs) | [DATA_MODEL.md](DATA_MODEL.md) |
| Module Business Logic | [MODULES.md](MODULES.md) |
| Migration Mapping | [MIGRATION_PLAN.md](MIGRATION_PLAN.md) |
| API Specifications | [API_SPECS.md](API_SPECS.md) |
