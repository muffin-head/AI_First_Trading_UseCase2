<script setup>
import { ref, computed } from 'vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

// Images
import awsImage from '@/assets/images/awsbedrocksummary3.png'
import warehouseImage from '@/assets/images/datawarehouse2.png'
import azureImage from '@/assets/images/azuredatawarehouse1.png'

const activeTab = ref('aws')

const tabs = [
  {
    key: 'aws',
    icon: '🧠',
    title: 'Smart Document Summarization with Bedrock',
    image: awsImage,
    description: `📄 Skip the scroll struggle! With Amazon Textract + Claude Bedrock, messy PDFs turn into polished, digestible summaries — perfect for instant insights. AI that reads so you don’t have to.`
  },
  {
    key: 'lakehouse',
    icon: '🏗️',
    title: 'Bronze → Silver → Gold: Elevate Your Data Story',
    image: warehouseImage,
    description: `🚰 Raw CSVs? JSON logs? Stream chaos? This lakehouse engine refines them into clean, structured, and ML-ready assets. The data alchemy you didn’t know you needed — until now.`
  },
  {
    key: 'azure',
    icon: '🚀',
    title: 'Azure ML Lifecycle: From Chaos to Clarity',
    image: azureImage,
    description: `🔄 From log dumps to Power BI dashboards — Azure’s full-stack pipeline blends Databricks, SQL, and Analysis Services into one seamless flow. Automate intelligence across your org.`
  }
]

const currentTab = computed(() => tabs.find(t => t.key === activeTab.value))
</script>

<template>
  <div class="container mx-auto">
    <Breadcrumbs parentTitle="Data Architecture" subParentTitle="AI Architecture Gallery" />

    <!-- Tabs -->
    <div class="flex justify-center gap-4 my-6">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-5 py-2 rounded-full font-semibold transition-all duration-300',
          activeTab === tab.key
            ? 'bg-purple-600 text-white shadow'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        ]"
      >
        {{ tab.icon }} {{ tab.key === 'aws' ? 'AWS Bedrock' : tab.key === 'lakehouse' ? 'Lakehouse' : 'Azure ML' }}
      </button>
    </div>

    <!-- Selected Tab Content -->
    <div class="grid grid-cols-12 gap-6 mt-4">
      <div class="col-span-12 xl:col-span-8 bg-white p-6 rounded-2xl shadow border border-gray-200">
        <h2 class="text-2xl font-bold text-purple-700 mb-3">{{ currentTab.title }}</h2>
        <p class="text-gray-700 text-[1rem] leading-relaxed">{{ currentTab.description }}</p>
      </div>
      <div class="col-span-12 xl:col-span-4 flex items-center justify-center">
        <img
          :src="currentTab.image"
          :alt="currentTab.title"
          class="rounded-xl w-full h-[420px] object-cover border border-gray-300 shadow-md"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
h2 {
  font-family: 'Segoe UI', sans-serif;
}
</style>
