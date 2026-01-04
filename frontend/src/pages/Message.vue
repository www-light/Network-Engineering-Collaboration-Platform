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
                  {{ getOtherUserName(conv) }}
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

      <!-- 右侧消息详情 -->
      <el-main class="message-main">
        <el-card v-if="!selectedConversationId" shadow="never">
          <el-empty description="请选择会话" />
        </el-card>
        <el-card v-else shadow="never" class="detail-card">
          <template #header>
            <div class="card-header">
              <h3>
                <el-icon><Message /></el-icon>
                会话 #{{ selectedConversationId }}
              </h3>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="showAutoReplyDialog">
                  <el-icon><Setting /></el-icon>
                  自动回复
                </el-button>
                <el-button type="danger" size="small" @click="handleClose">
                  <el-icon><Close /></el-icon>
                  关闭对话
                </el-button>
              </div>
            </div>
          </template>
          <div class="message-content">
            <div class="messages-list" ref="messagesListRef">
              <div v-if="messagesLoading" class="loading-container">
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
                  <template v-if="isFileMessage(msg)">
                    <div class="file-message">
                      <a
                        :href="msg.content"
                        class="file-icon"
                        target="_blank"
                        rel="noopener noreferrer"
                        :title="getFileNameFromUrl(msg.content)"
                      >
                        <el-icon><Upload /></el-icon>
                      </a>
                      <div class="file-name">{{ getFileNameFromUrl(msg.content) }}</div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="message-text">{{ msg.content }}</div>
                  </template>
                  <div class="message-time">{{ formatMessageTime(msg.create_time) }}</div>
                </div>
              </div>
            </div>
            <div class="message-input">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="3"
                placeholder="输入消息... (Ctrl+Enter发送)"
                :disabled="isClosed"
                @keyup.ctrl.enter="handleSend"
              />
              <div class="input-actions">
                <div v-if="isClosed" class="closed-tip">
                  <el-alert type="warning" :closable="false">会话已关闭，无法发送消息</el-alert>
                </div>
                <div v-else-if="pendingFile" class="pending-file">
                  <el-tag type="info" closable @close="clearPendingFile">
                    待发送文件：{{ pendingFile.original_filename || getFileNameFromUrl(pendingFile.download_url) }}
                  </el-tag>
                </div>
                <el-upload
                  v-if="!isClosed"
                  ref="uploadRef"
                  class="file-upload"
                  action=""
                  :auto-upload="false"
                  @change="handleFileSelect"
                >
                  <template #trigger>
                    <el-button type="info">
                      <el-icon><Upload /></el-icon>
                      上传文件
                    </el-button>
                  </template>
                </el-upload>
                <el-button type="primary" @click="handleSend" :loading="sending" :disabled="isClosed">
                  <el-icon><Promotion /></el-icon>
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
    
    <!-- 自动回复设置对话框 -->
    <el-dialog v-model="autoReplyDialogVisible" title="自动回复设置" width="400px">
      <div class="auto-reply-content">
        <div class="setting-item">
          <label>启用自动回复</label>
          <el-switch v-model="autoReplyEnabled" />
        </div>
        <div class="setting-item">
          <label>回复内容</label>
          <el-input
            v-model="autoReplyMessage"
            type="textarea"
            :rows="4"
            placeholder="输入自动回复的消息内容"
            :disabled="!autoReplyEnabled"
          />
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="autoReplyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAutoReplySettings" :loading="loadingAutoReply">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, defineOptions } from 'vue'
import { useRoute } from 'vue-router'

