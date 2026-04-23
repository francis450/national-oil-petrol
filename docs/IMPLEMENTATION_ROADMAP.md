# National Oil — Implementation Roadmap

> Practical build plan for closing the gap between the current `national_oil`
> app and the intended product described in `IMPLEMENTATION.md`.

---

## 1. Current State Summary

The app already has a meaningful backend foundation:

- Many transactional DocTypes exist for fuel, inventory, sales, receivables, payables, finance, and M-Pesa
- Basic Vue SPA shell exists with login, dashboard, sidebar, and some route groups
- Core controller logic exists for stock movement, debt/credit balance updates, and basic validations

The largest gaps are:

- Missing reuse strategy for ERPNext/HRMS standard masters and HR records
- Missing frontend/API layer over ERPNext/HRMS canonical masters
- Most SPA views are placeholders or mock-data screens
- Reports, print formats, workspaces, and operational polish are mostly absent
- Some auth, role, and routing assumptions are inconsistent

---

## 2. Recommended Delivery Strategy

Build in this order:

1. Stabilize foundations
2. Lock canonical ERPNext/HRMS master data usage
3. Fix route/auth/role inconsistencies
4. Deliver working CRUD for the most business-critical modules
5. Add dashboard/reporting polish
6. Complete HR, reports, print formats, and scheduled-task hardening

This sequence minimizes rework because the missing master DocTypes are dependencies for many existing records and screens.

---

## 3. Phase Plan

### Phase 0 — Alignment and Cleanup

**Goal**: Remove contradictions before adding new features.

**Estimated effort**: 0.5-1 day

**Deliverables**

- Choose one primary role model:
  - keep `Station Manager` and remove `Petrol Manager`, or
  - keep `Petrol Manager` and remap permissions consistently
- Choose one frontend entry path:
  - `/petrol`
  - `/national-oil/...`
  - `/app/petrol`
- Fix duplicated/overwritten dashboard API functions
- Confirm which modules are in scope for MVP vs later phases

**Files to review/update**

- `apps/national_oil/national_oil/api/auth.py`
- `apps/national_oil/national_oil/api/dashboard.py`
- `apps/national_oil/national_oil/hooks.py`
- `apps/national_oil/national_oil/setup_petrol_app.py`
- `apps/national_oil/national_oil/www/petrol.py`
- `apps/national_oil/national_oil/www/petrol.html`
- `apps/national_oil/frontend/src/router/index.ts`
- `apps/national_oil/frontend/src/api/client.ts`

**Acceptance criteria**

- Auth helper, fixtures, DocType permissions, and setup script all agree on the same role names
- SPA mounts and redirects using one consistent route strategy
- `dashboard.py` exports one clear implementation for each public API method

---

### Phase 1 — Canonical Masters and Customization Baseline

**Goal**: Reuse ERPNext/HRMS standard masters instead of recreating them.

**Estimated effort**: 1-2 days

**Must define as canonical**

- ERPNext `Department`
- ERPNext `Supplier`
- ERPNext `Customer`
- ERPNext `Driver`
- ERPNext `Employee`
- HRMS `Attendance`
- HRMS `Leave Application`

**Should verify after alignment**

- Existing Link fields resolve cleanly
- Frontend can consume these masters through app APIs
- Role permissions align with the chosen role model
- Naming, search fields, and list views are usable for operations staff

**Files likely needed**

- API wrappers over ERPNext/HRMS masters
- customization fixtures or custom-field definitions where justified
- canonical mapping documentation

**Existing files to update**

- `apps/national_oil/docs/IMPLEMENTATION.md`
- `apps/national_oil/docs/DATA_MODEL.md`
- `apps/national_oil/national_oil/modules.txt`

**Acceptance criteria**

- No duplicate National Oil DocTypes are created for ERPNext/HRMS standard masters
- Existing National Oil DocTypes can link to canonical ERPNext/HRMS masters from the UI and API

---

### Phase 2 — Core Transaction Stability

**Goal**: Finish the backend business rules before building more screens.

**Estimated effort**: 2-3 days

**Focus areas**

- Validate `Sales Entry` more fully:
  - future-date restriction
  - credit-sale flow
  - optional stock impact rules if needed for non-fuel products
- Validate `Fuel Purchase` against expected spec:
  - unique code handling
  - optional buying-price update behavior
  - cancellation edge cases
- Validate `Inventory Receipt` supplier-credit creation and stock math
- Confirm `Customer Debt`, `Debt Payment`, `Supplier Credit`, `Credit Payment` cover real-life station workflows
- Add test coverage for controller side effects

**Files to review/update**

