<template>
  <div class="message-container">
    <el-container class="message-layout">
      <!-- 左侧会话列表 -->
      <el-aside width="300px" class="message-aside">
        <el-card shadow="never" class="aside-card">
          <template #header>
            <div class="aside-header">
              <h3>
                <el-icon><Message /></el-icon>
                会话列表
              </h3>
            </div>
          </template>
          <div class="conversation-list">
            <div v-if="loading" class="loading-container">
              <el-skeleton :rows="5" animated />
            </div>
            <div v-else-if="conversations.length === 0" class="empty-container">
              <el-empty description="暂无会话" />
            </div>
            <div
              v-else
              v-for="conv in conversations"
              :key="conv.conversation_id"
              :class="['conversation-item', { active: selectedConversationId === conv.conversation_id }]"
              @click="handleConversationClick(conv)"
            >
              <div class="conversation-info">
                <div class="conversation-title">
                  会话 #{{ conv.conversation_id }}
                </div>
                <div class="conversation-time">
                  {{ formatTime(conv.last_message_at) }}
                </div>
              </div>
              <el-tag :type="conv.status === '1' ? 'success' : 'info'" size="small" effect="light">
                {{ conv.status === '1' ? '进行中' : '已关闭' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-aside>

      <!-- 右侧消息内容 -->
      <el-main class="message-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getConversations } from '@/api/conversation'
import { Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

const conversations = ref([])
const selectedConversationId = ref(null)
const loading = ref(false)

onMounted(() => {
  loadConversations()
})

const loadConversations = async () => {
  loading.value = true
  try {
    const data = await getConversations()
    conversations.value = data
    if (data.length > 0 && !selectedConversationId.value) {
      handleConversationClick(data[0])
    }
  } catch (error) {
    ElMessage.error('获取会话列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleConversationClick = (conv) => {
  selectedConversationId.value = conv.conversation_id
  router.push(`/message/${conv.conversation_id}`)
}

const formatTime = (time) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.message-container {
  height: calc(100vh - 100px);
}

.message-layout {
  height: 100%;
  background: #f8fafc;
}

.message-aside {
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
  background: white;
}

.aside-card {
  border-radius: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.aside-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  margin: 4px 0;
}

.conversation-item:hover {
  background-color: #f5f5f5;
}

.conversation-item.active {
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
  border-left: 3px solid #409eff;
}

.conversation-info {
  margin-bottom: 8px;
}

.conversation-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.conversation-time {
  font-size: 12px;
  color: #909399;
}

.loading-container,
.empty-container {
  padding: 20px;
}

.message-main {
  padding: 20px;
  overflow-y: auto;
  background: white;
}
</style>

