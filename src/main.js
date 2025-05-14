import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import './assets/scss/global.scss'
import './index.css'

// Base Components
import BaseCard from './components/Base/BaseCard.vue'
import BaseBtn from './components/Base/BaseBtn.vue'

// Plugins
import PerfectScrollbar from 'vue3-perfect-scrollbar'
import 'vue3-perfect-scrollbar/dist/vue3-perfect-scrollbar.css'
import VueApexCharts from 'vue3-apexcharts'

// Create app instance
const app = createApp(App)

// Global components
app.component('BaseCard', BaseCard)
app.component('BaseBtn', BaseBtn)

// Use plugins
app.use(PerfectScrollbar)
app.use(VueApexCharts)
app.use(store)
app.use(router)

// Mount app
app.mount('#app')