- `apps/national_oil/national_oil/fuel_operations/doctype/fuel_purchase/fuel_purchase.py`
- `apps/national_oil/national_oil/fuel_operations/doctype/fuel_price/fuel_price.py`
- `apps/national_oil/national_oil/inventory/doctype/inventory_receipt/inventory_receipt.py`
- `apps/national_oil/national_oil/inventory/doctype/product/product.py`
- `apps/national_oil/national_oil/sales/doctype/sales_entry/sales_entry.py`
- `apps/national_oil/national_oil/receivables/doctype/customer_debt/customer_debt.py`
- `apps/national_oil/national_oil/receivables/doctype/debt_payment/debt_payment.py`
- `apps/national_oil/national_oil/payables/doctype/supplier_credit/supplier_credit.py`
- `apps/national_oil/national_oil/payables/doctype/credit_payment/credit_payment.py`
- `apps/national_oil/national_oil/hooks.py`

**New files likely needed**

- tests for critical DocType workflows under each module, for example:
  - `.../fuel_purchase/test_fuel_purchase.py`
  - `.../inventory_receipt/test_inventory_receipt.py`
  - `.../debt_payment/test_debt_payment.py`
  - `.../credit_payment/test_credit_payment.py`

**Acceptance criteria**

- Submitting and cancelling the core transaction DocTypes produces correct stock and balance outcomes
- Critical workflows are covered by tests

---

### Phase 3 — Fuel, Receivables, and Payables UI

**Goal**: Turn the placeholder operational modules into usable working screens.

**Estimated effort**: 4-6 days

**Priority screens**

- Fuel Purchases
- Pump Readings
- Fuel Prices
- Customer Debts
- Debt Payments
- Supplier Credits
- Credit Payments

**What “done” means**

- Real API-backed list pages
- Create/edit flows
- Filters and status chips
- Submit/cancel actions where relevant
- Empty states and validation errors

**Frontend files to build/update**

- `apps/national_oil/frontend/src/router/index.ts`
- `apps/national_oil/frontend/src/views/fuel/FuelPurchaseListView.vue`
- `apps/national_oil/frontend/src/views/fuel/PumpReadingListView.vue`
- `apps/national_oil/frontend/src/views/fuel/FuelPriceListView.vue`
- `apps/national_oil/frontend/src/views/receivables/CustomerDebtListView.vue`
- `apps/national_oil/frontend/src/views/receivables/DebtPaymentListView.vue`
- `apps/national_oil/frontend/src/views/payables/SupplierCreditListView.vue`
- `apps/national_oil/frontend/src/views/payables/CreditPaymentListView.vue`
- shared composables/API files to be added under:
  - `apps/national_oil/frontend/src/api/`
  - `apps/national_oil/frontend/src/stores/`
  - `apps/national_oil/frontend/src/components/`

**Backend files to add/update**

- `apps/national_oil/national_oil/api/fuel.py`
- `apps/national_oil/national_oil/api/receivables.py`
- likely a new payables API module if list/action helpers are needed:
  - `apps/national_oil/national_oil/api/payables.py`

**Acceptance criteria**

- No “coming soon” placeholders remain for fuel, receivables, and payables
- Staff can complete the main cash/credit/fuel workflows from the SPA

---

### Phase 4 — Sales and Dashboard Real Data

**Goal**: Replace mock-data screens with live operational views.

**Estimated effort**: 2-4 days

**Work items**

- Connect dashboard cards/charts to real store/API data
- Replace hardcoded sales table rows with backend data
- Replace hardcoded sales target rows with backend data
- Add create/edit flows for sales entry and sales targets
- Align dashboard metrics payload with frontend expectations

**Frontend files to update**

- `apps/national_oil/frontend/src/views/dashboard/DashboardView.vue`
- `apps/national_oil/frontend/src/views/sales/SalesEntryListView.vue`
- `apps/national_oil/frontend/src/views/sales/SalesTargetListView.vue`
- `apps/national_oil/frontend/src/stores/dashboard.ts`
- `apps/national_oil/frontend/src/api/dashboard.ts`
- add sales API/store files under:
  - `apps/national_oil/frontend/src/api/`
  - `apps/national_oil/frontend/src/stores/`

**Backend files to update**

- `apps/national_oil/national_oil/api/dashboard.py`
- `apps/national_oil/national_oil/api/sales.py`

**Acceptance criteria**

- Dashboard uses live metrics
- Sales pages use real records, not fixture arrays
- Dashboard and backend payloads agree on field names and shapes

---

### Phase 5 — Inventory, Finance, and HR Module Completion

**Goal**: Complete the modules already implied by the menu/spec but absent from the router/UI.

**Estimated effort**: 4-6 days

**Inventory**

- Inventory list and receipt flow
- Product views

**Finance**

- Petty cash account screens
- Petty cash entry screens

**HR**

