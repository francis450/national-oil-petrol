import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class LeaveRequest(Document):
    def validate(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                frappe.throw("From Date cannot be after To Date.")
            self.total_days = date_diff(self.to_date, self.from_date) + 1
        self._check_overlap()

    def _check_overlap(self):
        if self.status == "Rejected":
            return
        overlap = frappe.db.sql(
            """
            SELECT name FROM `tabLeave Request`
            WHERE employee = %(employee)s
              AND status = 'Approved'
              AND name != %(name)s
              AND from_date <= %(to_date)s
              AND to_date >= %(from_date)s
            """,
            {
                "employee": self.employee,
                "name": self.name or "",
                "from_date": self.from_date,
                "to_date": self.to_date,
            },
        )
        if overlap:
            frappe.throw(
                f"Leave dates overlap with an already-approved request ({overlap[0][0]}) for {self.employee}."
            )