defineOptions({ name: 'MessagePage' })
import { useUserStore } from '@/store/user'
import { getConversations, getMessages, sendMessage, closeConversation, uploadConversationFile, getAutoReplySettings, updateAutoReplySettings } from '@/api/conversation'
import { Message, Close, Promotion, Setting, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const conversations = ref([])
const selectedConversationId = ref(null)
const currentConversation = ref(null)
const loading = ref(false)
const messages = ref([])
const messagesLoading = ref(false)
const inputMessage = ref('')
const sending = ref(false)
const messagesListRef = ref(null)
const pendingFile = ref(null)
const autoReplyDialogVisible = ref(false)
const autoReplyEnabled = ref(false)
const autoReplyMessage = ref('')
const loadingAutoReply = ref(false)
const isClosed = ref(false)

onMounted(() => {
  loadConversations()
  loadAutoReplySettings()
  
  // 如果URL中有conversationId参数，自动选中
  if (route.query.conversationId) {
    selectedConversationId.value = parseInt(route.query.conversationId)
  }
})

watch(selectedConversationId, (newId) => {
  if (newId) {
    loadMessages()
  }
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

const loadMessages = async (silent = false) => {
  if (!selectedConversationId.value) return
  
  if (!silent) messagesLoading.value = true
  try {
    const response = await getMessages(selectedConversationId.value)
    messages.value = response.messages.reverse()
    markConversationRead()
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('获取消息失败')
    console.error(error)
  } finally {
    if (!silent) messagesLoading.value = false
  }
}

const handleConversationClick = (conv) => {
  selectedConversationId.value = conv.conversation_id
  currentConversation.value = conv
  isClosed.value = conv.status === '0'
}

const getOtherUserName = (conv) => {
  // 如果当前用户是user1，显示user2的名字；反之亦然
  if (conv.user1_id === userStore.userInfo?.user_id) {
    return conv.user2_name || '未知用户'
  } else {
    return conv.user1_name || '未知用户'
  }
}

const handleSend = async () => {
  if (!selectedConversationId.value) return
  const hasText = !!inputMessage.value.trim()
  const hasFile = !!pendingFile.value
  if (!hasText && !hasFile) return
  
  sending.value = true
  try {
    const newMessages = []
    // 先发文本（如果有）
    if (hasText) {
      const res = await sendMessage(selectedConversationId.value, {
        type: 'text',
        content: inputMessage.value
      })
      if (res?.messages) newMessages.push(...res.messages)
    }

    // 再发文件（如果有）
    if (hasFile) {
      const fileContent = pendingFile.value.download_url || pendingFile.value.attachment_id
      const res = await sendMessage(selectedConversationId.value, {
        type: 'file',
        content: fileContent
      })
      if (res?.messages) newMessages.push(...res.messages)
    }

    // 合并新消息（包含可能的自动回复），按时间排序
    if (newMessages.length) {
      const normalized = newMessages.map(normalizeMessage)
      messages.value = [...messages.value, ...normalized].sort((a, b) => new Date(a.create_time) - new Date(b.create_time))
    } else {
      await loadMessages(true)
    }

    inputMessage.value = ''
    pendingFile.value = null
    await nextTick()
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送失败')
    console.error(error)
  } finally {
    sending.value = false
  }
}

const handleClose = async () => {
  if (!selectedConversationId.value) return
  
  try {
    await ElMessageBox.confirm('确定要关闭此对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await closeConversation(selectedConversationId.value)
    ElMessage.success('对话已关闭')
    isClosed.value = true
    if (currentConversation.value) {
      currentConversation.value.status = '0'
    }
    // 更新会话列表中的状态
    const conv = conversations.value.find(c => c.conversation_id === selectedConversationId.value)
    if (conv) {
      conv.status = '0'
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const formatTime = (time) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const formatMessageTime = (time) => {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  if (messagesListRef.value) {
    messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight
  }
}

const loadAutoReplySettings = async () => {
  try {
    const data = await getAutoReplySettings()
    autoReplyEnabled.value = data.auto_reply_enabled
    autoReplyMessage.value = data.auto_reply_message
  } catch (error) {
    console.error('获取自动回复设置失败', error)
  }
}

const showAutoReplyDialog = () => {
  autoReplyDialogVisible.value = true
}

const saveAutoReplySettings = async () => {
  loadingAutoReply.value = true
  try {
    await updateAutoReplySettings({
      auto_reply_enabled: autoReplyEnabled.value,
      auto_reply_message: autoReplyMessage.value
    })
    ElMessage.success('自动回复设置已保存')
    autoReplyDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存设置失败')
    console.error(error)
  } finally {
    loadingAutoReply.value = false
  }
}

const handleFileSelect = async (file) => {
  if (!file) return
  sending.value = true
  try {
    const response = await uploadConversationFile(file.raw)
    const data = response.data || {}
    const downloadUrl = data.download_url
    const attachmentId = data.attachment_id
    if (!downloadUrl && !attachmentId) {
      ElMessage.error('文件上传失败：缺少返回的下载地址')
      return
    }
    pendingFile.value = {
      download_url: downloadUrl,
      attachment_id: attachmentId,
      original_filename: data.original_filename
    }
    ElMessage.success('文件已上传，点击发送可发送给对方')
  } catch (error) {
    ElMessage.error('文件上传失败')
    console.error(error)
  } finally {
    sending.value = false
  }
}

const clearPendingFile = () => {
  pendingFile.value = null
}

const markConversationRead = () => {
  const conv = conversations.value.find(c => c.conversation_id === selectedConversationId.value)
  if (conv) {
    conv.unread_count = 0
  }
}

// 确保新消息数据结构与列表一致
const normalizeMessage = (msg) => ({
  ...msg,
  content_type: String(msg.content_type),
  is_read: msg.is_read ?? true
})

const isFileMessage = (msg) => msg.content_type === 1 || msg.content_type === '1'

const getFileNameFromUrl = (url) => {
  if (!url) return '文件'
  try {
    const parts = url.split('/')
    return parts[parts.length - 1] || '文件'
  } catch (e) {
    return '文件'
  }
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

.header-actions {
  display: flex;
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
  gap: 8px;
}

.file-upload {
  display: inline;
}

.file-message {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #ecf5ff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  text-decoration: none;
  transition: background 0.2s, transform 0.2s;
}

.file-icon:hover {
  background: #d9ecff;
  transform: translateY(-1px);
}

.file-name {
  font-size: 14px;
  color: #303133;
  word-break: break-all;
}

.auto-reply-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-item label {
  font-weight: 600;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

