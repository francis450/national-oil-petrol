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
            ]],
        ],
    },
]

# Document Events
doc_events = {
    "Debt Payment": {
        "on_submit": "national_oil.receivables.doctype.debt_payment.debt_payment.DebtPayment.on_submit",
        "on_cancel": "national_oil.receivables.doctype.debt_payment.debt_payment.DebtPayment.on_cancel",
    },
    "Credit Payment": {
        "on_submit": "national_oil.payables.doctype.credit_payment.credit_payment.CreditPayment.on_submit",
        "on_cancel": "national_oil.payables.doctype.credit_payment.credit_payment.CreditPayment.on_cancel",
    },
    "Fuel Purchase": {
        "on_submit": "national_oil.fuel_operations.doctype.fuel_purchase.fuel_purchase.FuelPurchase.on_submit",
        "on_cancel": "national_oil.fuel_operations.doctype.fuel_purchase.fuel_purchase.FuelPurchase.on_cancel",
    },
    "Inventory Receipt": {
        "on_submit": "national_oil.inventory.doctype.inventory_receipt.inventory_receipt.InventoryReceipt.on_submit",
        "on_cancel": "national_oil.inventory.doctype.inventory_receipt.inventory_receipt.InventoryReceipt.on_cancel",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "national_oil.tasks.auto_settle_debts",
        "national_oil.tasks.refresh_sales_targets",
    ],
    "weekly": [
        "national_oil.tasks.send_debt_reminders",
    ],
    "monthly": [
        "national_oil.tasks.backup_report_snapshot",
    ],
}

# Vue SPA route — catch-all served by Frappe page
website_route_rules = [
    {"from_route": "/national-oil/<path:app_path>", "to_route": "national_oil"},
]
