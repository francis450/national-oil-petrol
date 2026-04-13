# National Oil — API Specifications

> REST and RPC endpoints provided by the `national_oil` Frappe app.
> All endpoints are prefixed with `/api/method/national_oil.` unless otherwise noted.
> Authentication: Frappe session cookie or API key/secret header.

---

## 1. Authentication

Frappe provides built-in auth — no custom auth endpoints needed.

```
POST /api/method/login
Body: { usr, pwd }
Returns: { message: "Logged In", home_page, ... }

POST /api/method/logout

GET /api/method/frappe.auth.get_logged_user
Returns: current username
```

API key auth (for integrations):
```
Authorization: token <api_key>:<api_secret>
```

---

## 2. Standard Frappe REST Endpoints

Frappe auto-generates REST endpoints for all DocTypes.

### List records
```
GET /api/resource/{DocType}
Query params: filters, fields, limit, order_by
```

### Get single record
```
GET /api/resource/{DocType}/{name}
```

### Create
```
POST /api/resource/{DocType}
Body: { ...field values }
```

### Update
```
PUT /api/resource/{DocType}/{name}
Body: { ...updated fields }
```

### Delete
```
DELETE /api/resource/{DocType}/{name}
```

### Submit / Cancel
```
PUT /api/resource/{DocType}/{name}
Body: { docstatus: 1 }   # submit
Body: { docstatus: 2 }   # cancel
```

---

## 3. Custom API Methods

### 3.1 Fuel Operations

#### Get Current Fuel Stock

```
GET /api/method/national_oil.fuel_operations.api.get_fuel_stock

Response:
{
  "message": [
    { "fuel_type": "Petrol", "quantity": 4250.5, "unit": "Litres" },
    { "fuel_type": "Diesel", "quantity": 8100.0, "unit": "Litres" }
  ]
}
```

#### Get Current Fuel Prices

```
GET /api/method/national_oil.fuel_operations.api.get_current_prices

Response:
{
  "message": [
    {
      "fuel_type": "Petrol",
      "buying_price": 185.50,
      "selling_price_retail": 210.00,
      "selling_price_wholesale": 205.00,
      "effective_date": "2026-04-01"
    }
  ]
}
```

---

### 3.2 Sales

#### Get Sales Summary

```
GET /api/method/national_oil.sales.api.get_sales_summary

Query params:
  period: today | week | month | year
  department: (optional, Link to Department)
  sale_type: (optional, "Wet Stock" | "Other")

Response:
{
  "message": {
    "total": 125000.00,
    "period": "month",
    "breakdown": [
      { "department": "Forecourt", "amount": 98000.00 },
      { "department": "Shop", "amount": 27000.00 }
    ]
  }
}
```

---

### 3.3 Receivables

#### Get Customer Debt Balance

```
GET /api/method/national_oil.receivables.api.get_customer_balance
Query params: customer (name/link)

Response:
{
  "message": {
    "customer": "John Kamau",
    "total_payable": 15000.00,
    "total_paid": 8000.00,
    "balance": 7000.00,
    "open_debts": [
      {
        "name": "DEBT-2026-001",
        "code": "INV-001",
        "payable_amount": 7000.00,
        "balance": 7000.00,
        "dated": "2026-03-15"
      }
    ]
  }
}
```

#### Record Debt Payment

```
POST /api/method/national_oil.receivables.api.record_debt_payment
Body:
{
  "customer_debt": "DEBT-2026-001",
  "amount": 3500.00,
  "payment_method": "M-Pesa",
  "reference": "QK7XXXXXXX"
}

Response:
{
  "message": {
    "payment_name": "DPMT-2026-034",
    "remaining_balance": 3500.00
  }
}
```

---

### 3.4 M-Pesa Integration

#### Initiate STK Push

```
POST /api/method/national_oil.integrations.api.initiate_stk_push
Auth: Required (Cashier role minimum)

Body:
{
  "customer": "John Kamau",
  "phone": "0712345678",
  "amount": 3500.00,
  "debt_name": "DEBT-2026-001"   (optional)
}

Response:
{
  "message": {
    "transaction_name": "MPT-2026-089",
    "checkout_request_id": "ws_CO_...",
    "status": "Pending"
  }
}

Error:
{
  "exc_type": "ValidationError",
  "message": "Amount must be greater than 0"
}
```

#### M-Pesa Callback (Webhook)

```
POST /api/method/national_oil.integrations.api.mpesa_callback
Auth: allow_guest=True (restricted by IP whitelist at nginx level)

Body (Safaricom format):
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "...",
      "CheckoutRequestID": "ws_CO_...",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          { "Name": "Amount", "Value": 3500.00 },
          { "Name": "MpesaReceiptNumber", "Value": "QK7XXXXXXX" },
          { "Name": "PhoneNumber", "Value": 254712345678 }
        ]
      }
    }
  }
}

Response: { "ResultCode": 0, "ResultDesc": "Accepted" }
```

#### Check M-Pesa Transaction Status

