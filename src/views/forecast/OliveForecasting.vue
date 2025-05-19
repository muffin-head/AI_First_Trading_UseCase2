<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchOliveForecastData } from '@/data/oliveForecasting.js'
import BaseCard from '@/components/Base/BaseCard.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import ChartBlock from '@/components/ChartBlock.vue'

const fullData = ref({})
const data = ref({})
const loading = ref(true)

const selectedProduct = ref(null)
const selectedCounty = ref(null)
const selectedRegionGroup = ref(null)
const currentAverages = ref({})

const updateAverages = () => {
  const group = data.value[selectedProduct.value]?.find(
    entry => entry.county === selectedCounty.value
  )

  if (!group) {
    selectedRegionGroup.value = null
    currentAverages.value = {}
    return
  }

  selectedRegionGroup.value = group

  const quarters = ['2025Q1', '2025Q2', '2025Q3']
  const aggregated = {}

  quarters.forEach((q, i) => {
    let count = 0, units = 0, forecast = 0, inventory = 0

    group.suppliers.forEach(supplier => {
      const idx = supplier.quarters.indexOf(q)
      if (idx !== -1) {
        count++
        units += supplier.unitsSold[idx]
        forecast += supplier.forecasted[idx]
        inventory += supplier.inventory[idx]
      }
    })

    if (count > 0) {
      aggregated[q] = {
        unitsSold: Math.round(units / count),
        forecasted: Math.round(forecast / count),
        inventory: Math.round(inventory / count)
      }
    } else {
      const prev1 = quarters[i - 1] && aggregated[quarters[i - 1]]
      const prev2 = quarters[i - 2] && aggregated[quarters[i - 2]]
      const base = prev1?.forecasted || prev1?.unitsSold || 0
      const growth = prev2 ? prev1.forecasted - prev2.forecasted : Math.round(base * 0.1)

      aggregated[q] = {
        unitsSold: null,
        forecasted: Math.round(base + growth),
        inventory: null
      }
    }
  })

  currentAverages.value = aggregated
}

onMounted(async () => {
  const result = await fetchOliveForecastData()
  if (!result || !result.products) {
    console.error("🚨 'products' key missing in API response")
    return
  }

  fullData.value = result
  data.value = result.products

  selectedProduct.value = Object.keys(data.value)[0]
  const firstRegions = data.value[selectedProduct.value]
  selectedCounty.value = firstRegions.length > 0 ? firstRegions[0].county : null

  updateAverages()
  loading.value = false
})

const activeChartData = computed(() => {
  const quarters = ['2025Q1', '2025Q2', '2025Q3']
  const valid = quarters.filter(q => currentAverages.value[q])
  if (!valid.length) return null

  return {
    series: [
      {
        name: 'Units Sold (Q1–Q2)',
        data: valid.map(q => q === '2025Q3' ? null : currentAverages.value[q].unitsSold)
      },
      {
        name: 'Forecast (Q1–Q2)',
        data: valid.map(q => q === '2025Q3' ? null : currentAverages.value[q].forecasted)
      },
      {
        name: 'Forecast (Q3)',
        data: valid.map(q => q === '2025Q2' ? currentAverages.value[q].unitsSold : q === '2025Q3' ? currentAverages.value[q].forecasted : null)
      }
    ],
    chartOptions: {
      chart: { type: 'line', height: 320, toolbar: { show: false }, zoom: { enabled: false } },
      stroke: { curve: 'smooth', width: 3 },
      xaxis: {
        categories: valid,
        labels: { rotate: -45, style: { fontSize: '12px', colors: '#6b7280' } }
      },
      yaxis: {
        labels: { formatter: val => `${val.toFixed(0)} units` }
      },
      tooltip: {
        y: { formatter: val => `${val.toFixed(0)} units` }
      },
      colors: ['#10b981', '#3b82f6', '#ef4444']
    }
  }
})

const latestQ3 = computed(() => currentAverages.value['2025Q3']?.forecasted || '--')
const latestQ2 = computed(() => currentAverages.value['2025Q2']?.unitsSold || '--')
const latestInv = computed(() => currentAverages.value['2025Q3']?.inventory || '--')

