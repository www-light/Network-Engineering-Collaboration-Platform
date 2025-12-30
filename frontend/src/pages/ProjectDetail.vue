<template>
  <div class="project-detail-page">
    <el-card v-if="loading" shadow="never">
      <el-skeleton :rows="8" animated />
    </el-card>
    <ProjectDetail
      v-else-if="detail"
      :detail="detail"
      :loading="false"
      @apply="handleApply"
      @message="handleMessage"
    />
    <!-- 底部操作栏：点赞 / 收藏 / 评论 -->
    <template v-if="detail">
      <el-divider />
      <div class="post-actions">
        <el-button type="primary" @click="handleLike">点赞</el-button>
        <el-button @click="handleFavorite">收藏</el-button>
        <el-input
          v-model="commentText"
          type="textarea"
          placeholder="写下你的评论..."
          :rows="2"
          style="max-width: 520px"
        />
        <el-button type="success" @click="handleSubmitComment">发表评论</el-button>
      </div>
    </template>
    <el-empty v-else description="项目不存在" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getResearchDetail, getCompetitionDetail } from '@/api/project'
import { applyAndInvite } from '@/api/cooperation'
import { createConversation } from '@/api/conversation'
import { useUserStore } from '@/store/user'
import { likePost, favoritePost, commentPost } from '@/api/post'
import ProjectDetail from '@/components/ProjectDetail.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const detail = ref(null)
const loading = ref(false)
const commentText = ref('')

onMounted(async () => {
  const projectId = route.params.id
  await loadDetail(projectId)
})

const loadDetail = async (projectId) => {
  loading.value = true
  try {
    try {
      const data = await getResearchDetail(projectId)
      detail.value = { ...data, post_type: 'research' }
    } catch {
      const data = await getCompetitionDetail(projectId)
      detail.value = { ...data, post_type: 'competition' }
    }
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleApply = async () => {
  if (!detail.value) return
  
  try {
    const { value: roleStr } = await ElMessageBox.prompt('请选择角色：0-申请者, 1-邀请者', '申请/邀请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'number',
      inputPlaceholder: '0或1'
    })
    
    const role = parseInt(roleStr || '0')
    await applyAndInvite({
      post_id: detail.value.post_id,
      role
    })
    ElMessage.success('操作成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const handleMessage = async () => {
  if (!detail.value) return
  
  try {
    const receiverId = detail.value.teacher_id || userStore.userInfo?.user_id
    
    const response = await createConversation({
      post_id: detail.value.post_id,
      receiver_id: receiverId
    })
    
    router.push(`/message/${response.conversation_id}`)
  } catch (error) {
    ElMessage.error('创建会话失败')
    console.error(error)
  }
}

const ensureLoggedIn = () => {
  const uid = userStore.userInfo?.user_id
  if (!uid) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return null
  }
  return uid
}

const handleLike = async () => {
  if (!detail.value) return
  const uid = ensureLoggedIn()
  if (!uid) return
  try {
    await likePost({ post_id: detail.value.post_id, user_id: uid })
    ElMessage.success('已点赞')
  } catch (error) {
    ElMessage.error('点赞失败')
    console.error(error)
  }
}

const handleFavorite = async () => {
  if (!detail.value) return
  const uid = ensureLoggedIn()
  if (!uid) return
  try {
    await favoritePost({ post_id: detail.value.post_id, user_id: uid })
    ElMessage.success('已收藏')
  } catch (error) {
    ElMessage.error('收藏失败')
    console.error(error)
  }
}

const handleSubmitComment = async () => {
  if (!detail.value) return
  const uid = ensureLoggedIn()
  if (!uid) return
  if (!commentText.value || !commentText.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  try {
    await commentPost({ post_id: detail.value.post_id, user_id: uid, comment: commentText.value.trim() })
    ElMessage.success('评论成功')
    commentText.value = ''
  } catch (error) {
    ElMessage.error('评论失败')
    console.error(error)
  }
}
</script>

<style scoped>
.project-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>

