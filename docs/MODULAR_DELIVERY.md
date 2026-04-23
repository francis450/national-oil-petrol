# National Oil — Modular Delivery and Testability Guide

> Working agreement for implementing `national_oil` in small, testable slices.

---

## 1. Delivery Principle

Every module should be delivered in the same order:

1. Scope the slice
2. Finish backend model and rules
3. Add DocType/API tests
4. Add UI only after backend is stable
5. Verify manually with the intended role

This keeps modules independently testable and avoids building UI on unstable backend behavior.

---

## 2. Module Order

Implement modules in this dependency order:

1. `petrol_setup`
   - reuse ERPNext `Department`
   - reuse ERPNext `Supplier`
   - reuse ERPNext `Customer`
   - reuse ERPNext `Driver`
   - verify/customize existing `Fuel Type`, `Brand`
2. `sales`
   - `Sales Entry`
   - `Department Sales Target`
3. `receivables`
   - `Customer Debt`
   - `Debt Payment`
4. `payables`
   - `Supplier Credit`
   - `Credit Payment`
5. `fuel_operations`
   - `Fuel Price`
   - `Fuel Purchase`
   - `Pump Reading`
6. `inventory`
   - `Product`
   - `Inventory Receipt`
7. `finance`
   - `Petty Cash Account`
   - `Petty Cash Entry`
8. `petrol_hr`
   - `NO Employee`
   - `Attendance Record`
   - `Leave Request`
   - `Performance Review`
9. `mpesa`
   - `M-Pesa Settings`
   - `M-Pesa Transaction`
10. dashboards, reports, print formats, scheduled jobs

---

## 3. Done Checklist Per Slice

Each slice is only done when all of these exist:

- canonical source DocType chosen
- no duplicate standard master created if ERPNext/HRMS already provides it
- Python controller or API logic completed where customization is needed
- `test_*.py` DocType/API test added where behavior is custom
- linked dependencies documented
- permissions reviewed
- API contract reviewed if the UI depends on it

For UI-backed slices, also require:

- router entry
- API client/store wiring
- live data instead of placeholders
- manual verification notes

---

## 4. Test Conventions

Use the bench-standard Frappe pattern:

- Place tests next to the customized DocType or API module as `test_*.py`
- Use `FrappeTestCase`
- Keep each test focused on one rule
- Roll back DB changes in `tearDown`

Prioritize these test types:

- creation and naming
- unique constraints
- required validation rules
- submit/cancel side effects
- balance/stock recalculation
- permission-sensitive API behaviors

---

## 5. Backend Before UI Rule

For each module:

- reuse ERPNext/HRMS masters first
- add custom fields/property setters or API wrappers only when needed
- then finish controller validations
- then add tests
- only then expose the feature in the SPA

This is especially important for:

- `sales`
- `receivables`
- `payables`
- `fuel_operations`

because they affect balances and stock.

---

## 6. First Three Implementation Slices

### Slice 1

Canonical master-data layer over ERPNext/HRMS

- define canonical masters for frontend/API use
- expose reusable lookup APIs for ERPNext `Department`, `Supplier`, `Customer`, `Driver`
- add tests for allowed-doctype lookup behavior

### Slice 2

Customization audit for reusable ERPNext/HRMS masters

- identify required custom fields or property setters on ERPNext `Customer`, `Supplier`, `Item`, `Employee`
- verify `Brand`, `Fuel Purchase`, `Inventory Receipt`, `Supplier Credit` links

### Slice 3

Transactional modules that stay custom to National Oil

- keep petrol-specific transactional DocTypes in `national_oil`
- verify `Sales Entry`, `Customer Debt`, `Debt Payment`, `M-Pesa Transaction` links to canonical ERPNext masters

---

## 7. Phase Gate

Do not start broad frontend work for inventory, finance, HR, or reports until:

- ERPNext `Department`
- ERPNext `Supplier`
- ERPNext `Customer`

are confirmed as the canonical master records and exposed through stable APIs.
