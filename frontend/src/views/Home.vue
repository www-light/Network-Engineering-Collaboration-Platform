<template>
  <div class="home">
    <div class="hero">
      <h1>欢迎使用网络工程协作平台</h1>
      <p>基于Django和Vue3构建的现代化协作平台</p>
    </div>
    
    <div class="status-card">
      <h2>系统状态</h2>
      <div v-if="loading" class="loading">检查中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="success">
        <p>✅ 后端服务连接正常</p>
        <p>{{ statusMessage }}</p>
      </div>
      <button @click="checkHealth" class="btn-primary">检查连接</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)
const error = ref(null)
const statusMessage = ref('')

const checkHealth = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await axios.get('/api/health/')
    statusMessage.value = response.data.message
  } catch (err) {
    error.value = '无法连接到后端服务，请确保Django服务器正在运行'
    console.error('Health check failed:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.home {
  text-align: center;
}

.hero {
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  color: #666;
}

.status-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 0 auto;
}

.status-card h2 {
  margin-top: 0;
  color: #333;
}

.loading {
  color: #667eea;
  margin: 1rem 0;
}

.error {
  color: #e74c3c;
  margin: 1rem 0;
}

.success {
  color: #27ae60;
  margin: 1rem 0;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

.btn-primary:active {
  transform: translateY(0);
}
</style>

