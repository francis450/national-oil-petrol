# National Oil — Migration Plan

> Strategy for migrating all data and features from the legacy `bigbroco_petrol`
> PHP system into the `national_oil` Frappe app.

---

## 1. Migration Overview

| Phase | Name | Scope |
|---|---|---|
| 0 | Preparation | Schema finalization, environment setup, backup |
| 1 | Master Data | Departments, Suppliers, Customers, Employees, Brands, Drivers, Fuel Types |
| 2 | Fuel & Inventory | Fuel Purchases, Inventory Receipts, Products, Fuel Prices |
| 3 | Financial Records | Customer Debts, Supplier Credits, Debt Payments, Credit Payments, Petty Cash |
| 4 | Sales History | Sales Entries, Sales Targets |
| 5 | HR Records | Attendance, Leave Requests, Performance Reviews |
| 6 | Integrations | M-Pesa Transactions |
| 7 | Cutover | DNS/URL switch, legacy system freeze, parallel run |

---

## 2. Phase 0 — Preparation

### 2.1 Legacy Database Backup

```bash
# On legacy server
mysqldump -u bigbroco_john -p bigbroco_petrol > bigbroco_petrol_backup_$(date +%F).sql

# Verify row counts before migration
mysql -u bigbroco_john -p bigbroco_petrol -e "
  SELECT table_name, table_rows
  FROM information_schema.tables
  WHERE table_schema = 'bigbroco_petrol'
  ORDER BY table_name;
"
```

### 2.2 Direct Database Access for Migration

```bash
# Frappe site DB credentials from:
cat /home/frappeuser/frappe-bench/sites/national-oil/site_config.json
# db_name: _4061ec13d1011333
# db_password: (see file)
```

### 2.3 Migration Script Setup

```
apps/national_oil/national_oil/migrations/
├── __init__.py
├── config.py          # Source DB connection config
├── utils.py           # Shared helpers (clean_phone, safe_date, etc.)
├── phase1_masters.py
├── phase2_fuel.py
├── phase3_finance.py
├── phase4_sales.py
├── phase5_hr.py
├── phase6_mpesa.py
└── run_all.py         # Orchestrator with rollback on failure
```

---

## 3. Phase 1 — Master Data Migration

### Source → Target Mapping

#### Departments (`departments` → `Department`)

```python
import frappe
import MySQLdb

src = MySQLdb.connect(host="legacy_host", user="bigbroco_john",
                      passwd="...", db="bigbroco_petrol")
cur = src.cursor(MySQLdb.cursors.DictCursor)

cur.execute("SELECT * FROM departments")
for row in cur.fetchall():
    if not frappe.db.exists("Department", row["department"]):
        doc = frappe.new_doc("Department")
        doc.department_name = row["department"]
        doc.insert(ignore_permissions=True)

frappe.db.commit()
```

#### Suppliers (`suppliers` → `Supplier`)

```python
cur.execute("SELECT * FROM suppliers")
for row in cur.fetchall():
    doc = frappe.new_doc("Supplier")
    doc.supplier_name   = row["name"]
    doc.account_number  = row.get("account", "")
    doc.phone           = row.get("phone", "")
    doc.email           = row.get("email", "")
    doc.address         = row.get("address", "")
    doc.insert(ignore_permissions=True)
```

#### Customers (`customers` → `Customer`)

```python
cur.execute("SELECT * FROM customers")
for row in cur.fetchall():
    doc = frappe.new_doc("Customer")
    doc.customer_name = row["name"]
    doc.email         = row.get("email", "")
    doc.phone         = row.get("phone", "")
    # Photo: migrate file separately if passportlocation exists
    doc.insert(ignore_permissions=True)
```

#### Employees (`worker` → `Employee`)

```python
cur.execute("SELECT * FROM worker")
for row in cur.fetchall():
    doc = frappe.new_doc("Employee")
    doc.employee_name = row["name"]
    doc.phone         = row.get("phone", "")
    doc.address       = row.get("address", "")
    doc.location      = row.get("location", "")
    doc.profession    = row.get("profession", "")
    doc.designation   = row.get("designation", "Casual")
    doc.insert(ignore_permissions=True)
```

