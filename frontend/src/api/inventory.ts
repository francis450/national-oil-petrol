import { apiClient } from './client'

export interface ProductRow {
  name: string
  product_name: string
  is_fuel: number
  fuel_type?: string
  brand?: string
  unit_of_measure: string
  quantity: number
  buying_price?: number
  selling_price?: number
  selling_price_wholesale?: number
}

const productFields = [
  'name',
  'product_name',
  'is_fuel',
  'fuel_type',
  'brand',
  'unit_of_measure',
  'quantity',
  'buying_price',
  'selling_price',
  'selling_price_wholesale',
]

export const inventoryApi = {
  async listProducts() {
    const response = await apiClient.get('/api/resource/Product', {
      params: {
        fields: JSON.stringify(productFields),
        limit_page_length: 100,
        order_by: 'modified desc',
      },
    })
    return response.data.data as ProductRow[]
  },
}
