<template>
  <div class="home-container">
    <el-card shadow="never" class="home-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Bell /></el-icon>
            消息推送
          </h2>
        </div>
      </template>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="messages.length === 0" class="empty-container">
        <el-empty description="暂无消息推送" />
      </div>
      <div v-else class="messages-list">
        <el-timeline>
          <el-timeline-item
            v-for="message in messages"
            :key="message.id"
            :timestamp="message.time"
            placement="top"
            :icon="Bell"
            color="#409eff"
          >
            <el-card shadow="hover" class="message-card">
              <h4>{{ message.title }}</h4>
              <p>{{ message.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'

const loading = ref(false)
const messages = ref([])

onMounted(() => {
  // TODO: 从后端获取消息推送
  // 这里暂时使用示例数据
  messages.value = [
    {
      id: 1,
      title: '欢迎使用网络工程协作平台',
      content: '这是一个用于师生协作的平台，您可以浏览科研项目、发布项目、进行合作等。',
      time: new Date().toLocaleString('zh-CN')
    }
  ]
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

.home-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px;
}

.messages-list {
  padding: 20px 0;
}

.message-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.message-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-card h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
}

.message-card p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}
</style>

