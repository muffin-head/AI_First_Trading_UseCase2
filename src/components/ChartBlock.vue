<script setup>
import { defineProps } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  chart: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'bar'
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

// Merge Y-axis formatter to limit decimals globally
const mergedOptions = {
  ...props.chart.chartOptions,
  yaxis: {
    ...(props.chart.chartOptions.yaxis || {}),
    labels: {
      ...(props.chart.chartOptions.yaxis?.labels || {}),
      formatter: val => Number(val).toFixed(1)
    }
  }
}
</script>

<template>
  <div :class="fullWidth ? 'col-span-12' : 'col-span-12 xl:col-span-6 md:col-span-6'">
    <BaseCard>
      <h4 class="chart-title mb-4">{{ title }}</h4>

      <div v-if="chart && chart.series && chart.series.length > 0">
        <VueApexCharts
          :type="type"
          :options="mergedOptions"
          :series="chart.series"
          height="320"
        />
      </div>

      <div v-else class="text-gray-400 text-sm py-10 text-center">
        No data available for this chart.
      </div>
    </BaseCard>
  </div>
</template>

<style scoped>
.chart-title {
  font-weight: 600;
  font-size: 1.125rem;
  color: #4b5563;
}
</style>