#### Drivers (`drivers` → `Driver`)

```python
cur.execute("SELECT * FROM drivers")
for row in cur.fetchall():
    doc = frappe.new_doc("Driver")
    doc.driver_name       = row["driver"]
    doc.phone             = row.get("phone", "")
    doc.email             = row.get("email", "")
    doc.car_plate         = row.get("car", "")
    # Map supplier name → Supplier doctype
    supplier = frappe.db.get_value("Supplier", {"supplier_name": row.get("supplier")})
    doc.supplier          = supplier
    doc.insert(ignore_permissions=True)
```

#### Brands (`brands` → `Brand`)

```python
cur.execute("SELECT * FROM brands")
for row in cur.fetchall():
    supplier = frappe.db.get_value("Supplier", {"supplier_name": row.get("supplier")})
    doc = frappe.new_doc("Brand")
    doc.brand_name = row["brandname"]
    doc.supplier   = supplier
    doc.insert(ignore_permissions=True)
```

---

## 4. Phase 2 — Fuel & Inventory Migration

### Fuel Purchases (`fuel` → `Fuel Purchase`)

```python
cur.execute("SELECT * FROM fuel ORDER BY dated ASC")
for row in cur.fetchall():
    doc = frappe.new_doc("Fuel Purchase")
    doc.code             = row["code"]
    doc.dated            = row["dated"]
    doc.supplier         = resolve_supplier(row["supplier"])
    doc.driver           = resolve_driver(row["driver"])
    doc.car_plate        = row.get("car", "")
    doc.fuel_type        = resolve_fuel_type(row.get("fuel", ""))
    doc.initial_dip      = flt(row.get("initdip"))
    doc.final_dip        = flt(row.get("finaldip"))
    doc.actual_quantity  = flt(row.get("actual"))
    doc.unit_cost        = flt(row.get("unitcost"))
    doc.total_cost       = flt(row.get("totalcost"))
    doc.amount_paid      = flt(row.get("paid"))
    doc.balance          = flt(row.get("balance"))
    doc.payment_method   = map_payment_method(row.get("paymentmethod"))
    doc.temperature      = flt(row.get("temperature"))
    doc.density          = flt(row.get("density"))
    doc.seal_condition   = row.get("seal", "")
    doc.comments         = row.get("comment", "")
    doc.insert(ignore_permissions=True)
    # Submit but skip on_submit side effects (stock/debt already in legacy)
    doc.flags.ignore_validate_update_after_submit = True
    doc.submit()
```

**Important**: Set a migration flag `doc.flags.migration_mode = True` in controller
`on_submit` to skip re-creating supplier credits and re-adjusting stock (data already
captured in subsequent phases).

### Products (`products` → `Product`)

```python
cur.execute("SELECT * FROM products")
for row in cur.fetchall():
    doc = frappe.new_doc("Product")
    doc.product_name             = row["fuel"]
    doc.quantity                 = flt(row.get("qnty", 0))
    doc.buying_price             = flt(row.get("bp", 0))
    doc.selling_price            = flt(row.get("sp", 0))
    doc.selling_price_wholesale  = flt(row.get("spw", 0))
    doc.is_fuel                  = 1
    doc.insert(ignore_permissions=True)
```

### Inventory Receipts (`inventory` → `Inventory Receipt`)

Similar pattern to Fuel Purchase — map columns, submit with `migration_mode=True`.

---

## 5. Phase 3 — Financial Records Migration

### Customer Debts (`customerdebts` → `Customer Debt`)

```python
cur.execute("SELECT * FROM customerdebts ORDER BY code ASC")
for row in cur.fetchall():
    doc = frappe.new_doc("Customer Debt")
    doc.code            = row["code"]
    doc.customer        = resolve_customer(row["customer"])
    doc.payable_amount  = abs(flt(row.get("payable", 0)))
    doc.receipt         = row.get("receipt", "")
    # dated: legacy may not have this field — default to today or lookup from fuel/sales
    doc.dated           = row.get("dated") or frappe.utils.today()
    doc.insert(ignore_permissions=True)
    doc.submit()
```