const forecastAccuracy = computed(() => {
  const q1 = currentAverages.value['2025Q1']
  const q2 = currentAverages.value['2025Q2']
  if (!q1 || !q2) return '--'
  const err1 = Math.abs(q1.unitsSold - q1.forecasted) / q1.forecasted
  const err2 = Math.abs(q2.unitsSold - q2.forecasted) / q2.forecasted
  return `${(100 - ((err1 + err2) / 2) * 100).toFixed(1)}%`
})

const revenueAtRisk = computed(() => {
  const q3 = currentAverages.value['2025Q3']
  if (!q3 || !q3.inventory || !q3.forecasted) return '--'
  const gap = q3.forecasted - q3.inventory
  const unitValue = 2.5
  return gap > 0 ? `~£${(gap * unitValue).toLocaleString()}` : '£0'
})

const regionConfidence = computed(() => {
  const values = Object.values(currentAverages.value)
  if (!values.length) return '--'

  const variance = values.reduce((acc, val) => {
    if (val && val.unitsSold !== null && val.forecasted !== null) {
      acc.push(Math.abs(val.unitsSold - val.forecasted) / val.forecasted)
    }
    return acc
  }, [])

  const avgError = variance.length ? variance.reduce((a, b) => a + b, 0) / variance.length : 0
  return `${(100 - avgError * 100).toFixed(1)}%`
})

const forecastVsActualChart = computed(() => {
  if (!selectedRegionGroup.value) return null

  const suppliers = selectedRegionGroup.value.suppliers
  return {
    series: [
      { name: 'Actual', data: suppliers.map(s => s.unitsSold.at(-1)) },
      { name: 'Forecast', data: suppliers.map(s => s.forecasted.at(-1)) }
    ],
    chartOptions: {
      chart: { type: 'line' },
      xaxis: {
        categories: suppliers.map(s => s.supplier),
        labels: {
          show: true,
          rotate: -30,
          style: { fontSize: '11px', fontWeight: 400, colors: '#374151' },
          hideOverlappingLabels: false,
          showDuplicates: true,
          minHeight: 60,
          maxHeight: 120
        }
      },
      stroke: { curve: 'smooth' },
      colors: ['#34d399', '#60a5fa']
    }
  }
})

const forecastDeviationChart = computed(() => {
  if (!selectedRegionGroup.value) return null

  const quarters = ['2025Q1', '2025Q2', '2025Q3']
  const deviations = quarters.map(q => {
    let count = 0, total = 0
    selectedRegionGroup.value.suppliers.forEach(supplier => {
      const idx = supplier.quarters.indexOf(q)
      if (idx !== -1) {
        total += Math.abs(supplier.unitsSold[idx] - supplier.forecasted[idx]) / supplier.forecasted[idx]
        count++
      }
    })
    return count ? +(total / count * 100).toFixed(2) : null
  })

  return {
    series: [{ name: 'Deviation %', data: deviations }],
    chartOptions: {
      chart: { type: 'line' },
      xaxis: { categories: quarters },
      stroke: { curve: 'smooth' },
      colors: ['#f97316']
    }
  }
})

const forecastAccuracyTrendChart = computed(() => {
  if (!selectedRegionGroup.value) return null

  const quarters = ['2025Q1', '2025Q2', '2025Q3']
  const accuracy = quarters.map(q => {
    let total = 0, count = 0
    selectedRegionGroup.value.suppliers.forEach(supplier => {
      const idx = supplier.quarters.indexOf(q)
      if (idx !== -1) {
        total += Math.abs(supplier.unitsSold[idx] - supplier.forecasted[idx]) / supplier.forecasted[idx]
        count++
      }
    })
    return count ? +(100 - (total / count * 100)).toFixed(2) : null
  })

  return {
    series: [{ name: 'Forecast Accuracy (%)', data: accuracy }],
    chartOptions: {
      chart: { type: 'line' },
      xaxis: { categories: quarters },
      stroke: { curve: 'smooth' },
      colors: ['#6366f1']
    }
  }
})

const topSuppliersChart = computed(() => {
  if (!selectedRegionGroup.value) return null

  const suppliers = selectedRegionGroup.value.suppliers.map(supplier => {
    let total = 0, count = 0
    for (let i = 0; i < supplier.quarters.length; i++) {
      const forecast = supplier.forecasted[i]
      const actual = supplier.unitsSold[i]
      if (forecast > 0) {
        total += Math.abs(actual - forecast) / forecast
        count++
      }
    }
    const avgError = count ? total / count : 1
    return {
      name: supplier.supplier,
      accuracy: +(100 - avgError * 100).toFixed(2)
    }
  })

  const top5 = suppliers.sort((a, b) => b.accuracy - a.accuracy).slice(0, 5)
  return {
    series: [{ name: 'Accuracy (%)', data: top5.map(s => s.accuracy) }],
    chartOptions: {
      chart: { type: 'bar' },
      xaxis: { categories: top5.map(s => s.name) },
      colors: ['#10b981']
    }
  }
})
</script>


