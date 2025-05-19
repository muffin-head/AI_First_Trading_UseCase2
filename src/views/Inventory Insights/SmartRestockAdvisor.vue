  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { fetchOliveForecastData } from '@/data/oliveForecasting.js'
  import BaseCard from '@/components/Base/BaseCard.vue'
  import Breadcrumbs from '@/components/Breadcrumbs.vue'
  import ChartBlock from '@/components/ChartBlock.vue'

  // Core states
  const loading = ref(true)
  const data = ref({})
  const currentQuarterAlerts = ref([])
  const futureQuarterAlerts = ref([])

  // Dropdown filters
  const allProducts = ref([])
  const allCounties = ref([])
  const allQuarters = ['2025Q1', '2025Q2', '2025Q3']
  const selectedProduct = ref('')
  const selectedCounty = ref('')
  const selectedQuarter = ref('2025Q2')
  const filteredStock = ref([])
  const supplierScorecard = ref([])

const selectedPerfRegion = ref('')
const selectedPerfSupplier = ref('')
const availableRegions = computed(() => {
  const set = new Set((supplierScorecard.value || []).map(entry => entry['County Retailer']))
  return Array.from(set)
})
const filteredSupplierOptions = computed(() => {
  if (!selectedPerfRegion.value) return []
  return (supplierScorecard.value || [])
    .filter(entry => entry['County Retailer'] === selectedPerfRegion.value)
    .map(entry => entry['Retailer Supplier Name'])
})

const supplierPerformanceTable = computed(() => {
  return supplierScorecard.value || []
})
const filteredSupplierPerformanceTable = computed(() => {
  if (!selectedPerfRegion.value || !selectedPerfSupplier.value) return []

  return supplierPerformanceTable.value.filter(entry =>
    entry['Retailer Supplier Name'] === selectedPerfSupplier.value &&
    (entry['County Retailer'] === selectedPerfRegion.value || entry['Region'] === selectedPerfRegion.value)
  )
})


