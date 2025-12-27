<template>
  <div class="message-detail-container">
    <el-card v-if="!conversationId" shadow="never">
      <el-empty description="请选择会话" />
    </el-card>
    <el-card v-else shadow="never" class="detail-card">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Message /></el-icon>
            会话 #{{ conversationId }}
          </h3>
          <el-button type="danger" size="small" @click="handleClose">
            <el-icon><Close /></el-icon>
            关闭对话
          </el-button>
        </div>
      </template>
      <div class="message-content">
        <div class="messages-list" ref="messagesListRef">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else-if="messages.length === 0" class="empty-container">
            <el-empty description="暂无消息" />
          </div>
          <div
            v-else
            v-for="msg in messages"
            :key="msg.message_id"
            :class="['message-item', { 'is-self': msg.sender_id === userStore.userInfo?.user_id }]"
          >
            <div class="message-bubble">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime(msg.create_time) }}</div>
            </div>
          </div>
        </div>
        <div class="message-input">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入消息... (Ctrl+Enter发送)"
            @keyup.ctrl.enter="handleSend"
          />
          <div class="input-actions">
            <el-button type="primary" @click="handleSend" :loading="sending">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getMessages, sendMessage, closeConversation } from '@/api/conversation'
import { Message, Close, Promotion } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const conversationId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const sending = ref(false)
const messagesListRef = ref(null)

onMounted(() => {
  conversationId.value = route.params.conversationId
  if (conversationId.value) {
    loadMessages()
  }
})

watch(() => route.params.conversationId, (newId) => {
  conversationId.value = newId
  if (conversationId.value) {
    loadMessages()
  }
})

const loadMessages = async () => {
  if (!conversationId.value) return
  
  loading.value = true
  try {
    const response = await getMessages(conversationId.value)
    messages.value = response.messages.reverse()
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('获取消息失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || !conversationId.value) return
  
  sending.value = true
  try {
    await sendMessage(conversationId.value, {
      type: 'text',
      content: inputMessage.value
    })
    inputMessage.value = ''
    await loadMessages()
  } catch (error) {
    ElMessage.error('发送失败')
    console.error(error)
  } finally {
    sending.value = false
  }
}

const handleClose = async () => {
  if (!conversationId.value) return
  
  try {
    await ElMessageBox.confirm('确定要关闭此对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await closeConversation(conversationId.value)
    ElMessage.success('对话已关闭')
    // TODO: 刷新会话列表
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const formatTime = (time) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  if (messagesListRef.value) {
    messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight
  }
}
</script>

<style scoped>
.message-detail-container {
  height: 100%;
}

.detail-card {
  border-radius: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-content {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f8fafc 100%);
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.is-self {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-item.is-self .message-bubble {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.message-text {
  margin-bottom: 4px;
  word-wrap: break-word;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.message-item.is-self .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.message-input {
  border-top: 1px solid #e4e7ed;
  padding: 16px;
  background-color: white;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.loading-container,
.empty-container {
  padding: 40px;
  text-align: center;
}
</style>

