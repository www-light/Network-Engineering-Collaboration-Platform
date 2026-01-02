<template>
  <div class="project-detail">
    <el-card v-if="loading" shadow="never">
      <el-skeleton :rows="8" animated />
    </el-card>
    <div v-else-if="detail">
      <!-- 项目信息板块 -->
      <el-card shadow="never" class="detail-card">
        <template #header>
          <div class="detail-header">
            <h2>{{ getTitle() }}</h2>
            <div class="header-actions">
              <el-button type="primary" @click="handleApply">
                <el-icon><Link /></el-icon>
                申请/邀请
              </el-button>
              <el-button @click="handleMessage">
                <el-icon><Message /></el-icon>
                私信
              </el-button>
            </div>
          </div>
        </template>
        <div class="detail-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item v-if="detail.post_type !== 'personal'" label="项目名称">
              {{ getTitle() }}
            </el-descriptions-item>
            <el-descriptions-item v-if="detail.post_type !== 'personal'" label="发布人">
              {{ getPublisherName() }}
            </el-descriptions-item>
            <el-descriptions-item v-if="detail.post_type === 'personal'" label="发布人">
              {{ getPublisherName() }}
            </el-descriptions-item>
            <template v-if="detail.post_type === 'research'">
              <el-descriptions-item label="研究方向">
                {{ detail.research_direction }}
              </el-descriptions-item>
              <el-descriptions-item label="技术栈">
                {{ detail.tech_stack }}
              </el-descriptions-item>
              <el-descriptions-item label="招募人数">
                {{ detail.recruit_quantity }}人
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDate(detail.starttime) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间" :span="2">
                {{ formatDate(detail.endtime) }}
              </el-descriptions-item>
              <el-descriptions-item label="预期成果" :span="2">
                {{ detail.outcome }}
              </el-descriptions-item>
              <el-descriptions-item label="联系方式" :span="2">
                {{ detail.contact }}
              </el-descriptions-item>
              <el-descriptions-item v-if="detail.attachments && detail.attachments.length > 0" label="附件" :span="2">
                <div class="attachments-list">
                  <div
                    v-for="attachment in detail.attachments"
                    :key="attachment.attachment_id"
                    class="attachment-item"
                  >
                    <el-link
                      type="primary"
                      :href="getAttachmentUrl(attachment.download_url)"
                      @click.prevent="handleDownloadAttachment(attachment)"
                    >
                      <el-icon><Download /></el-icon>
                      {{ attachment.original_filename }}
                    </el-link>
                    <span class="attachment-size">({{ attachment.formatted_size || formatFileSize(attachment.file_size) }})</span>
                  </div>
                </div>
              </el-descriptions-item>
            </template>
            <template v-else-if="detail.post_type === 'competition'">
              <el-descriptions-item label="竞赛类型">
                {{ getCompetitionTypeText(detail.competition_type) }}
              </el-descriptions-item>
              <el-descriptions-item label="截止时间" :span="2">
                {{ formatDate(detail.deadline) }}
              </el-descriptions-item>
              <el-descriptions-item label="团队要求" :span="2">
                {{ detail.team_require }}
              </el-descriptions-item>
              <el-descriptions-item label="指导方式" :span="2">
                {{ getGuideWayText(detail.guide_way) }}
              </el-descriptions-item>
              <el-descriptions-item label="奖励" :span="2">
                {{ detail.reward }}
              </el-descriptions-item>
              <el-descriptions-item v-if="detail.attachments && detail.attachments.length > 0" label="附件" :span="2">
                <div class="attachments-list">
                  <div
                    v-for="attachment in detail.attachments"
                    :key="attachment.attachment_id"
                    class="attachment-item"
                  >
                    <el-link
                      type="primary"
                      :href="getAttachmentUrl(attachment.download_url)"
                      @click.prevent="handleDownloadAttachment(attachment)"
                    >
                      <el-icon><Download /></el-icon>
                      {{ attachment.original_filename }}
                    </el-link>
                    <span class="attachment-size">({{ attachment.formatted_size || formatFileSize(attachment.file_size) }})</span>
                  </div>
                </div>
              </el-descriptions-item>
            </template>
            <template v-else-if="detail.post_type === 'personal'">
              <el-descriptions-item label="专业方向">
                {{ formatMajor(detail.major) }}
              </el-descriptions-item>
              <el-descriptions-item label="技能" :span="2">
                <div class="skills-list">
                  <el-tag
                    v-for="(skill, index) in (detail.skills || [])"
                    :key="'skill-' + index"
                    type="primary"
                    size="small"
                    style="margin-right: 8px; margin-bottom: 4px;"
                  >
                    {{ skill.skill_name }} ({{ getSkillDegreeText(skill.skill_degree) }})
                  </el-tag>
                  <span v-if="!detail.skills || detail.skills.length === 0" class="no-tags">暂无技能</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="可投入时间" :span="2">
                {{ detail.spend_time }}
              </el-descriptions-item>
              <!-- 项目经验独占一行，在可投入时间下面 -->
              <el-descriptions-item label="项目经验" :span="2">
                <span v-if="detail.project_experience" class="project-experience-text">{{ detail.project_experience }}</span>
                <span v-else class="no-experience">暂无项目经验</span>
              </el-descriptions-item>
              <el-descriptions-item v-if="detail.experience_link" label="经验链接" :span="2">
                <el-link :href="detail.experience_link" target="_blank" type="primary">
                  {{ detail.experience_link }}
                </el-link>
              </el-descriptions-item>
              <el-descriptions-item label="兴趣领域" :span="2">
                <div class="tags-container">
                  <el-tag
                    v-for="tag in (detail.tags || [])"
                    :key="tag.tag_id"
                    type="primary"
                    size="small"
                    style="margin-right: 8px; margin-bottom: 4px;"
                  >
                    {{ tag.name }}
                  </el-tag>
                  <span v-if="!detail.tags || detail.tags.length === 0" class="no-tags">暂无标签</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="期望合作类型" :span="2">
                {{ getExpectWorktypeText(detail.expect_worktype) }}
              </el-descriptions-item>
              <el-descriptions-item label="筛选条件" :span="2">
                {{ getFilterText(detail.filter) }}
              </el-descriptions-item>
              <el-descriptions-item v-if="detail.attachments && detail.attachments.length > 0" label="附件" :span="2">
                <div class="attachments-list">
                  <div
                    v-for="attachment in detail.attachments"
                    :key="attachment.attachment_id"
                    class="attachment-item"
                  >
                    <el-link
                      type="primary"
                      :href="getAttachmentUrl(attachment.download_url)"
                      @click.prevent="handleDownloadAttachment(attachment)"
                    >
                      <el-icon><Download /></el-icon>
                      {{ attachment.original_filename }}
                    </el-link>
                    <span class="attachment-size">({{ attachment.formatted_size || formatFileSize(attachment.file_size) }})</span>
                  </div>
                </div>
              </el-descriptions-item>
            </template>
          </el-descriptions>
        </div>
        
        <!-- 点赞和收藏按钮 -->
        <div class="action-bar">
          <el-button
            :type="detail.is_liked ? 'primary' : 'default'"
            :icon="detail.is_liked ? StarFilled : Star"
            @click="handleLike"
            :loading="likeLoading"
          >
            {{ detail.is_liked ? '已点赞' : '点赞' }}
            <span class="count">{{ detail.like_num || 0 }}</span>
          </el-button>
          <el-button
            :type="detail.is_favorited ? 'warning' : 'default'"
            :icon="detail.is_favorited ? CollectionTag : Collection"
            @click="handleFavorite"
            :loading="favoriteLoading"
          >
            {{ detail.is_favorited ? '已收藏' : '收藏' }}
            <span class="count">{{ detail.favorite_num || 0 }}</span>
          </el-button>
        </div>
      </el-card>

      <!-- 评论区板块 -->
      <el-card shadow="never" class="comment-card">
        <template #header>
          <div class="comment-header">
            <h3>评论区 ({{ detail.comment_num || 0 }})</h3>
          </div>
        </template>
        
        <!-- 评论输入框 -->
        <div class="comment-input-section">
          <el-input
            v-model="commentText"
            type="textarea"
            :rows="3"
            placeholder="写下你的评论..."
            maxlength="255"
            show-word-limit
          />
          <div class="comment-submit">
            <el-button
              type="primary"
              @click="handleSubmitComment"
              :loading="commentLoading"
              :disabled="!commentText.trim()"
            >
              发表评论
            </el-button>
          </div>
        </div>

        <!-- 评论列表 -->
        <div class="comment-list">
          <div v-if="commentsLoading" class="loading-comments">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="comments.length === 0" class="empty-comments">
            <el-empty description="暂无评论" :image-size="80" />
          </div>
          <div v-else class="comments">
            <div
              v-for="comment in comments"
              :key="comment.comment_id || `${comment.user_id}-${comment.created_at}`"
              class="comment-item"
            >
              <div class="comment-avatar">
                <el-avatar :size="40">{{ comment.user_name?.charAt(0) || 'U' }}</el-avatar>
              </div>
              <div class="comment-content">
                <div class="comment-header-info">
                  <span class="comment-user">{{ comment.user_name || '匿名用户' }}</span>
                  <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.comment_content }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
    <el-empty v-else description="暂无项目详情" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Link, Message, Download, Star, StarFilled, Collection, CollectionTag } from '@element-plus/icons-vue'
