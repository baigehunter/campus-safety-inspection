import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import router from './router'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import design system
import './styles/design-system.css'
import './style.css'

const app = createApp(App)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, {
  // Custom Element Plus theme
  size: 'default',
})

// Pinia should be installed before router
app.use(createPinia())
app.use(router)

app.mount('#app')
