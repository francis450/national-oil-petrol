import { apiClient } from './client'

export const dashboardApi = {
  async getMetrics() {
    const response = await apiClient.get('/api/method/national_oil.api.dashboard.get_dashboard_metrics')
    return response.data.message
  },

  async getSalesTrend(days: number = 7) {
    const response = await apiClient.get('/api/method/national_oil.api.dashboard.get_sales_trend', {
      params: { days },
    })
    return response.data.message
  },

  async getPerformance() {
    const response = await apiClient.get('/api/resource/Performance Review', {
      params: {
        fields: ['name', 'employee', 'rating', 'creation'],
        limit_page_length: 10,
        filters: [['docstatus', '=', 1]],
      },
    })
    return response.data.data
  },
}
