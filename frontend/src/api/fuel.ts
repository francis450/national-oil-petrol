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
  shift: string
  nozzle_no: number
  pump_number: string
  pump_no: string
  fuel_type: string
  opening_reading: number
  closing_reading: number
  variance: number
  unit_price?: number
  expected_sales_amount?: number
  attendant?: string
  department?: string
}

export interface PumpReadingSummary {
  count: number
  rows: PumpReadingRow[]
  today: {
    reading_count: number
    throughput: number
    expected_sales: number
  }
}

export interface NozzleDefaults {
  nozzle_no: number
  pump_no: string
  fuel_type: string
  item: string
}

export interface FuelPurchaseSubmitResult {
  name: string
  docstatus: number
  purchase_receipt?: string
}

export interface AssignedPumpRow {
  pump_number: string
  nozzle_no: number
  fuel_type: string
  status: 'Pending' | 'Opened' | 'Closed'
}

export interface ShiftAssignmentDoc {
  name: string
  employee: string
  employee_name?: string
  shift_type: string
  start_date: string
  end_date?: string
  reconciliation_status: 'Open' | 'Closed' | 'Verified'
  total_expected_sales?: number
  closed_at?: string
  assigned_pumps?: AssignedPumpRow[]
}

export interface OpenPumpReadingRow {
  name: string
  nozzle_no: number
  pump_number: string
  fuel_type: string
  opening_reading: number
  dated: string
}

export interface MyShiftContext {
  employee: string | null
  shift: ShiftAssignmentDoc | null
  open_readings: OpenPumpReadingRow[]
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

  async getNozzleDefaults(nozzleNo: number) {
    const response = await apiClient.get('/api/method/national_oil.api.fuel.get_nozzle_defaults', {
      params: { nozzle_no: nozzleNo },
    })
    return response.data.message as NozzleDefaults | null
  },

  async submitFuelPurchase(name: string) {
    const response = await apiClient.post('/api/method/national_oil.api.fuel.submit_fuel_purchase', {
      name,
    })
    return response.data.message as FuelPurchaseSubmitResult
  },

  async getMyShiftContext() {
    const response = await apiClient.get('/api/method/national_oil.api.fuel.get_my_shift_context')
    return response.data.message as MyShiftContext
  },

  async openPumpReading(shift: string, nozzleNo: number, openingReading: number, unitPrice?: number) {
    const response = await apiClient.post('/api/method/national_oil.api.fuel.open_pump_reading', {
      shift,
      nozzle_no: nozzleNo,
      opening_reading: openingReading,
      unit_price: unitPrice || undefined,
    })
    return response.data.message
  },

  async closePumpReading(name: string, closingReading: number, unitPrice?: number) {
    const response = await apiClient.post('/api/method/national_oil.api.fuel.close_pump_reading', {
      name,
      closing_reading: closingReading,
      unit_price: unitPrice || undefined,
    })
    return response.data.message
  },
}
