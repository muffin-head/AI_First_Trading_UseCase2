<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

// Search and results
const isSearchOpen = ref(false)
const searchQuery = ref('')
const searchResults = ref([])

// Filters
const selectedType = ref('')
const selectedCountry = ref('')
const minRating = ref(null)

// Sorting
const sortKey = ref('')
const sortDirection = ref('asc')

const performSearch = async () => {
  if (searchQuery.value.trim().length >= 2) {
    const response = await axios.post('http://localhost:5000/api/search-wines', {
      query: searchQuery.value.trim()
    })
    searchResults.value = response.data
    isSearchOpen.value = true
  }
}

// Unique dropdown values
const types = computed(() => [...new Set(searchResults.value.map(w => w.Type))])
const countries = computed(() => [...new Set(searchResults.value.map(w => w.Country))])

// Filtered and sorted data
const filteredResults = computed(() => {
  let filtered = searchResults.value.filter(item => {
    return (
      (!selectedType.value || item.Type === selectedType.value) &&
      (!selectedCountry.value || item.Country === selectedCountry.value) &&
      (!minRating.value || item.Rating >= minRating.value)
    )
  })

  if (sortKey.value) {
    filtered = [...filtered].sort((a, b) => {
      const aVal = a[sortKey.value]
      const bVal = b[sortKey.value]
      return sortDirection.value === 'asc' ? aVal - bVal : bVal - aVal
    })
  }

  return filtered
})
</script>

<template>
  <!-- Search Bar -->
  <div class="relative text-gray-600 search-bar mx-3 sm:flex hidden">
    <input
      v-model="searchQuery"
      @keyup.enter="performSearch"
      class="bg-gray-100 h-10 px-5 pr-10 rounded-full text-sm focus:outline-none w-80"
      type="search"
      placeholder="Search wines..."
    />
    <button
      class="absolute right-0 top-0 mt-2 mr-4 focus:outline-none"
      type="button"
      @click="performSearch"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </button>
  </div>

  <!-- Search Result Popup -->
  <div v-if="isSearchOpen" class="search-ui open">
    <div class="container mx-auto">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-semibold text-purple-600">Search Results</h2>
        <button class="btn text-gray-600" @click="isSearchOpen = false">
          <i class="i-Close-Window text-xl"></i> Close
        </button>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-4 mb-4">
        <select v-model="selectedType" class="border rounded px-2 py-1">
          <option value="">All Types</option>
          <option v-for="type in types" :key="type" :value="type">{{ type }}</option>
        </select>

        <select v-model="selectedCountry" class="border rounded px-2 py-1">
          <option value="">All Countries</option>
          <option v-for="country in countries" :key="country" :value="country">{{ country }}</option>
        </select>

        <input
          v-model.number="minRating"
          type="number"
          min="0"
          max="5"
          step="0.1"
          placeholder="Min Rating"
          class="border rounded px-2 py-1 w-32"
        />

        <select v-model="sortKey" class="border rounded px-2 py-1">
          <option value="">Sort by</option>
          <option value="Rating">Rating</option>
          <option value="Price">Price</option>
        </select>

        <select v-model="sortDirection" class="border rounded px-2 py-1">
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>
      </div>

      <!-- Results Table -->
      <div v-if="filteredResults.length">
        <table class="min-w-full table-auto text-left border border-gray-300 bg-white rounded shadow">
          <thead class="bg-purple-100">
            <tr>
              <th class="px-4 py-2">Name</th>
              <th class="px-4 py-2">Type</th>
              <th class="px-4 py-2">Rating</th>
              <th class="px-4 py-2">Price</th>
              <th class="px-4 py-2">Country</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, index) in filteredResults"
              :key="index"
              class="border-t hover:bg-gray-50"
            >
              <td class="px-4 py-2">{{ item.Name }}</td>
              <td class="px-4 py-2">{{ item.Type }}</td>
              <td class="px-4 py-2">{{ item.Rating }}</td>
              <td class="px-4 py-2">${{ item.Price }}</td>
              <td class="px-4 py-2">{{ item.Country }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="text-gray-500 mt-6">No results match your filters.</div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.search-ui {
  position: fixed;
  top: -200%;
  left: 0;
  right: 0;
  bottom: 0;
  margin: auto;
  padding: 1.5rem;
  z-index: 9999;
  background-color: #fff;
  max-width: 100%;
  height: 100vh;
  opacity: 0;
  transition: all 0.3s ease-in;
  visibility: hidden;
  overflow-y: auto;

  &.open {
    opacity: 1;
    visibility: visible;
    top: 0;
  }
}
</style>