```
GET /api/method/national_oil.integrations.api.check_transaction_status
Query params: checkout_request_id OR transaction_name

Response:
{
  "message": {
    "status": "Confirmed",
    "amount": 3500.00,
    "mpesa_receipt": "QK7XXXXXXX",
    "linked_debt": "DEBT-2026-001"
  }
}
```

---

### 3.5 HR

#### Get Attendance Status for Today

```
GET /api/method/national_oil.hr.api.get_today_attendance

Response:
{
  "message": {
    "total_employees": 12,
    "present": 10,
    "absent": 2,
    "absent_list": ["James Waweru", "Mary Njoki"]
  }
}
```

#### Bulk Mark Attendance

```
POST /api/method/national_oil.hr.api.bulk_mark_attendance
Body:
{
  "dated": "2026-04-11",
  "records": [
    { "employee": "EMP-001", "status": "Present", "overtime_hours": 0 },
    { "employee": "EMP-002", "status": "Absent" }
  ]
}

Response:
{
  "message": { "created": 12, "updated": 0, "errors": [] }
}
```

---

### 3.6 Dashboard Data

#### Main Dashboard Metrics

```
GET /api/method/national_oil.api.dashboard.get_dashboard_metrics

Response:
{
  "message": {
    "today_sales": 45200.00,
    "month_sales": 1250000.00,
    "year_sales": 8500000.00,
    "open_customer_debts": 14,
    "open_supplier_credits": 3,
    "fuel_stock": [
      { "fuel_type": "Petrol", "quantity": 4250.5 },
      { "fuel_type": "Diesel", "quantity": 8100.0 }
    ],
    "today_attendance": {
      "present": 10,
      "absent": 2,
      "total": 12
    }
  }
}
```

#### Sales Trend (Chart Data)

```
GET /api/method/national_oil.api.dashboard.get_sales_trend
Query params: days=7|30|365

Response:
{
  "message": {
    "labels": ["Apr 05", "Apr 06", "Apr 07", "Apr 08", "Apr 09", "Apr 10", "Apr 11"],
    "datasets": [
      {
        "name": "Wet Stock",
        "values": [38000, 41000, 39500, 45200, 43100, 47000, 45200]
      },
      {
        "name": "Other",
        "values": [8000, 9500, 7800, 9200, 8500, 10100, 9800]
      }
    ]
  }
}
```

---

## 4. Frappe Query Reports (Callable via API)

All reports can be fetched via:
```
GET /api/method/frappe.desk.query_report.run
Query params: report_name=<name>&filters=<JSON>
```

| Report Name | Key Filters |
|---|---|
| `Daily Sales Summary` | `{ "dated": "2026-04-11" }` |
| `Monthly Sales Summary` | `{ "month": 4, "year": 2026 }` |
| `Customer Debt Ageing` | `{ "as_of_date": "2026-04-11" }` |
| `Supplier Payables` | `{ "supplier": "Total Kenya" }` |
| `Petty Cash Summary` | `{ "from_date": "...", "to_date": "..." }` |
| `Fuel Delivery Log` | `{ "from_date": "...", "to_date": "..." }` |
| `Attendance Summary` | `{ "month": 4, "year": 2026 }` |
| `Performance Report` | `{ "employee": "EMP-001", "period": "Monthly" }` |

---

## 5. Webhooks Emitted by National Oil

These outgoing webhooks can be configured via Frappe's built-in Webhook doctype:

| Event | DocType | Trigger | Payload |
|---|---|---|---|
| New Fuel Delivery | Fuel Purchase | on_submit | `{ name, supplier, fuel_type, quantity, total_cost, dated }` |
| Debt Settled | Customer Debt | status→Settled | `{ name, customer, payable_amount, dated }` |
| Low Fuel Stock | Product | quantity < threshold | `{ fuel_type, quantity, threshold }` |
| Leave Approved | Leave Request | status→Approved | `{ employee, from_date, to_date, leave_type }` |

---

## 6. Error Response Format

All custom API methods follow this error format (Frappe standard):

```json
{
  "exc_type": "ValidationError",
  "exc": "...",
  "_server_messages": "[{\"message\": \"Human-readable error message\"}]"
}
```

HTTP status codes:
- `200` — success
- `400` — validation error / bad request
- `403` — permission denied
- `404` — document not found
- `500` — server error

---

## 7. Rate Limiting

Frappe applies rate limiting per user. For M-Pesa webhook endpoint:
- Whitelist Safaricom IP ranges in nginx config
- No auth token required but IP-restricted
- Log all incoming payloads to `M-Pesa Transaction.raw_payload` for audit

---

## 8. API Access by Role

| Endpoint Group | Allowed Roles |
|---|---|
| Fuel Operations | Station Manager, Store Keeper, System Manager |
| Sales | Cashier, Pump Attendant, Station Manager, Accountant |
| Receivables | Cashier, Accountant, Station Manager |
| Payables | Accountant, Station Manager |
| HR | HR Officer, Station Manager |
| M-Pesa Initiate | Cashier, Station Manager |
| M-Pesa Callback | Guest (IP-restricted) |
| Dashboard Metrics | All authenticated users |
