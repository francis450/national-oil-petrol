# National Oil — Operational to ERPNext Mapping

> Mapping guide for custom operational records that may remain in `national_oil`
> while ERPNext stays the accounting and commercial system of record.

---

## 1. Purpose

Some National Oil records are still useful as operational capture documents even when
ERPNext owns the canonical financial and stock documents.

This document defines how they should map.

---

## 2. Mapping Rules

### Fuel Purchase

Operational purpose:

- wet-stock delivery capture
- dip and seal checks
- forecourt-specific quantity verification

ERPNext targets:

- `Purchase Receipt` for stock receipt
- `Purchase Invoice` for supplier billing
- `Payment Entry` when some or all of the delivery is paid immediately

Notes:

- should not become the final accounting record
- needs a canonical `Item` for the delivered fuel product
- may remain the operational source of truth for dip-related details not modeled in ERPNext

### Inventory Receipt

Operational purpose:

- quick receiving flow for non-fuel stock

ERPNext targets:

- `Purchase Receipt`
- `Purchase Invoice`
- `Payment Entry` if paid immediately

Notes:

- should eventually become a thin operational wrapper or be collapsed into ERPNext receiving flows
- needs canonical `Item` mapping instead of relying on custom `Product`

### Sales Entry

Operational purpose:

- quick operational capture of station, car wash, cafeteria, and retail sales
- departmental performance tracking

ERPNext targets:

- `Sales Invoice`
- `Payment Entry` for non-POS settlement where needed

Notes:

- if used for cash-and-carry operations, likely maps to POS-style `Sales Invoice`
- if used for credit operations, should map to standard receivables through ERPNext `Sales Invoice`
- custom `Customer Debt` should be revisited against standard receivables once sales posting is aligned

---

## 3. Integration Principle

The frontend should use preview and bridge APIs to:

1. capture the operational record
2. preview ERPNext documents that should be created
3. surface unresolved dependencies such as missing `Item` links or missing payment configuration
4. only automate posting after mapping is explicit and test-covered

