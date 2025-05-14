<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Breadcrumb from '@/components/Breadcrumbs.vue'
import BaseCard from '@/components/Base/BaseCard.vue'


const emailText = ref('')
const result = ref(null)
const loading = ref(false)
const error = ref('')

const evaluateEmail = async () => {
  loading.value = true
  result.value = null
  error.value = ''

  try {
    const response = await axios.post('http://localhost:5000/evaluate', {
      email_text: emailText.value,
    })
    result.value = response.data
  } catch (err) {
    error.value = 'Failed to connect to compliance engine.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container mx-auto">
    <Breadcrumb parentTitle="Tools" subParentTitle="Email Compliance" />

    <BaseCard>
      <template #cardHeader>
        <h2 class="text-xl font-semibold p-4">📧 Email Policy Compliance Check</h2>
      </template>

      <div>
        <textarea
          v-model="emailText"
          placeholder="Paste the email content here..."
          class="w-full h-40 p-4 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        ></textarea>

        <button
          @click="evaluateEmail"
          class="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Check Compliance
        </button>
      </div>
    </BaseCard>

    <div v-if="loading" class="mt-4 text-gray-600">Checking policy compliance...</div>

    <BaseCard v-if="result" class="mt-6">
      <h3 class="text-lg font-semibold mb-2">🔍 Compliance Result</h3>
      <p><strong>Matched Policy:</strong> {{ result.matched_policy }}</p>
      <p><strong>Violation:</strong> {{ result.violation ? 'Yes' : 'No' }}</p>
      <p class="mt-2"><strong>Explanation:</strong> {{ result.explanation }}</p>
    </BaseCard>

    <BaseCard v-if="error" class="mt-6 text-red-600">
      <p>❌ {{ error }}</p>
    </BaseCard>
  </div>
</template>
