<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Fuel Prices</h1>
      <p class="text-gray-400">Latest pump-side pricing and operational fuel stock from National Oil forecourt records.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Active Fuel Prices</p>
        <p class="text-3xl font-bold text-white mt-2">{{ prices.length }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Highest Retail Price</p>
        <p class="text-3xl font-bold text-white mt-2">{{ formatCurrency(highestRetailPrice) }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-sm text-gray-400">Fuel Stock Snapshot</p>
        <p class="text-3xl font-bold text-white mt-2">{{ totalStockQuantity }}</p>
        <p class="text-xs text-gray-500 mt-1">Total quantity across operational fuel products</p>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Latest Price Matrix</h2>
            <p class="text-sm text-gray-400">One active price row per fuel type based on the most recent effective date.</p>
          </div>
          <button
            @click="loadView"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div
          v-if="loading"
          class="text-sm text-gray-400 py-8 text-center"
        >
          Loading fuel prices...
        </div>

        <div
          v-else-if="prices.length === 0"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          No fuel price records found yet.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Fuel Type</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Effective</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Buying</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Retail</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Wholesale</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Margin</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="price in prices"
                :key="price.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedPrice?.name === price.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
                @click="selectedPrice = price"
              >
                <td class="px-4 py-3 text-gray-100 font-medium">{{ price.fuel_type }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(price.effective_date) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(price.buying_price) }}</td>
                <td class="px-4 py-3 text-green-300 font-medium">{{ formatCurrency(price.selling_price_retail) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(price.selling_price_wholesale) }}</td>
                <td class="px-4 py-3 text-blue-300">{{ formatCurrency(price.selling_price_retail - price.buying_price) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">Price Detail</h2>
          <p class="text-sm text-gray-400">Pair the latest pricing with operational stock so forecourt teams can sanity-check changes quickly.</p>
        </div>

        <div
          v-if="!selectedPrice"
          class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg"
        >
          Select a price row to inspect it.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-4">
            <div>
              <p class="text-xs uppercase tracking-wider text-gray-500">Selected Fuel Type</p>
              <p class="text-lg font-semibold text-white">{{ selectedPrice.fuel_type }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Effective Date</p>
                <p class="text-gray-200">{{ formatDate(selectedPrice.effective_date) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Set By</p>
                <p class="text-gray-200">{{ selectedPrice.set_by || '—' }}</p>
              </div>
              <div>
                <p class="text-gray-500">Buying Price</p>
                <p class="text-gray-200">{{ formatCurrency(selectedPrice.buying_price) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Retail Price</p>
                <p class="text-green-300">{{ formatCurrency(selectedPrice.selling_price_retail) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Wholesale Price</p>
                <p class="text-gray-200">{{ formatCurrency(selectedPrice.selling_price_wholesale) }}</p>
              </div>
              <div>
                <p class="text-gray-500">Retail Margin</p>
                <p class="text-blue-300">{{ formatCurrency(selectedPrice.selling_price_retail - selectedPrice.buying_price) }}</p>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-3">
            <div class="flex items-center justify-between">
              <p class="text-sm font-semibold text-white">Fuel Stock Snapshot</p>
              <span class="text-xs text-gray-500">{{ stock.length }} products</span>
            </div>

            <div
              v-if="stock.length === 0"
              class="text-sm text-gray-400 py-4 text-center border border-dashed border-gray-800 rounded-lg"
            >
              No fuel stock products found yet.
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="row in stock"
                :key="row.name"
                class="flex items-center justify-between rounded border border-gray-800 px-3 py-2"
              >
                <div>
                  <p class="text-sm text-gray-200">{{ row.product_name }}</p>
                  <p class="text-xs text-gray-500">{{ row.unit_of_measure || 'Units' }}</p>
                </div>
                <p class="text-sm font-medium text-white">{{ formatNumber(row.quantity) }}</p>
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
import { fuelApi, type FuelPriceRow, type FuelStockRow } from '@/api/fuel'

const prices = ref<FuelPriceRow[]>([])
const stock = ref<FuelStockRow[]>([])
const selectedPrice = ref<FuelPriceRow | null>(null)
const loading = ref(false)
const pageError = ref('')

const highestRetailPrice = computed(() =>
  prices.value.reduce((max, row) => Math.max(max, Number(row.selling_price_retail || 0)), 0),
)

const totalStockQuantity = computed(() =>
  `${formatNumber(stock.value.reduce((sum, row) => sum + Number(row.quantity || 0), 0))} L`,
)

const formatCurrency = (value?: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value?: string) => (value ? new Date(value).toLocaleDateString('en-KE') : '—')
const formatNumber = (value?: number) => Number(value || 0).toLocaleString()

const loadView = async () => {
  loading.value = true
  pageError.value = ''

  try {
    const [priceRows, stockRows] = await Promise.all([
      fuelApi.getCurrentPrices(),
      fuelApi.getFuelStock(),
    ])
    prices.value = priceRows
    stock.value = stockRows
    if (!selectedPrice.value && prices.value.length > 0) {
      selectedPrice.value = prices.value[0]
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load fuel pricing data.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadView()
})
</script>
