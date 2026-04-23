import { apiClient } from './client'

export interface DashboardChartRow {
  label: string
  value: number
  color?: string
}

export interface DashboardMetrics {
  today_sales: number
  month_sales: number
  outstanding_receivables: number
  outstanding_payables: number
  stock_balance_qty: number
  operational_backlog: number
  sales_trend: DashboardChartRow[]
  stock_levels: DashboardChartRow[]
  attendance: DashboardChartRow[]
  pipeline: DashboardChartRow[]
  settlement: {
    receipts_this_month: number
    payments_this_month: number
  }
}

export const dashboardApi = {
  async getMetrics() {
    const response = await apiClient.get('/api/method/national_oil.api.dashboard.get_dashboard_metrics')
    return response.data.message as DashboardMetrics
  },
}