- Build missing DocTypes:
  - `Attendance Record`
  - `Leave Request`
- Add employee, attendance, leave, and performance screens

**Files likely needed**

- new frontend views/layout routes for:
  - `inventory`
  - `finance`
  - `hr`
- new backend HR DocType files:
  - `apps/national_oil/national_oil/petrol_hr/doctype/attendance_record/attendance_record.json`
  - `apps/national_oil/national_oil/petrol_hr/doctype/attendance_record/attendance_record.py`
  - `apps/national_oil/national_oil/petrol_hr/doctype/leave_request/leave_request.json`
  - `apps/national_oil/national_oil/petrol_hr/doctype/leave_request/leave_request.py`

**Acceptance criteria**

- Sidebar routes are real and navigable
- HR module is no longer partial scaffold only
- Inventory and finance workflows can be completed in the SPA

---

### Phase 6 — Reports, Print Formats, and Workspaces

**Goal**: Add management visibility and operational outputs.

**Estimated effort**: 2-4 days

**Reports to prioritize**

- Sales summary
- Outstanding customer debts
- Outstanding supplier credits
- Fuel stock levels
- Pump reading variance
- Department performance vs target

**Likely file areas**

- `apps/national_oil/national_oil/*/report/`
- `apps/national_oil/national_oil/print_format/` or module-specific print-format folders
- workspace or desk configuration files under app config/module paths

**Acceptance criteria**

- Managers can print/export the most important reports without relying on the legacy system

---

### Phase 7 — Integration and Operations Hardening

**Goal**: Make the app production-safe.

**Estimated effort**: 2-3 days

**Work items**

- Harden M-Pesa callback and transaction reconciliation
- Replace stubbed scheduled tasks with production-ready behavior
- Add monthly snapshot/report archive logic
- Add better error logging and audit visibility
- Verify permissions by role in real user journeys

**Files to update**

- `apps/national_oil/national_oil/api/mpesa.py`
- `apps/national_oil/national_oil/tasks.py`
- `apps/national_oil/national_oil/hooks.py`

**Acceptance criteria**

- Background jobs do real operational work
- Payment callback path is auditable and recoverable
- Production role-based access is verified

---

## 4. Suggested MVP Cut

If we want the fastest route to a usable first release, treat the MVP as:

- Phase 0
- Phase 1
- Phase 2
- Phase 3
- Phase 4

That would give us:

- working ERPNext/HRMS-backed master data
- working fuel operations
- working sales
- working receivables/payables
- a real dashboard

This is the smallest slice that can realistically replace daily station operations.

---

## 5. Risks and Dependencies

### High-risk dependencies

- Lack of canonical reuse rules can lead to duplicate masters and fragmented operations
- Role mismatch (`Station Manager` vs `Petrol Manager`) can cause silent access issues
- Route mismatch can create login loops or broken navigation
- Dashboard payload mismatch can break the first screen users land on

### Medium-risk areas

- Stock math for inventory receipts vs product subunits
- Fuel purchase cancellation side effects
- Debt/credit balance integrity after edits and cancellations
- M-Pesa callback reliability and replay handling

### Low-risk but still important

- Print formats
- workspace polish
- profile/settings UX

---

## 6. Rough Timeline

Assuming one focused engineer:

- Phase 0: 0.5-1 day
- Phase 1: 1-2 days
- Phase 2: 2-3 days
- Phase 3: 4-6 days
- Phase 4: 2-4 days
- Phase 5: 4-6 days
- Phase 6: 2-4 days
- Phase 7: 2-3 days

**MVP total**: about 10-16 working days  
**Full roadmap total**: about 17.5-29 working days

With two engineers split across backend and frontend after Phase 1, the schedule can compress materially.

---

## 7. Recommended First Sprint

If we start immediately, the first sprint should be:

1. Normalize roles and route strategy
2. Lock ERPNext/HRMS canonical masters and expose them through stable APIs
3. Fix `dashboard.py` duplication and payload shape
4. Add tests for fuel purchase, debt payment, and credit payment
5. Replace the Fuel Purchases placeholder with a real list page

This sprint gives us the highest leverage and removes the biggest blockers early.

---

## 8. Implementation Order by File Group

### Backend first

- `national_oil/api/`
- missing `petrol_setup` DocTypes
- missing `petrol_hr` DocTypes
- controller validations and tests

### Frontend second

- router alignment
- API clients/stores
- operational list/form views
- dashboard live data wiring

### Platform and ops last

- reports
- print formats
- scheduled tasks
- workspace polish

---

## 9. Definition of Done

A phase should be considered complete only when:

- code exists
- migrations run
- affected routes render
- backend endpoints return real data
- no placeholder text remains for the scoped feature
- critical workflows are tested
- role permissions are verified manually
