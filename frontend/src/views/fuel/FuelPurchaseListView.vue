<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-white mb-1">Fuel Purchases</h1>
      <p class="text-gray-400">Operational delivery capture with ERPNext purchase bridge actions.</p>
    </div>

    <div v-if="pageError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
      {{ pageError }}
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.5fr)_minmax(340px,1fr)] gap-6">
      <section class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-white">Operational Records</h2>
            <p class="text-sm text-gray-400">Select a fuel purchase to preview ERPNext targets.</p>
          </div>
          <button
            @click="loadFuelPurchases"
            :disabled="loading"
            class="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 transition-colors text-sm"
          >
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loading" class="text-sm text-gray-400 py-8 text-center">Loading fuel purchases...</div>

        <div v-else-if="fuelPurchases.length === 0" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          No fuel purchase records found.
        </div>

        <div v-else class="overflow-x-auto rounded-lg border border-gray-800">
          <table class="w-full text-sm">
            <thead class="bg-gray-950 border-b border-gray-800">
              <tr>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Code</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Supplier</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Fuel</th>
                <th class="px-4 py-3 text-left text-gray-400 font-medium text-xs uppercase tracking-wider">Amount</th>
                <th class="px-4 py-3 text-center text-gray-400 font-medium text-xs uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in fuelPurchases"
                :key="row.name"
                class="border-b border-gray-800 transition-colors"
                :class="selectedPurchase?.name === row.name ? 'bg-gray-800' : 'hover:bg-gray-900'"
              >
                <td class="px-4 py-3 text-gray-200 font-medium">{{ row.code }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatDate(row.dated) }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.supplier }}</td>
                <td class="px-4 py-3 text-gray-300">{{ row.fuel_type }}</td>
                <td class="px-4 py-3 text-gray-300">{{ formatCurrency(row.total_cost) }}</td>
                <td class="px-4 py-3">
                  <div class="flex justify-center gap-2">
                    <button
                      @click="selectPurchase(row)"
                      class="px-3 py-1.5 text-xs rounded bg-blue-900 text-blue-200 hover:bg-blue-800 transition-colors"
                    >
                      Preview
                    </button>
                    <button
                      @click="createTarget(row, 'Purchase Receipt')"
                      :disabled="creatingTargetFor === `${row.name}:Purchase Receipt`"
                      class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
                    >
                      {{ creatingTargetFor === `${row.name}:Purchase Receipt` ? 'Creating...' : 'Create Receipt' }}
                    </button>
                    <button
                      @click="createTarget(row, 'Purchase Invoice')"
                      :disabled="creatingTargetFor === `${row.name}:Purchase Invoice`"
                      class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
                    >
                      {{ creatingTargetFor === `${row.name}:Purchase Invoice` ? 'Creating...' : 'Create Invoice' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-4">
        <div>
          <h2 class="text-xl font-bold text-white">ERPNext Bridge Preview</h2>
          <p class="text-sm text-gray-400">See exactly what draft ERPNext documents will be created.</p>
        </div>

        <div v-if="!selectedPurchase" class="text-sm text-gray-400 py-8 text-center border border-dashed border-gray-800 rounded-lg">
          Select a fuel purchase to preview its ERPNext mappings.
        </div>

        <template v-else>
          <div class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-2">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-xs uppercase tracking-wider text-gray-500">Selected Record</p>
                <p class="text-white font-semibold">{{ selectedPurchase.code }}</p>
              </div>
              <button
                @click="loadPreview(selectedPurchase.name)"
                :disabled="previewLoading"
                class="px-3 py-1.5 text-xs rounded bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors"
              >
                {{ previewLoading ? 'Loading...' : 'Reload Preview' }}
              </button>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p class="text-gray-500">Supplier</p>
                <p class="text-gray-200">{{ selectedPurchase.supplier }}</p>
              </div>
              <div>
                <p class="text-gray-500">Fuel Type</p>
                <p class="text-gray-200">{{ selectedPurchase.fuel_type }}</p>
              </div>
              <div>
                <p class="text-gray-500">Quantity</p>
                <p class="text-gray-200">{{ selectedPurchase.actual_quantity.toLocaleString() }}</p>
              </div>
              <div>
                <p class="text-gray-500">Amount</p>
                <p class="text-gray-200">{{ formatCurrency(selectedPurchase.total_cost) }}</p>
              </div>
            </div>
          </div>

          <div v-if="previewError" class="p-4 rounded-lg border border-red-800 bg-red-900 bg-opacity-20 text-red-200 text-sm">
            {{ previewError }}
          </div>

          <div v-if="previewLoading" class="text-sm text-gray-400 py-8 text-center">Loading mapping preview...</div>

          <div v-else-if="preview?.targets?.length" class="space-y-4">
            <article
              v-for="target in preview.targets"
              :key="target.target_doctype"
              class="rounded-lg border border-gray-800 bg-gray-950 p-4 space-y-3"
            >
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-white">{{ target.target_doctype }}</p>
                  <p class="text-xs text-gray-500">{{ target.recommended ? 'Recommended target' : 'Optional target' }}</p>
                </div>
                <button
                  v-if="target.target_doctype === 'Purchase Receipt' || target.target_doctype === 'Purchase Invoice'"
                  @click="createTarget(selectedPurchase, target.target_doctype as 'Purchase Receipt' | 'Purchase Invoice')"
                  :disabled="creatingTargetFor === `${selectedPurchase.name}:${target.target_doctype}`"
                  class="px-3 py-1.5 text-xs rounded bg-deepseek-blue text-white hover:bg-blue-700 transition-colors"
                >
                  {{ creatingTargetFor === `${selectedPurchase.name}:${target.target_doctype}` ? 'Creating...' : `Create ${target.target_doctype}` }}
                </button>
              </div>

              <div v-if="target.unresolved_dependencies.length" class="p-3 rounded border border-yellow-800 bg-yellow-500 bg-opacity-10">
                <p class="text-xs uppercase tracking-wider text-yellow-400 mb-2">Unresolved Dependencies</p>
                <ul class="space-y-1 text-sm text-yellow-200">
                  <li v-for="issue in target.unresolved_dependencies" :key="issue">{{ issue }}</li>
                </ul>
              </div>

              <pre class="text-xs text-gray-300 bg-black rounded p-3 overflow-x-auto whitespace-pre-wrap">{{ formatPayload(target.payload) }}</pre>
            </article>
          </div>
        </template>

        <div v-if="createdTargets.length" class="pt-2 border-t border-gray-800 space-y-2">
          <p class="text-xs uppercase tracking-wider text-gray-500">Created ERPNext Drafts</p>
          <div
            v-for="target in createdTargets"
            :key="`${target.target_doctype}:${target.name}`"
            class="rounded border border-green-800 bg-green-900 bg-opacity-10 px-3 py-2 text-sm text-green-200"
          >
            {{ target.target_doctype }}: {{ target.name }}
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  operationsBridgeApi,
  type BridgePreview,
  type FuelPurchaseRow,
} from '@/api/operationsBridge'

const fuelPurchases = ref<FuelPurchaseRow[]>([])
const loading = ref(false)
const pageError = ref('')

const selectedPurchase = ref<FuelPurchaseRow | null>(null)
const preview = ref<BridgePreview | null>(null)
const previewLoading = ref(false)
const previewError = ref('')
const creatingTargetFor = ref('')
const createdTargets = ref<Array<{ target_doctype: string; name: string }>>([])

const formatCurrency = (value: number) => `KSh ${Number(value || 0).toLocaleString()}`
const formatDate = (value: string) => new Date(value).toLocaleDateString('en-KE')
const formatPayload = (payload: Record<string, any>) => JSON.stringify(payload, null, 2)

const loadFuelPurchases = async () => {
  loading.value = true
  pageError.value = ''

  try {
    fuelPurchases.value = await operationsBridgeApi.listFuelPurchases()
    if (!selectedPurchase.value && fuelPurchases.value.length > 0) {
      await selectPurchase(fuelPurchases.value[0])
    }
  } catch (error: any) {
    pageError.value = error?.response?.data?.message || error?.message || 'Failed to load fuel purchases.'
  } finally {
    loading.value = false
  }
}

const loadPreview = async (name: string) => {
  previewLoading.value = true
  previewError.value = ''

  try {
    preview.value = await operationsBridgeApi.previewFuelPurchaseMapping(name)
  } catch (error: any) {
    previewError.value = error?.response?.data?.message || error?.message || 'Failed to load ERPNext mapping preview.'
  } finally {
    previewLoading.value = false
  }
}

const selectPurchase = async (row: FuelPurchaseRow) => {
  selectedPurchase.value = row
  await loadPreview(row.name)
}

const createTarget = async (row: FuelPurchaseRow, targetDoctype: 'Purchase Receipt' | 'Purchase Invoice') => {
  const key = `${row.name}:${targetDoctype}`
  creatingTargetFor.value = key
  previewError.value = ''

  try {
    const result = await operationsBridgeApi.createFuelPurchaseTarget(row.name, targetDoctype)
    createdTargets.value = [
      { target_doctype: result.target_doctype, name: result.name },
      ...createdTargets.value.filter((entry) => !(entry.target_doctype === result.target_doctype && entry.name === result.name)),
    ]
    if (selectedPurchase.value?.name === row.name) {
      await loadPreview(row.name)
    }
  } catch (error: any) {
    previewError.value = error?.response?.data?.message || error?.message || `Failed to create ${targetDoctype}.`
  } finally {
    creatingTargetFor.value = ''
  }
}

onMounted(async () => {
  await loadFuelPurchases()
})
</script>
