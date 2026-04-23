# National Oil — ERPNext / HRMS Reuse Strategy

> Canonical model map for building National Oil as an operational layer on top of ERPNext and HRMS.

---

## 1. Principle

Use ERPNext and HRMS as the system of record wherever they already provide a stable business object.

Create National Oil DocTypes only for petrol-station-specific workflows that are not modeled well by the base products.

---

## 2. Canonical Standard Masters

These should not be recreated in `national_oil`:

| Business Entity | Canonical DocType | Source App | Notes |
|---|---|---|---|
| Department | `Department` | ERPNext | Shared across petrol station, car wash, cafeteria, admin |
| Customer | `Customer` | ERPNext | Use customer groups/territories/custom fields if needed |
| Supplier | `Supplier` | ERPNext | Shared for fuel, shop stock, cafeteria, services |
| Driver | `Driver` | ERPNext | Reuse for fuel delivery and logistics |
| Vehicle | `Vehicle` | ERPNext | Reuse for fleet/logistics if needed |
| Employee | `Employee` | ERPNext | Canonical worker master |
| Attendance | `Attendance` | HRMS | Canonical attendance record |
| Leave | `Leave Application` | HRMS | Canonical leave workflow |
| Expense Claim | `Expense Claim` | HRMS | Prefer for reimbursable operating costs |
| Item / Product | `Item` | ERPNext | Canonical product master for fuel, cafeteria, car wash stock and services |
| Price List | `Price List` / item prices | ERPNext | Prefer ERPNext pricing model where possible |

---

## 3. National Oil Custom DocTypes That Still Make Sense

These remain good custom candidates because they represent station-specific operational workflows:

- `Fuel Purchase`
- `Fuel Price` if ERPNext pricing is not sufficient for dated wet-stock pricing history
- `Pump Reading`
- `Sales Entry` only if it represents a non-accounting operational capture layer distinct from ERPNext POS/Sales Invoice
- `Department Sales Target`
- `Customer Debt` if it is an operations-facing credit tracker separate from formal ERPNext invoicing
- `Debt Payment`
- `Supplier Credit`
- `Credit Payment`
- `M-Pesa Transaction`

These should be revisited before final implementation if ERPNext native flows can absorb them cleanly.

---

## 4. Areas to Prefer Customization Over New DocTypes

### Customer

Prefer:

- ERPNext `Customer`
- custom fields
- customer groups for segments such as fleet, retail, cafeteria, car wash, staff, corporate

### Supplier

Prefer:

- ERPNext `Supplier`
- supplier groups for fuel vendors, FMCG vendors, service vendors

### Employee and HR

Prefer:

- ERPNext `Employee`
- HRMS `Attendance`
- HRMS `Leave Application`
- HRMS `Shift Type`
- HRMS `Shift Assignment`

Avoid:

- separate `NO Employee`
- separate `Attendance Record`
- separate `Leave Request`

unless there is a hard business rule that cannot be met with HRMS customization.

### Existing Custom HR/Logistics Records to Treat as Legacy

The current `national_oil` app already contains some overlapping custom structures.

These should be treated as legacy candidates, not future foundation models:

- `NO Employee`
- planned `Attendance Record`
- planned `Leave Request`
- custom `petrol_setup.Driver` if ERPNext `Driver` is sufficient

Preferred direction:

- stop building new UI/API dependencies on these custom records
- shift new frontend work to canonical ERPNext/HRMS APIs
- only keep overlapping custom DocTypes if they hold data or behavior that cannot be migrated cleanly

### Inventory and Products

Prefer:

- ERPNext `Item`
- ERPNext stock ledger flows
- ERPNext `Purchase Receipt`
- ERPNext `Purchase Invoice`
- ERPNext `Stock Entry`

Use National Oil custom records only where wet-stock operational capture must precede or supplement accounting stock flows.

### Existing Custom Inventory / Commercial Records to Treat Carefully

The current `national_oil` app includes overlapping custom records in this area:

- `Product`
- `Inventory Receipt`
- `Sales Entry`

Preferred direction:

- treat ERPNext `Item` as the canonical product and service master across petrol station, car wash, cafeteria, and retail
- treat ERPNext `Purchase Receipt`, `Purchase Invoice`, `Sales Invoice`, and `Payment Entry` as the canonical accounting/commercial records
- keep `Fuel Purchase`, `Pump Reading`, and other wet-stock operational captures only where they serve a true operational purpose before ERPNext posting
- avoid adding new dependencies on custom `Product` unless we explicitly decide it remains an operational abstraction over `Item`

---

## 5. Frontend API Direction

The new frontend should not talk directly in terms of “custom app owns all data.”

Instead:

- build National Oil API endpoints that aggregate ERPNext, HRMS, and National Oil data
- expose canonical master lookups for departments, customers, suppliers, drivers, employees
- keep the frontend decoupled from where the data physically lives

This lets the UI stay product-specific while ERPNext remains the back-office core.

---

## 6. Immediate Next Actions

1. Add master-data lookup APIs over ERPNext/HRMS canonical masters
2. Audit custom DocTypes that duplicate ERPNext/HRMS concepts
3. Convert planning docs to “reuse first, customize second”
4. Implement future frontend forms against canonical APIs, not duplicate master DocTypes