### Debt Payments (`debtpayment` → `Debt Payment`)

```python
cur.execute("SELECT * FROM debtpayment ORDER BY code ASC")
for row in cur.fetchall():
    debt_name = frappe.db.get_value("Customer Debt", {"code": row["code"]})
    if not debt_name:
        continue
    doc = frappe.new_doc("Debt Payment")
    doc.customer_debt   = debt_name
    doc.amount          = abs(flt(row.get("amount", 0)))
    doc.dated           = frappe.utils.today()  # legacy lacks dated field
    doc.insert(ignore_permissions=True)
    doc.submit()
```

### Supplier Credits & Credit Payments

Follow the same pattern as Customer Debts / Debt Payments above, mapping from `debts`
and `debtpayment` tables.

**Filter**: `WHERE amount < 0` in `debts` = supplier payable; `amount > 0` = customer debt.

### Petty Cash (`pettycash` → `Petty Cash Entry`)

```python
cur.execute("SELECT * FROM pettycash ORDER BY dated ASC")
for row in cur.fetchall():
    doc = frappe.new_doc("Petty Cash Entry")
    doc.dated       = row["dated"]
    doc.amount      = flt(row.get("amount", 0))
    doc.description = row.get("detail", "Petty Cash")
    doc.insert(ignore_permissions=True)
    doc.submit()
```

---

## 6. Phase 4 — Sales History Migration

### Sales (`sales` → `Sales Entry`)

```python
cur.execute("SELECT * FROM sales ORDER BY dated ASC")
for row in cur.fetchall():
    doc = frappe.new_doc("Sales Entry")
    doc.dated       = row["dated"]
    doc.amount      = flt(row.get("amount", 0))
    doc.department  = resolve_department(row.get("department"))
    # Determine sale_type from department name or a legacy flag
    doc.sale_type   = classify_sale_type(row)
    doc.insert(ignore_permissions=True)
    doc.submit()
```

---

## 7. Phase 5 — HR Records Migration

### Attendance (`attendance` → `Attendance Record`)

```python
cur.execute("SELECT * FROM attendance ORDER BY dated ASC")
for row in cur.fetchall():
    employee = frappe.db.get_value("Employee", {"employee_name": row["name"]})
    if not employee:
        continue
    doc = frappe.new_doc("Attendance Record")
    doc.employee        = employee
    doc.dated           = row["dated"]
    doc.status          = map_attendance_status(row.get("attendance"))
    doc.overtime_hours  = flt(row.get("overtime", 0))
    doc.insert(ignore_permissions=True)
```

### Performance Reviews (`performance` → `Performance Review`)

```python
cur.execute("SELECT * FROM performance ORDER BY dated ASC")
for row in cur.fetchall():
    employee = frappe.db.get_value("Employee", {"employee_name": row["name"]})
    doc = frappe.new_doc("Performance Review")
    doc.employee    = employee
    doc.dated       = row["dated"]
    doc.target      = flt(row.get("target", 0))
    doc.hit         = flt(row.get("hit", 0))
    doc.deviation   = flt(row.get("deviation", 0))
    doc.period      = "Daily"
    doc.insert(ignore_permissions=True)
```

---

## 8. Phase 6 — M-Pesa Transactions

### M-Pesa (`mpesatransactions` → `M-Pesa Transaction`)

```python
cur.execute("SELECT * FROM mpesatransactions ORDER BY dated ASC")
for row in cur.fetchall():
    doc = frappe.new_doc("M-Pesa Transaction")
    doc.transaction_id  = row.get("transaction_id") or row.get("code")
    doc.dated           = row.get("dated")
    doc.phone           = row.get("phone", "")
    doc.amount          = flt(row.get("amount", 0))
    doc.status          = "Confirmed"
    doc.insert(ignore_permissions=True)
```

---

## 9. Phase 7 — Cutover

### Pre-Cutover Checklist

- [ ] All Phase 1–6 migrations completed and verified (row counts match)
- [ ] User accounts created in Frappe with correct roles
- [ ] Print Formats tested and approved by station manager
- [ ] All reports producing correct figures vs legacy comparison
- [ ] M-Pesa callback URL updated to national_oil Frappe URL
- [ ] Staff training completed (2–3 days minimum)
- [ ] Parallel run completed for at least 3 business days

