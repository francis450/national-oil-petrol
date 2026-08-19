import frappe
from frappe import _
from frappe.utils import flt
import requests
import base64
from datetime import datetime


def _get_settings():
	return frappe.get_single("M-Pesa Settings")


def _get_access_token(settings):
	credentials = base64.b64encode(
		f"{settings.consumer_key}:{settings.get_password('consumer_secret')}".encode()
	).decode()
	resp = requests.get(
		f"{settings.api_base_url}/oauth/v1/generate?grant_type=client_credentials",
		headers={"Authorization": f"Basic {credentials}"},
		timeout=10,
	)
	resp.raise_for_status()
	return resp.json().get("access_token")


@frappe.whitelist()
def initiate_stk_push(customer, amount, phone_number, customer_debt=None):
	"""Trigger an M-Pesa STK Push to the customer's phone."""
	frappe.has_permission("M-Pesa Transaction", "create", throw=True)

	settings = _get_settings()
	token = _get_access_token(settings)

	timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
	password_str = f"{settings.business_shortcode}{settings.get_password('passkey')}{timestamp}"
	password = base64.b64encode(password_str.encode()).decode()

	payload = {
		"BusinessShortCode": settings.business_shortcode,
		"Password": password,
		"Timestamp": timestamp,
		"TransactionType": "CustomerPayBillOnline",
		"Amount": int(flt(amount)),
		"PartyA": phone_number,
		"PartyB": settings.business_shortcode,
		"PhoneNumber": phone_number,
		"CallBackURL": settings.callback_url,
		"AccountReference": "National Oil",
		"TransactionDesc": "Debt Payment",
	}

	resp = requests.post(
		f"{settings.api_base_url}/mpesa/stkpush/v1/processrequest",
		json=payload,
		headers={"Authorization": f"Bearer {token}"},
		timeout=15,
	)
	resp.raise_for_status()
	data = resp.json()

	# Record the pending transaction
	txn = frappe.get_doc({
		"doctype": "M-Pesa Transaction",
		"transaction_type": "STK Push",
		"customer": customer,
		"amount": amount,
		"phone_number": phone_number,
		"status": "Pending",
		"checkout_request_id": data.get("CheckoutRequestID"),
		"merchant_request_id": data.get("MerchantRequestID"),
		"customer_debt": customer_debt,
		"raw_response": frappe.as_json(data),
	})
	txn.insert(ignore_permissions=True)
	return {"transaction": txn.name, "checkout_request_id": data.get("CheckoutRequestID")}


@frappe.whitelist(allow_guest=True)
def mpesa_callback(**kwargs):
	"""
	Webhook called by Safaricom when an STK Push transaction completes.
	IP restriction should be enforced at the nginx/firewall level — as of this
	writing that restriction is NOT present in this bench's nginx config, so the
	in-app payload validation below is the only real defense until it is added.
	"""
	body = frappe.request.get_json(force=True) or {}

	stk_callback = body.get("Body", {}).get("stkCallback")
	if not isinstance(stk_callback, dict):
		frappe.throw(_("Malformed M-Pesa callback payload."), frappe.ValidationError)

	checkout_id = stk_callback.get("CheckoutRequestID")
	result_code = stk_callback.get("ResultCode")
	if not checkout_id or not isinstance(checkout_id, str):
		frappe.throw(_("M-Pesa callback missing CheckoutRequestID."), frappe.ValidationError)
	if not isinstance(result_code, int):
		frappe.throw(_("M-Pesa callback missing or invalid ResultCode."), frappe.ValidationError)

	txn_name = frappe.db.get_value(
		"M-Pesa Transaction", {"checkout_request_id": checkout_id}, "name"
	)
	if not txn_name:
		return {"ResultCode": 0, "ResultDesc": "Accepted"}

	txn = frappe.get_doc("M-Pesa Transaction", txn_name)
	if txn.status != "Pending":
		# Already resolved — ignore replayed/duplicate callbacks instead of overwriting a final state.
		return {"ResultCode": 0, "ResultDesc": "Accepted"}

	if result_code == 0:
		# Success — extract metadata
		items = {
			item["Name"]: item.get("Value")
			for item in stk_callback.get("CallbackMetadata", {}).get("Item", [])
		}
		txn.status = "Confirmed"
		txn.mpesa_receipt_number = items.get("MpesaReceiptNumber")
		txn.result_description = stk_callback.get("ResultDesc")
	else:
		txn.status = "Failed"
		txn.result_description = stk_callback.get("ResultDesc")

	txn.raw_response = frappe.as_json(body)
	txn.save(ignore_permissions=True)
	return {"ResultCode": 0, "ResultDesc": "Accepted"}


@frappe.whitelist()
def check_transaction_status(transaction_name):
	"""Return current status of an M-Pesa Transaction."""
	return frappe.db.get_value(
		"M-Pesa Transaction",
		transaction_name,
		["status", "mpesa_receipt_number", "result_description"],
		as_dict=True,
	)