import { downloadFile, getProjectDetail } from '@/api/project'
import { likePost, unlikePost, favoritePost, unfavoritePost, commentPost, getComments } from '@/api/post'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const props = defineProps({
  detail: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['apply', 'message', 'update:detail'])

const userStore = useUserStore()
const commentText = ref('')
const comments = ref([])
const likeLoading = ref(false)
const favoriteLoading = ref(false)
const commentLoading = ref(false)
const commentsLoading = ref(false)

// 监听detail变化，加载评论
watch(() => props.detail?.post_id, (postId) => {
  if (postId) {
    loadComments()
  }
}, { immediate: true })

onMounted(() => {
  if (props.detail?.post_id) {
    loadComments()
  }
})

const getTitle = () => {
  if (!props.detail) return ''
  if (props.detail.post_type === 'research') {
    return props.detail.research_name
  } else if (props.detail.post_type === 'competition') {
    return props.detail.competition_name
  } else if (props.detail.post_type === 'personal') {
    // 个人技能项目：专业 - 发布人名称
    return `${props.detail.major} - ${getPublisherName()}`
  }
  return ''
}

const getPublisherName = () => {
  if (!props.detail) return ''
  if (props.detail.post_type === 'research' || props.detail.post_type === 'competition') {
    return props.detail.teacher_name || '未知'
  } else if (props.detail.post_type === 'personal') {
    return props.detail.student_name || '未知'
  }
  return ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const getSkillDegreeText = (value) => {
  const map = {
    'skillful': '熟练',
    'known': '了解'
  }
  return map[value] || value || '未知'
}

const getExpectWorktypeText = (value) => {
  const map = {
    'research': '科研',
    'competition': '大创',
    'innovation': '竞赛'
  }
  return map[value] || value || '未知'
}

const getFilterText = (value) => {
  const map = {
    'all': '所有项目',
    'cross': '可接受跨方向合作',
    'local': '优先本地项目'
  }
  return map[value] || value || '未知'
}

const getCompetitionTypeText = (value) => {
  const map = {
    'IETP': '大创项目',
    'AC': '学科竞赛',
    'CC': '企业合作竞赛'
  }
  return map[value] || value || '未知'
}

const getGuideWayText = (value) => {
  const map = {
    'online': '线上',
    'offline': '线下'
  }
  return map[value] || value || '未知'
}

const handleApply = () => {
  emit('apply')
}

const handleMessage = () => {
  emit('message')
}

const handleDownload = async (url) => {
  try {
    await downloadFile(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const getAttachmentUrl = (downloadUrl) => {
  if (!downloadUrl) return '#'
  // 如果URL已经包含/api，直接使用；否则添加/api前缀
  if (downloadUrl.startsWith('/api')) {
    return downloadUrl
  } else if (downloadUrl.startsWith('/')) {
    return '/api' + downloadUrl
  } else {
    return '/api/' + downloadUrl
  }
}

const handleDownloadAttachment = async (attachment) => {
  if (!attachment.download_url) {
    ElMessage.error('附件下载链接不存在')
    return
  }
  
  try {
    // 直接打开下载链接
    const url = getAttachmentUrl(attachment.download_url)
    window.open(url, '_blank')
  } catch (error) {
    ElMessage.error('下载失败')
    console.error(error)
  }
}

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatMajor = (major) => {
  if (!major) return ''
  if (Array.isArray(major)) {
    return major.length > 0 ? major.join('、') : ''
  }
  return major
}

const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  
  if (!props.detail?.post_id) return
  
  likeLoading.value = true
  try {
    if (props.detail.is_liked) {
      await unlikePost({ post_id: props.detail.post_id })
      props.detail.is_liked = false
      props.detail.like_num = Math.max(0, (props.detail.like_num || 0) - 1)
      ElMessage.success('取消点赞成功')
    } else {
      await likePost({ post_id: props.detail.post_id })
      props.detail.is_liked = true
      props.detail.like_num = (props.detail.like_num || 0) + 1
      ElMessage.success('点赞成功')
    }
    emit('update:detail', props.detail)
  } catch (error) {
    ElMessage.error(props.detail.is_liked ? '取消点赞失败' : '点赞失败')
    console.error(error)
  } finally {
    likeLoading.value = false
  }
}

const handleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  
  if (!props.detail?.post_id) return
  
  favoriteLoading.value = true
  try {
    if (props.detail.is_favorited) {
      await unfavoritePost({ post_id: props.detail.post_id })
      props.detail.is_favorited = false
      props.detail.favorite_num = Math.max(0, (props.detail.favorite_num || 0) - 1)
      ElMessage.success('取消收藏成功')
    } else {
      await favoritePost({ post_id: props.detail.post_id })
      props.detail.is_favorited = true
      props.detail.favorite_num = (props.detail.favorite_num || 0) + 1
      ElMessage.success('收藏成功')
    }
    emit('update:detail', props.detail)
  } catch (error) {
    ElMessage.error(props.detail.is_favorited ? '取消收藏失败' : '收藏失败')
    console.error(error)
  } finally {
    favoriteLoading.value = false
  }
}

const handleSubmitComment = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  
  if (!commentText.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }
  
  if (!props.detail?.post_id) return
  
  commentLoading.value = true
  try {
    await commentPost({
      post_id: props.detail.post_id,
      comment: commentText.value.trim()
    })
    ElMessage.success('评论成功')
    commentText.value = ''
    // 重新加载评论列表
    await loadComments()
    // 更新评论数
    props.detail.comment_num = (props.detail.comment_num || 0) + 1
    emit('update:detail', props.detail)
  } catch (error) {
    ElMessage.error('评论失败')
    console.error(error)
  } finally {
    commentLoading.value = false
  }
}

const loadComments = async () => {
  if (!props.detail?.post_id) return
  
  commentsLoading.value = true
  try {
    const response = await getComments(props.detail.post_id)
    if (response.code === 200) {
      comments.value = response.data || []
    }
  } catch (error) {
    console.error('加载评论失败:', error)
    comments.value = []
  } finally {
    commentsLoading.value = false
  }
}
</script>

<style scoped>
.project-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  border-radius: 12px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  padding: 20px 0;
}

.action-bar {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
}

.action-bar .el-button {
  flex: 1;
}

.action-bar .count {
  margin-left: 8px;
  font-weight: 600;
}

.comment-card {
  border-radius: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.comment-input-section {
  margin-bottom: 20px;
}

.comment-submit {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.comment-list {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

.loading-comments {
  padding: 20px;
}

.empty-comments {
  padding: 40px 20px;
}

.comments {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: background 0.3s;
}

.comment-item:hover {
  background: #f0f2f5;
}

.comment-avatar {
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.comment-user {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-text {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.no-tags {
  color: #909399;
  font-size: 14px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-size {
  color: #909399;
  font-size: 12px;
}

.project-experience-text {
  color: #606266;
}

.no-experience {
  color: #909399;
}
</style>