### Cutover Steps

1. **Freeze legacy system** — set maintenance mode in PHP app
2. **Final incremental sync** — run migration scripts for records created since Phase 6
3. **Verify record counts** (see Verification section below)
4. **Switch DNS / URL** to national_oil Frappe instance
5. **Monitor** for 48 hours — keep legacy DB read-only as fallback

### Rollback Plan

If critical issues arise within 72 hours of cutover:
1. Re-point DNS to legacy PHP server
2. Legacy DB was read-only — no data loss
3. Investigate and fix in Frappe
4. Schedule new cutover window

---

## 10. Data Verification Queries

Run these against both databases to confirm migration integrity:

```sql
-- Legacy: bigbroco_petrol
SELECT COUNT(*) FROM fuel;            -- should match Fuel Purchase count
SELECT COUNT(*) FROM customers;       -- should match Customer count
SELECT COUNT(*) FROM customerdebts;   -- should match Customer Debt count
SELECT COUNT(*) FROM debtpayment;     -- should match Debt Payment count
SELECT COUNT(*) FROM sales;           -- should match Sales Entry count
SELECT COUNT(*) FROM attendance;      -- should match Attendance Record count
SELECT COUNT(*) FROM performance;     -- should match Performance Review count

-- Frappe: verify totals
SELECT SUM(payable_amount) FROM `tabCustomer Debt`;
SELECT SUM(total_amount) FROM `tabSupplier Credit`;
SELECT SUM(amount) FROM `tabSales Entry`;
```

---

## 11. Known Data Quality Issues in Legacy

| Issue | Affected Table | Resolution |
|---|---|---|
| `dated` field missing from `debtpayment` | debtpayment | Default to `fuel.dated` of linked delivery or TODAY |
| Customer names not normalized (duplicates) | customers | Deduplicate before migration; keep first, merge debts |
| Supplier names inconsistent case | suppliers | Title-case normalize all names |
| NULL phone numbers | all | Insert empty string `""` |
| `amount < 0` in debts = payable, `> 0` = receivable | debts | Split into two DocTypes based on sign |
| Receipt filenames stored as relative paths | fuel, inventory | Re-attach from `legacy-petrol/receipts/` filesystem |
| `passportlocation` photo paths | worker, customers | Re-attach from `legacy-petrol/customers/` filesystem |

---

## 12. Helper Functions Reference

```python
# apps/national_oil/national_oil/migrations/utils.py

def resolve_supplier(legacy_name):
    return frappe.db.get_value("Supplier", {"supplier_name": legacy_name}) or None

def resolve_customer(legacy_name):
    return frappe.db.get_value("Customer", {"customer_name": legacy_name}) or None

def resolve_department(legacy_name):
    return frappe.db.get_value("Department", {"department_name": legacy_name}) or None

def resolve_driver(legacy_name):
    return frappe.db.get_value("Driver", {"driver_name": legacy_name}) or None

def resolve_fuel_type(legacy_fuel):
    mapping = {"petrol": "Petrol", "diesel": "Diesel", "kerosene": "Kerosene"}
    return mapping.get(legacy_fuel.lower(), legacy_fuel.title())

def map_payment_method(legacy_val):
    mapping = {
        "cash": "Cash",
        "mpesa": "M-Pesa",
        "cheque": "Cheque",
        "bank": "Bank Transfer",
    }
    return mapping.get((legacy_val or "").lower(), "Cash")

def map_attendance_status(legacy_val):
    mapping = {"present": "Present", "absent": "Absent", "1": "Present", "0": "Absent"}
    return mapping.get(str(legacy_val).lower(), "Present")

def flt(val, precision=2):
    try:
        return round(float(val or 0), precision)
    except (ValueError, TypeError):
        return 0.0

def classify_sale_type(row):
    dept = (row.get("department") or "").lower()
    if "pump" in dept or "fuel" in dept or "wet" in dept:
        return "Wet Stock"
    return "Other"
```
