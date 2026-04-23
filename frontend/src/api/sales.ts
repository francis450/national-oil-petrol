import { apiClient } from './client'

export interface DepartmentSalesTargetRow {
  name: string
  department: string
  period_type: 'Daily' | 'Weekly' | 'Monthly'
  period_start: string
  period_end?: string
  target_amount: number
  hit_amount: number
  deviation: number
  variance_percent?: number
}

const departmentSalesTargetFields = [
  'name',
  'department',
  'period_type',
  'period_start',
  'period_end',
  'target_amount',
  'hit_amount',
  'deviation',
  'variance_percent',
]

export const salesApi = {
  async listDepartmentSalesTargets() {
    const response = await apiClient.get('/api/resource/Department Sales Target', {
      params: {
        fields: JSON.stringify(departmentSalesTargetFields),
        limit_page_length: 50,
        order_by: 'period_start desc, modified desc',
      },
    })
    return response.data.data as DepartmentSalesTargetRow[]
  },
}
