import { apiClient } from './client'

export interface CommerceInvoiceRow {
  name: string
  posting_date: string
  company?: string
  status?: string
  grand_total?: number
  outstanding_amount?: number
  customer?: string
  customer_name?: string
  supplier?: string
  supplier_name?: string
  docstatus?: number
  is_pos?: number
  doctype: 'Sales Invoice' | 'Purchase Invoice'
  label?: string
}

export interface PaymentEntryRow {
  name: string
  docstatus?: number
  payment_type: 'Pay' | 'Receive'
  party_type?: 'Customer' | 'Supplier'
  party?: string
  party_name?: string
  posting_date: string
  company?: string
  paid_amount?: number
  received_amount?: number
  mode_of_payment?: string
  status?: string
  doctype: 'Payment Entry'
  label?: string
}

export interface PaymentEntryResult {
  target_doctype: 'Payment Entry'
  name: string
  docstatus: number
  reference_doctype: 'Sales Invoice' | 'Purchase Invoice'
  reference_name: string
}

interface ListCommerceResponse {
  doctype: string
  count: number
  records: Array<CommerceInvoiceRow | PaymentEntryRow>
}

const listCommerceRecords = async (
  doctype: 'Sales Invoice' | 'Purchase Invoice' | 'Payment Entry',
  params: Record<string, any> = {},
) => {
  const response = await apiClient.get('/api/method/national_oil.api.commerce.list_commerce_records', {
    params: {
      doctype,
      limit_page_length: 50,
      ...params,
    },
  })

  return (response.data.message as ListCommerceResponse).records
}

export const commerceApi = {
  async listReceivableInvoices() {
    return (await listCommerceRecords('Sales Invoice')) as CommerceInvoiceRow[]
  },

  async listPayableInvoices() {
    return (await listCommerceRecords('Purchase Invoice')) as CommerceInvoiceRow[]
  },

  async listReceivablePayments() {
    return (await listCommerceRecords('Payment Entry', {
      payment_type: 'Receive',
      party_type: 'Customer',
    })) as PaymentEntryRow[]
  },

  async listPayablePayments() {
    return (await listCommerceRecords('Payment Entry', {
      payment_type: 'Pay',
      party_type: 'Supplier',
    })) as PaymentEntryRow[]
  },

  async createPaymentEntry(
    referenceDoctype: 'Sales Invoice' | 'Purchase Invoice',
    referenceName: string,
    modeOfPayment = 'Cash',
  ) {
    const response = await apiClient.post(
      '/api/method/national_oil.api.operations_bridge.create_payment_entry_for_reference',
      {
        reference_doctype: referenceDoctype,
        reference_name: referenceName,
        mode_of_payment: modeOfPayment,
      },
    )

    return response.data.message as PaymentEntryResult
  },
}
