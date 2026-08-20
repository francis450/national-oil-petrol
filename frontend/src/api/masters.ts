import { apiClient } from './client'

export interface MasterRecord {
  name: string
  label: string
  doctype: string
  [key: string]: any
}

export interface MasterLookupResult {
  doctype: string
  count: number
  records: MasterRecord[]
}

export const mastersApi = {
  async list(doctype: string, txt = '', limit = 20, company?: string) {
    const response = await apiClient.get('/api/method/national_oil.api.masters.list_master_records', {
      params: { doctype, txt, limit_page_length: limit, company },
    })
    return response.data.message as MasterLookupResult
  },
}
