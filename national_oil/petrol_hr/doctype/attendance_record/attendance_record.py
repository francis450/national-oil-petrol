import frappe
from frappe.model.document import Document


class AttendanceRecord(Document):
    def validate(self):
        self._check_duplicate()

    def _check_duplicate(self):
        existing = frappe.db.get_value(
            "Attendance Record",
            {"employee": self.employee, "dated": self.dated, "name": ("!=", self.name)},
            "name",
        )
        if existing:
            frappe.throw(
                f"Attendance for {self.employee} on {self.dated} already recorded as {existing}."
            )
