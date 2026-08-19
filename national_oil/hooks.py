app_name = "national_oil"
app_title = "National oil"
app_publisher = "ERP Kenya"
app_description = "A custom frappe app to manage a petrol station in kenya"
app_email = "franciskamande2001@gmail.com"
app_license = "mit"

# Fixtures — synced with bench export-fixtures / migrate
fixtures = [
    {
        "doctype": "Role",
        "filters": [
            ["name", "in", [
                "Station Manager",
                "Pump Attendant",
                "Cashier",
                "Store Keeper",
                "HR Officer",
                "Accountant",
                "Driver",
                "Petrol Manager",
            ]],
        ],
    },
    {
        "doctype": "Custom Field",
        "filters": [
            ["dt", "=", "Shift Assignment"],
        ],
    },
]

# Document Events
# Note: Debt Payment, Credit Payment, Fuel Purchase, and Inventory Receipt already
# implement on_submit/on_cancel natively on their Document controller classes — Frappe
# calls those automatically. A doc_events entry pointing at "Class.method" is not a
# valid module path for hook resolution and breaks submit for these doctypes; do not
# re-add these without pointing at a plain function.

# Scheduled Tasks
# auto_settle_debts and send_debt_reminders are parked along with Receivables (see
# docs/ERP_REUSE_STRATEGY.md) and intentionally not scheduled here. backup_report_snapshot
# was a no-op stub and has been removed.
scheduler_events = {
    "daily": [
        "national_oil.tasks.settle_supplier_credits",
        "national_oil.tasks.refresh_sales_targets",
    ],
}

# Vue SPA route — any deep link under /petrol/* must resolve to the same page
# (national_oil/www/petrol.html) so vue-router's client-side history routing can
# take over after load. Without this, reloading on a sub-route 404s server-side.
website_route_rules = [
    {"from_route": "/petrol/<path:app_path>", "to_route": "petrol"},
]
