import { apiClient } from './client'

export interface PettyCashAccountRow {
  name: string
  account_name: string
  balance: number
  department?: string
  last_replenished?: string
}

export interface PettyCashEntryRow {
  name: string
  dated: string
  description: string
  account: string
  department?: string
  amount: number
  approved_by?: string
  payment_method?: string
  docstatus: number
}

const pettyCashAccountFields = [
  'name',
  'account_name',
  'balance',
  'department',
  'last_replenished',
]

const pettyCashEntryFields = [
  'name',
  'dated',
  'description',
  'account',
  'department',
  'amount',
  'approved_by',
  'payment_method',
  'docstatus',
]

export const financeApi = {
  async listPettyCashAccounts() {
    const response = await apiClient.get('/api/resource/Petty Cash Account', {
      params: {
        fields: JSON.stringify(pettyCashAccountFields),
        limit_page_length: 50,
        order_by: 'modified desc',
      },
    })
    return response.data.data as PettyCashAccountRow[]
  },

  async listPettyCashEntries() {
    const response = await apiClient.get('/api/resource/Petty Cash Entry', {
      params: {
        fields: JSON.stringify(pettyCashEntryFields),
        limit_page_length: 50,
        order_by: 'dated desc, modified desc',
      },
    })
    return response.data.data as PettyCashEntryRow[]
  },
}