const updateSupplierOptions = () => {
  selectedPerfSupplier.value = ''
}


  const CURRENT_QUARTER = '2025Q2'

  // === Restock Alert Logic ===
  const extractRestockAlerts = () => {
    const current = []
    const future = []

    for (const [product, regions] of Object.entries(data.value.products)) {
      regions.forEach(region => {
        region.suppliers.forEach(supplier => {
          supplier.quarters.forEach((quarter, index) => {
            const forecast = supplier.forecasted[index]
            const inventory = Math.max(supplier.inventory[index], 0)
            const unitsSold = supplier.unitsSold[index]

            const isCurrent = quarter === CURRENT_QUARTER
            const isFuture = quarter > CURRENT_QUARTER
            const shouldRestock = forecast > inventory

            if (shouldRestock && isCurrent) {
              current.push({
                product,
                county: region.county,
                supplier: supplier.supplier,
                quarter,
                forecast,
                inventory,
                reorderQty: forecast - inventory,
                sold: unitsSold
              })
            }
            if (shouldRestock && isFuture) {
              future.push({
                product,
                county: region.county,
                supplier: supplier.supplier,
                quarter,
                forecast,
                inventory,
                reorderQty: forecast - inventory,
                sold: unitsSold
              })
            }
          })
        })
      })
    }

    currentQuarterAlerts.value = current
    futureQuarterAlerts.value = future
  }

  // === Filter Inventory Data Based on Selections ===
  const updateFilteredStock = () => {
    const stock = []

    for (const [product, regions] of Object.entries(data.value.products)) {
      if (selectedProduct.value && product !== selectedProduct.value) continue

      regions.forEach(region => {
        if (selectedCounty.value && region.county !== selectedCounty.value) return

        region.suppliers.forEach(supplier => {
          supplier.quarters.forEach((quarter, index) => {
            if (quarter !== selectedQuarter.value) return

            stock.push({
              product,
              county: region.county,
              supplier: supplier.supplier,
              quarter,
              forecast: supplier.forecasted[index],
              inventory: Math.max(supplier.inventory[index], 0),
              unitsSold: selectedQuarter.value === '2025Q3' ? null : supplier.unitsSold[index]
            })
          })
        })
      })
    }

    filteredStock.value = stock
  }

  // === Supplier Performance Chart ===
  const supplierPerformanceChart = computed(() => {
    const scorecard = data.value.supplier_scorecard || []
    if (!scorecard.length) return null

    return {
      chartOptions: {
        chart: { type: 'bar', height: 300 },
        xaxis: { categories: scorecard.map(s => s['Retailer Supplier Name']) },
        dataLabels: { enabled: true },
        tooltip: { shared: true }
      },
      series: [
        {
          name: 'Fulfillment Rate',
          data: scorecard.map(s => +(s.avg_fulfillment_rate * 100).toFixed(1))
        },
        {
          name: 'Forecast Deviation',
          data: scorecard.map(s => +(s.avg_forecast_deviation).toFixed(1))
        }
      ]
    }
  })

  // === Load Data on Mount ===
  onMounted(async () => {
  const result = await fetchOliveForecastData();

  if (!result || !result.products) {
    console.error("🚨 'products' key missing in API response");
    return;
  }

  data.value = result;


    extractRestockAlerts()
    updateFilteredStock()

    allProducts.value = Object.keys(data.value.products)
    const countiesSet = new Set()
    for (const regions of Object.values(data.value.products)) {
      regions.forEach(region => countiesSet.add(region.county))
    }
    allCounties.value = Array.from(countiesSet)

    if (data.value.supplier_scorecard) {
      supplierScorecard.value = data.value.supplier_scorecard
    }

    loading.value = false
  })
  </script>


  <template>
    <div class="container mx-auto">
      <Breadcrumbs parentTitle="Inventory Insights" subParentTitle="Smart Restock Advisor" />

      <div v-if="loading" class="text-center py-10 text-gray-500">
        Loading restock recommendations...
      </div>

      <div v-else class="grid grid-cols-12 gap-6">
        <!-- KPI Cards -->
        <div class="col-span-12 sm:col-span-6 xl:col-span-3" v-for="(kpi, idx) in [
          { label: 'Current Quarter Alerts', value: currentQuarterAlerts.length, color: 'text-yellow-600' },
          { label: 'Forecasted Future Alerts', value: futureQuarterAlerts.length, color: 'text-green-600' }
        ]" :key="idx">
          <BaseCard>
            <div class="text-center">
              <p class="text-gray-400">{{ kpi.label }}</p>
              <p class="text-2xl font-semibold" :class="kpi.color">{{ kpi.value }}</p>
            </div>
          </BaseCard>
        </div>

        <!-- 🔁 Dynamic Restock Alerts Section -->
        <div class="col-span-12">
          <BaseCard>
            <h2 class="text-xl font-semibold text-gray-700 mb-4">📦 Restock Recommendations</h2>

            <div class="overflow-x-auto">
              <h3 class="text-md font-medium text-blue-600 mb-2">Current Quarter</h3>
              <table class="min-w-full divide-y divide-gray-300 mb-8">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Product</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">County</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Retailer</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Quarter</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Current Demand</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Current Inventory</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Reorder Qty</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(alert, index) in currentQuarterAlerts" :key="index" class="bg-yellow-50">
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.product }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.county }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.supplier }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.quarter }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.forecast }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.inventory }}</td>
                    <td class="px-4 py-2 text-sm text-red-500 font-semibold">+{{ alert.reorderQty }}</td>
                  </tr>
                </tbody>
              </table>

              <h3 class="text-md font-medium text-green-600 mb-2">Future Forecasted</h3>
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Product</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">County</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Retailer</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Quarter</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Forecast</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Current Inventory</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Reorder Qty</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(alert, index) in futureQuarterAlerts" :key="index" class="bg-green-50">
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.product }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.county }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.supplier }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.quarter }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.forecast }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ alert.inventory }}</td>
                    <td class="px-4 py-2 text-sm text-red-500 font-semibold">+{{ alert.reorderQty }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </BaseCard>
        </div>


<!-- 📊 Supplier Performance Table -->
<BaseCard class="col-span-12">
  <h2 class="text-xl font-semibold text-gray-700 mb-4">📈 Supplier Performance</h2>

  <!-- Dropdown filters -->
  <div class="flex flex-wrap gap-6 mb-4">
    <div class="flex flex-col">
      <label class="text-sm text-gray-600 mb-1">Select Region:</label>
      <select v-model="selectedPerfRegion" @change="updateSupplierOptions" class="border rounded px-3 py-1 text-sm">
        <option disabled value="">-- Select Region --</option>
        <option v-for="region in availableRegions" :key="region" :value="region">{{ region }}</option>
      </select>
    </div>

    <div class="flex flex-col">
      <label class="text-sm text-gray-600 mb-1">Select Supplier:</label>
      <select v-model="selectedPerfSupplier" class="border rounded px-3 py-1 text-sm">
        <option disabled value="">-- Select Supplier --</option>
        <option v-for="supplier in filteredSupplierOptions" :key="supplier" :value="supplier">{{ supplier }}</option>
      </select>
    </div>
  </div>

  <!-- Table -->
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-300 table-auto">
      <thead class="bg-gray-50">
        <tr>
          <th class="min-w-[160px] px-4 py-2 text-left text-sm text-gray-500">Supplier</th>
          <th class="min-w-[180px] px-4 py-2 text-left text-sm text-gray-500">Fulfillment Rate</th>
          <th class="min-w-[180px] px-4 py-2 text-left text-sm text-gray-500">Forecast Deviation</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
<tr
  v-for="(entry, index) in filteredSupplierPerformanceTable"
  :key="index"
  class="hover:bg-gray-50"
>

  <td class="px-4 py-2 text-sm text-gray-700">{{ entry['Retailer Supplier Name'] }}</td>
  <td class="px-4 py-2 text-sm text-green-600">{{ (entry.avg_fulfillment_rate * 100).toFixed(1) }}%</td>
  <td class="px-4 py-2 text-sm text-blue-600">{{ entry.avg_forecast_deviation.toFixed(2) }}</td>
</tr>

      </tbody>
    </table>
  </div>
</BaseCard>



        <!-- 🎯 Inventory Drilldown Section -->
        <div class="col-span-12">
          <BaseCard>
            <h2 class="text-xl font-semibold text-gray-700 mb-4">📊 Inventory Management</h2>

            <div class="flex flex-wrap gap-4 mb-4">
              <div class="flex flex-col">
                <label class="text-sm text-gray-600 mb-1">Product:</label>
                <select v-model="selectedProduct" @change="updateFilteredStock" class="border rounded px-3 py-1 text-sm">
                  <option value="">All</option>
                  <option v-for="product in allProducts" :key="product" :value="product">{{ product }}</option>
                </select>
              </div>

              <div class="flex flex-col">
                <label class="text-sm text-gray-600 mb-1">County:</label>
                <select v-model="selectedCounty" @change="updateFilteredStock" class="border rounded px-3 py-1 text-sm">
                  <option value="">All</option>
                  <option v-for="county in allCounties" :key="county" :value="county">{{ county }}</option>
                </select>
              </div>

              <div class="flex flex-col">
                <label class="text-sm text-gray-600 mb-1">Quarter:</label>
                <select v-model="selectedQuarter" @change="updateFilteredStock" class="border rounded px-3 py-1 text-sm">
                  <option v-for="q in allQuarters" :key="q" :value="q">{{ q }}</option>
                </select>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Product</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">County</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Retailer</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Quarter</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Demand</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Current Inventory</th>
                    <th class="px-4 py-2 text-left text-sm text-gray-500">Units Sold</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(row, index) in filteredStock" :key="index">
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.product }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.county }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.supplier }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.quarter }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.forecast }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">{{ row.inventory }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700">
                      {{ row.unitsSold !== null ? row.unitsSold : '-' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>
  </template>


  <style scoped>
  th, td {
    white-space: nowrap;
  }
  </style>




  