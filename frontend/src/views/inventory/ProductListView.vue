<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Products</h1>
      <p class="text-gray-400">Operational product catalog with stock and pricing visibility.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Products</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(products.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Fuel Products</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(fuelProducts.length) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Total Stock</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatNumber(totalQuantity) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Highest Retail Price</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(highestRetailPrice) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Product Register</h2>
            <p class="text-sm text-gray-400">Current product stock and selling prices from the operational inventory catalog.</p>
          </div>
          <button
            @click="loadProducts"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading products...</div>

        <div v-else-if="products.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No products found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Product</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Stock</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Buying</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Retail</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Wholesale</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="product in products"
                :key="product.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedProduct?.name === product.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedProduct = product"
              >
                <td class="px-4 py-3">
                  <div class="text-gray-100 font-medium">{{ product.product_name }}</div>
                  <div class="text-xs text-gray-500">{{ product.brand || 'No brand' }}</div>
                </td>
                <td class="px-4 py-3 text-gray-300">{{ product.is_fuel ? (product.fuel_type || 'Fuel') : 'Non-fuel' }}</td>
                <td class="px-4 py-3 text-white">{{ formatNumber(product.quantity) }} {{ product.unit_of_measure }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(product.buying_price) }}</td>
                <td class="px-4 py-3 text-green-300">{{ formatCurrency(product.selling_price) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(product.selling_price_wholesale) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Product Detail</h2>
          <p class="text-sm text-gray-400">Review one product at a time across stock, pricing, and fuel classification.</p>
        </div>

        <div v-if="!selectedProduct" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select a product to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Product</p>
              <p class="text-lg font-semibold text-white">{{ selectedProduct.product_name }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Type</p>
                <p class="text-gray-200">{{ selectedProduct.is_fuel ? 'Fuel' : 'Non-fuel' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Fuel Type</p>
                <p class="text-gray-200">{{ selectedProduct.fuel_type || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Brand</p>
                <p class="text-gray-200">{{ selectedProduct.brand || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Unit</p>
                <p class="text-gray-200">{{ selectedProduct.unit_of_measure }}</p>
              </div>
              <div>
                <p class="text-gray-500">Stock</p>
                <p class="text-white">{{ formatNumber(selectedProduct.quantity) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Buying Price</p>
                <p class="text-gray-200">{{ formatCurrency(selectedProduct.buying_price) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Retail Price</p>
                <p class="text-green-300">{{ formatCurrency(selectedProduct.selling_price) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Wholesale Price</p>
                <p class="text-gray-200">{{ formatCurrency(selectedProduct.selling_price_wholesale) }}</p>
              </div>
            </div>
          </div>
        </template>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { inventoryApi, type ProductRow } from '@/api/inventory'

const products = ref<ProductRow[]>([])
const selectedProduct = ref<ProductRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const fuelProducts = computed(() => products.value.filter((product) => Boolean(product.is_fuel)))
const totalQuantity = computed(() => products.value.reduce((sum, product) => sum + Number(product.quantity || 0), 0))
const highestRetailPrice = computed(() => products.value.reduce((max, product) => Math.max(max, Number(product.selling_price || 0)), 0))

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const loadProducts = async () => {
  loading.value = true
  pageError.value = ''

  try {
    products.value = await inventoryApi.listProducts()
    if (!selectedProduct.value && products.value.length > 0) {
      selectedProduct.value = products.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load products.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadProducts()
})
</script>
