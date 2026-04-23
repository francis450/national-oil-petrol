import { apiClient } from './client'

export interface FuelPurchaseRow {
  name: string
  code: string
  dated: string
  supplier: string
  fuel_type: string
  actual_quantity: number
  unit_cost: number
  total_cost: number
  amount_paid: number
  balance: number
  payment_method?: string
  docstatus: number
}

export interface SalesEntryRow {
  name: string
  dated: string
  department: string
  sale_type: string
  amount: number
  payment_method?: string
  customer?: string
  docstatus: number
}

export interface InventoryReceiptRow {
  name: string
  code: string
  dated: string
  supplier: string
  product?: string
  brand?: string
  units: number
  unit_cost: number
  total_cost: number
  amount_paid: number
  balance: number
  payment_method?: string
  docstatus: number
}

export interface BridgeTarget {
  target_doctype: string
  recommended: boolean
  payload: Record<string, any>
  unresolved_dependencies: string[]
}

export interface BridgePreview {
  source_doctype: string
  source_name?: string
  targets: BridgeTarget[]
}

const fuelPurchaseFields = [
  'name',
  'code',
  'dated',
  'supplier',
  'fuel_type',
  'actual_quantity',
  'unit_cost',
  'total_cost',
  'amount_paid',
  'balance',
  'payment_method',
  'docstatus',
]

const salesEntryFields = [
  'name',
  'dated',
  'department',
  'sale_type',
  'amount',
  'payment_method',
  'customer',
  'docstatus',
]

const inventoryReceiptFields = [
  'name',
  'code',
  'dated',
  'supplier',
  'product',
  'brand',
  'units',
  'unit_cost',
  'total_cost',
  'amount_paid',
  'balance',
  'payment_method',
  'docstatus',
]

export const operationsBridgeApi = {
  async listFuelPurchases() {
    const response = await apiClient.get('/api/resource/Fuel Purchase', {
      params: {
        fields: JSON.stringify(fuelPurchaseFields),
        limit_page_length: 50,
        order_by: 'dated desc',
      },
    })
    return response.data.data as FuelPurchaseRow[]
  },

  async previewFuelPurchaseMapping(name: string) {
    const response = await apiClient.get('/api/method/national_oil.api.operations_bridge.preview_erpnext_mapping', {
      params: {
        source_doctype: 'Fuel Purchase',
        docname: name,
      },
    })
    return response.data.message as BridgePreview
  },

  async createFuelPurchaseTarget(name: string, targetDoctype: 'Purchase Receipt' | 'Purchase Invoice') {
    const response = await apiClient.post('/api/method/national_oil.api.operations_bridge.create_erpnext_target_from_operational', {
      source_doctype: 'Fuel Purchase',
      target_doctype: targetDoctype,
      docname: name,
    })
    return response.data.message as { target_doctype: string; name: string; docstatus: number }
  },

  async listSalesEntries() {
    const response = await apiClient.get('/api/resource/Sales Entry', {
      params: {
        fields: JSON.stringify(salesEntryFields),
        limit_page_length: 50,
        order_by: 'dated desc',
      },
    })
    return response.data.data as SalesEntryRow[]
  },

  async previewSalesEntryMapping(name: string) {
    const response = await apiClient.get('/api/method/national_oil.api.operations_bridge.preview_erpnext_mapping', {
      params: {
        source_doctype: 'Sales Entry',
        docname: name,
      },
    })
    return response.data.message as BridgePreview
  },

  async createSalesEntryTarget(name: string, targetDoctype: 'Sales Invoice') {
    const response = await apiClient.post('/api/method/national_oil.api.operations_bridge.create_erpnext_target_from_operational', {
      source_doctype: 'Sales Entry',
      target_doctype: targetDoctype,
      docname: name,
    })
    return response.data.message as { target_doctype: string; name: string; docstatus: number }
  },

  async listInventoryReceipts() {
    const response = await apiClient.get('/api/resource/Inventory Receipt', {
      params: {
        fields: JSON.stringify(inventoryReceiptFields),
        limit_page_length: 50,
        order_by: 'dated desc',
      },
    })
    return response.data.data as InventoryReceiptRow[]
  },

  async previewInventoryReceiptMapping(name: string) {
    const response = await apiClient.get('/api/method/national_oil.api.operations_bridge.preview_erpnext_mapping', {
      params: {
        source_doctype: 'Inventory Receipt',
        docname: name,
      },
    })
    return response.data.message as BridgePreview
  },

  async createInventoryReceiptTarget(name: string, targetDoctype: 'Purchase Receipt' | 'Purchase Invoice') {
    const response = await apiClient.post('/api/method/national_oil.api.operations_bridge.create_erpnext_target_from_operational', {
      source_doctype: 'Inventory Receipt',
      target_doctype: targetDoctype,
      docname: name,
    })
    return response.data.message as { target_doctype: string; name: string; docstatus: number }
  },
}