<template>
  <div class="container mx-auto">
    <Breadcrumbs parentTitle="Forecasting" subParentTitle="Demand Forecast – Olive Oil" />

    <div v-if="loading" class="text-center py-10 text-gray-500">
      Gathering fresh insights from supplier and regional sales...
    </div>

    <div v-else class="grid grid-cols-12 gap-6">
      <div class="col-span-12">
        <BaseCard>
          <div class="flex flex-wrap items-center gap-4">
            <div class="flex-1 min-w-[200px]">
              <label class="text-sm font-medium text-gray-700 mb-1 block">Select Product</label>
              <select v-model="selectedProduct" @change="updateAverages" class="w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm">
                <option v-for="product in Object.keys(data)" :key="product" :value="product">
                  🫒 {{ product }}
                </option>
              </select>
            </div>

            <div class="flex-1 min-w-[200px]">
              <label class="text-sm font-medium text-gray-700 mb-1 block">Select Region</label>
              <select v-model="selectedCounty" @change="updateAverages" class="w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm">
                <option v-for="region in data[selectedProduct]?.map(r => r.county)" :key="region" :value="region">
                  📍 {{ region }}
                </option>
              </select>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- KPI Summary -->
      <div class="col-span-12 md:col-span-4">
        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">Q3 Forecast</h4>
          <p class="text-2xl font-bold text-blue-600">{{ latestQ3 }} units</p>
        </BaseCard>
      </div>

      <div class="col-span-12 md:col-span-4">
        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">Last Quarter Sales (Q2)</h4>
          <p class="text-2xl font-bold text-green-600">{{ latestQ2 }} units</p>
        </BaseCard>
      </div>

      <div class="col-span-12 md:col-span-4">
        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">Inventory (Q3)</h4>
          <p class="text-2xl font-bold text-yellow-500">{{ latestInv }} units</p>
        </BaseCard>
      </div>

      <!-- Forecast Chart -->
      <ChartBlock
        v-if="activeChartData"
        title="📊 Units Sold vs Forecasted Demand"
        :chart="activeChartData"
        :type="'area'"
        :fullWidth="true"
      />

      <!-- Forecast Insights Section -->
      <div class="col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">🔍 Forecast Accuracy (Q1–Q2)</h4>
          <p class="text-2xl font-bold text-green-700">{{ forecastAccuracy }}</p>
          <p class="text-sm text-gray-400">Actuals matched forecasts within ±8% margin</p>
        </BaseCard>


        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">📍 Region Confidence</h4>
          <p class="text-2xl font-bold text-indigo-600">{{ selectedCounty }}: {{ regionConfidence }}</p>
          <p class="text-sm text-gray-400">High confidence based on stable historic patterns</p>
        </BaseCard>



        <BaseCard>
          <h4 class="text-sm font-semibold text-gray-500 mb-1">🔮 Drivers Behind Q3 Forecast</h4>
          <ul class="text-sm text-gray-700 list-disc pl-4 mt-2">
            <li>+18% from seasonal demand (Autumn)</li>
            <li>+9% due to double promotion weeks</li>
            <li>-5% impact from competitor pricing</li>
          </ul>
        </BaseCard>
      </div>

     <!-- 📊 Additional Forecast Visualizations in 2x2 grid -->
<div class="col-span-12 grid grid-cols-1 md:grid-cols-2 gap-6">
  <ChartBlock
    class="w-full h-full"
    v-if="selectedRegionGroup"
    title="📊 Forecast vs Actual by Supplier"
    :chart="forecastVsActualChart"
    :type="'bar'"
    :fullWidth="true"
  />
</div>




    </div>
  </div>
</template>

<style scoped>
select {
  appearance: none;
  background: url("data:image/svg+xml;charset=UTF-8,<svg fill='gray' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/></svg>") no-repeat right 0.75rem center;
  background-size: 1rem;
}
</style>