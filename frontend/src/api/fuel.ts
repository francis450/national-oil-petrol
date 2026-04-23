import { apiClient } from './client'

export interface FuelPriceRow {
  name: string
  fuel_type: string
  effective_date: string
  buying_price: number
  selling_price_retail: number
  selling_price_wholesale?: number
  set_by?: string
}

export interface FuelStockRow {
  name: string
  product_name: string
  quantity: number
  unit_of_measure?: string
}

export interface PumpReadingRow {
  name: string
  dated: string
  pump_number: string
  fuel_type: string
  opening_reading: number
  closing_reading: number
  variance: number
  attendant?: string
  department?: string
}

export interface PumpReadingSummary {
  count: number
  rows: PumpReadingRow[]
  today: {
    reading_count: number
    throughput: number
  }
}

export const fuelApi = {
  async getCurrentPrices() {
    const response = await apiClient.get('/api/method/national_oil.api.fuel.get_current_prices')
    return response.data.message as FuelPriceRow[]
  },

  async getFuelStock() {
    const response = await apiClient.get('/api/method/national_oil.api.fuel.get_fuel_stock')
    return response.data.message as FuelStockRow[]
  },

  async getRecentPumpReadings(limit = 20) {
    const response = await apiClient.get('/api/method/national_oil.api.fuel.get_recent_pump_readings', {
      params: {
        limit_page_length: limit,
      },
    })
    return response.data.message as PumpReadingSummary
  },
}
