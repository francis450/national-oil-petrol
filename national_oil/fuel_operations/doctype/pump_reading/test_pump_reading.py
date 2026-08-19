import frappe
from frappe.tests.utils import FrappeTestCase


class TestPumpReading(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def _create_shift_assignment(self):
		employee = frappe.db.sql(
			"""
			SELECT e.name FROM `tabEmployee` e
			WHERE e.name NOT IN (
				SELECT DISTINCT sa.employee FROM `tabShift Assignment` sa WHERE sa.docstatus < 2
			)
			LIMIT 1
			"""
		)
		employee = employee[0][0] if employee else frappe.db.get_value("Employee", {}, "name")
		shift_type = frappe.db.get_value("Shift Type", {}, "name")
		company = frappe.db.get_value("Company", {}, "name")
		doc = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee,
				"shift_type": shift_type,
				"company": company,
				"start_date": frappe.utils.today(),
				"end_date": frappe.utils.today(),
			}
		).insert(ignore_permissions=True)
		return doc.name

	def _ensure_fuel_type(self, name, item):
		if frappe.db.exists("Fuel Type", name):
			doc = frappe.get_doc("Fuel Type", name)
			if doc.item != item:
				doc.item = item
				doc.save(ignore_permissions=True)
			return name

		frappe.get_doc(
			{
				"doctype": "Fuel Type",
				"fuel_type_name": name,
				"unit_of_measure": "Litres",
				"item": item,
			}
		).insert(ignore_permissions=True)
		return name

	def test_nozzle_defaults_pump_and_fuel_type(self):
		self._ensure_fuel_type("Test Diesel Nozzle", "DIESEL")
		shift = self._create_shift_assignment()

		doc = frappe.get_doc(
			{
				"doctype": "Pump Reading",
				"dated": frappe.utils.today(),
				"shift": shift,
				"nozzle_no": 2,
				"opening_reading": 500,
				"closing_reading": 620,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(doc.pump_no, "1")
		self.assertEqual(doc.variance, 120)

	def test_rejects_fuel_type_mismatch_for_nozzle(self):
		self._ensure_fuel_type("Test Petrol Nozzle", "PETROL")
		shift = self._create_shift_assignment()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Pump Reading",
					"dated": frappe.utils.today(),
					"shift": shift,
					"nozzle_no": 2,  # nozzle 2 is Diesel
					"fuel_type": "Test Petrol Nozzle",
					"opening_reading": 100,
					"closing_reading": 150,
				}
			).insert(ignore_permissions=True)

	def test_blocks_duplicate_reading_for_same_nozzle_date_shift(self):
		self._ensure_fuel_type("Test Petrol Dup", "PETROL")
		shift = self._create_shift_assignment()

		frappe.get_doc(
			{
				"doctype": "Pump Reading",
				"dated": frappe.utils.today(),
				"shift": shift,
				"nozzle_no": 1,
				"opening_reading": 100,
				"closing_reading": 150,
			}
		).insert(ignore_permissions=True)

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Pump Reading",
					"dated": frappe.utils.today(),
					"shift": shift,
					"nozzle_no": 1,
					"opening_reading": 150,
					"closing_reading": 200,
				}
			).insert(ignore_permissions=True)

	def test_meter_rollover_calculates_variance(self):
		self._ensure_fuel_type("Test Paraffin Rollover", "PARAFFIN")
		shift = self._create_shift_assignment()

		doc = frappe.get_doc(
			{
				"doctype": "Pump Reading",
				"dated": frappe.utils.today(),
				"shift": shift,
				"nozzle_no": 13,
				"opening_reading": 9980,
				"closing_reading": 50,
				"meter_rollover": 1,
				"meter_rollover_limit": 10000,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(doc.variance, 70)

	def test_shift_closes_out_only_once_all_assigned_pumps_are_closed(self):
		fuel_type = self._ensure_fuel_type("Test Close-Out Petrol", "PETROL")

		employee = frappe.db.sql(
			"""
			SELECT e.name FROM `tabEmployee` e
			WHERE e.name NOT IN (
				SELECT DISTINCT sa.employee FROM `tabShift Assignment` sa WHERE sa.docstatus < 2
			)
			LIMIT 1
			"""
		)
		employee = employee[0][0] if employee else frappe.db.get_value("Employee", {}, "name")
		shift_type = frappe.db.get_value("Shift Type", {}, "name")
		company = frappe.db.get_value("Company", {}, "name")

		nozzles = [1, 5, 9]  # three different pumps, all petrol
		shift_doc = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee,
				"shift_type": shift_type,
				"company": company,
				"start_date": frappe.utils.today(),
				"end_date": frappe.utils.today(),
				"assigned_pumps": [
					{"pump_number": f"P{n}", "nozzle_no": n, "fuel_type": fuel_type} for n in nozzles
				],
			}
		).insert(ignore_permissions=True)

		readings = []
		for nozzle_no in nozzles:
			readings.append(
				frappe.get_doc(
					{
						"doctype": "Pump Reading",
						"dated": frappe.utils.today(),
						"shift": shift_doc.name,
						"nozzle_no": nozzle_no,
						"opening_reading": 100,
					}
				).insert(ignore_permissions=True)
			)

		# Close 2 of the 3 pumps — shift should stay Open with no total computed.
		for reading in readings[:2]:
			reading.closing_reading = 150
			reading.unit_price = 10
			reading.save(ignore_permissions=True)
			reading.submit()

		shift_doc.reload()
		self.assertEqual(shift_doc.reconciliation_status, "Open")
		self.assertFalse(shift_doc.total_expected_sales)

		# Close the last pump — shift should flip to Closed with the summed total.
		last = readings[2]
		last.closing_reading = 150
		last.unit_price = 10
		last.save(ignore_permissions=True)
		last.submit()

		shift_doc.reload()
		self.assertEqual(shift_doc.reconciliation_status, "Closed")
		self.assertEqual(shift_doc.total_expected_sales, 1500)  # 3 readings x 50L x 10
		self.assertTrue(shift_doc.closed_at)
		self.assertTrue(
			all(row.status == "Closed" for row in shift_doc.assigned_pumps)
		)
