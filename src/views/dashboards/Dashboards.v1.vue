<script setup>
import { onMounted, ref } from 'vue'
import { fetchWineDashboardData } from '@/data/dashboard.v1.js'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import ChartBlock from '@/components/ChartBlock.vue'

const dashboard = ref(null)
const loading = ref(true)

onMounted(async () => {
  dashboard.value = await fetchWineDashboardData()
  loading.value = false
})
</script>

<template>
  <div class="container mx-auto">
    <Breadcrumbs parentTitle="Dashboard" subParentTitle="Wine Insights" />

    <div v-if="loading" class="text-center py-10 text-gray-500">
      Loading wine dashboard...
    </div>

    <div v-else class="grid grid-cols-12 gap-5">
      <!-- KPIs -->
      <div
        class="col-span-12 sm:col-span-6 xl:col-span-3"
        v-for="(kpi, i) in [
  { icon: 'i-Globe', label: 'Top Country', value: dashboard.kpis.topCountry },
  { icon: 'i-Home1', label: 'Total Wines', value: dashboard.kpis.totalWines },
  { icon: 'i-Like', label: 'Avg. Rating', value: dashboard.kpis.avgRating },
  { icon: 'i-Folder', label: 'Varieties', value: dashboard.kpis.varietyCount }
]
"
        :key="i"
      >
        <BaseCard>
          <div class="flex items-center">
            <i :class="`${kpi.icon} text-6xl text-purple-200`"></i>
            <div class="m-auto">
              <p class="text-gray-400">{{ kpi.label }}</p>
              <p class="text-xl text-primary font-semibold">{{ kpi.value }}</p>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Dynamic Chart Blocks -->
      <ChartBlock title="Top 5 Wine Producing Countries" :chart="dashboard.charts.countryChart" />
      <ChartBlock title="Wine Type Distribution" :chart="dashboard.charts.typeChart" :type="'pie'" />
      <ChartBlock title="Average Rating Over Years" :chart="dashboard.charts.ratingOverYearChart" :type="'line'" :fullWidth="true" />
      <ChartBlock title="Top Regions by Wine Count" :chart="dashboard.charts.regionChart" />
      <ChartBlock title="Top Wineries by Count" :chart="dashboard.charts.wineryChart" />
      <ChartBlock title="Average Price by Country" :chart="dashboard.charts.priceCountryChart" />
      <ChartBlock title="Average Price by Type" :chart="dashboard.charts.priceTypeChart" :type="'pie'" />
      <ChartBlock title="Price Range Distribution" :chart="dashboard.charts.priceBucketChart" />
      <ChartBlock title="Best Value Wines (Rating ÷ Price)" :chart="dashboard.charts.bestValueChart" :type="'pie'" />
      <ChartBlock title="Vintage Distribution" :chart="dashboard.charts.vintageChart"  :type="'line'" :fullWidth="true"/>
      <ChartBlock title="Top Wineries by Avg. Rating" :chart="dashboard.charts.wineryRatingChart" />
      <ChartBlock title="Avg. Price per Wine Type" :chart="dashboard.charts.typePriceChart"  />
            

            
      <!-- 🌟 Custom Featured Wine Card -->
<div class="col-span-12 xl:col-span-6">
  <BaseCard noPadding class="overflow-hidden">
    <div class="p-5 grid grid-cols-12 gap-4 items-center">
      <!-- Column 1: Price + Link -->
      <div class="col-span-4">
        <div class="text-gray-600 font-medium text-lg mb-1">Alpilles Rosé 2024</div>
        <p class="text-sm text-gray-500 mb-2">Domaine de Valdition</p>
        <div class="flex items-center space-x-3 mb-2">
          <span class="text-green-600 font-bold text-lg">£11.97</span>
          <span class="text-xs text-gray-400">£15.96/L</span>
        </div>
        <a
          href="https://www.vinatis.co.uk/74041-alpilles-rose-2024-domaine-de-valdition"
          target="_blank"
          rel="noopener noreferrer"
          class="text-purple-600 underline text-sm"
        >
          View on Vinatis →
        </a>
      </div>

      <!-- Column 2: Description -->
      <div class="col-span-5 pr-4">
        <p class="text-sm text-gray-600">
          The new vintage of the old Cuvée Tradition. Love and respect for the soil, this is the mantra of the Domaine de Valdition,
          which has moved from semi to fully organic farming. A single goal: the constant search for quality.
          <br /><br />
          Their mission accomplished with this flagship cuvée: This rosé from Provence will use its attractive nose to seduce you.
          Its aromas of vine peach, citrus fruits, and its freshness make it a delicate pleasure to savour under a parasol.
        </p>
      </div>

      <!-- Column 3: Wine Image -->
      <div class="col-span-3">
        <img
          src="\src\assets\images\alpilles-rose-2024.png"
          alt="Alpilles Rosé 2024"
          class="object-contain h-40 w-full rounded-lg shadow"
        />
      </div>
    </div>
  </BaseCard>
</div>


<!-- 🌟 Custom Featured Wine Card -->
<div class="col-span-12 xl:col-span-6">
  <BaseCard noPadding class="overflow-hidden">
    <div class="p-5 grid grid-cols-12 gap-4 items-center">
      <!-- Column 1: Price + Link -->
      <div class="col-span-4">
        <div class="text-gray-600 font-medium text-lg mb-1">Ségla 2016</div>
        <p class="text-sm text-gray-500 mb-2">second wine of Château Rauzan-Ségla</p>
        <div class="flex items-center space-x-3 mb-2">
          <span class="text-green-600 font-bold text-lg">£40.89</span>
          <span class="text-xs text-gray-400">£54.52/L</span>
        </div>
        <a
          href="https://www.vinatis.co.uk/70849-segla-2016-second-wine-of-chateau-rauzan-segla"
          target="_blank"
          rel="noopener noreferrer"
          class="text-purple-600 underline text-sm"
        >
          View on Vinatis →
        </a>
      </div>

      <!-- Column 2: Description -->
      <div class="col-span-5 pr-4">
        <p class="text-sm text-gray-600">
          Ségla is a beautiful second wine with good aromatic complexity and a nice depth. Delicious and elegant, it beautifully expresses the radiant personality of the vintage with aromas of dark fruits such as blackberry and blueberry. 
          <br /><br />
          The palate is medium bodied with a juicy start and spicy notes that gently tickle the taste buds. The finish is long and is expressed with an extraordinary tension. Wonderful!
        </p>
      </div>

      <!-- Column 3: Wine Image -->
      <div class="col-span-3">
        <img
          src="\src\assets\images\segla-2016.png"
          alt="segla-2016.png"
          class="object-contain h-40 w-full rounded-lg shadow"
        />
      </div>
    </div>
  </BaseCard>
</div>




    </div>
  </div>
</template>


<style scoped>
.card-title {
  font-weight: 600;
  font-size: 1.125rem;
  color: #4b5563;
}
</style>
