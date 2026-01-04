<template>
  <div class="project-list-container">
    <el-container class="list-layout">
      <!-- 左侧项目列表 -->
      <el-aside width="400px" class="list-aside">
        <el-card shadow="never" class="aside-card">
          <template #header>
            <div class="aside-header">
              <h3>项目列表</h3>
              <el-select
                v-model="selectedDirection"
                placeholder="筛选方向"
                size="small"
                style="width: 150px"
                @change="handleDirectionChange"
              >
                <el-option label="全部" value="all" />
                <el-option label="科研项目" value="research" />
                <el-option label="大创/竞赛" value="competition" />
                <el-option label="个人技能" value="personal" />
              </el-select>
            </div>
          </template>
          <div class="card-body-wrapper">
            <!-- 搜索框 -->
            <div class="search-container">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索项目..."
                clearable
                @input="handleSearch"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <el-icon><i class="fa fa-search"></i></el-icon>
                </template>
              </el-input>
            </div>
            <div class="project-list">
              <div v-if="projectStore.loading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="filteredProjects.length === 0" class="empty-container">
                <el-empty description="暂无项目" />
              </div>
              <ProjectCard
                v-else
                v-for="project in filteredProjects"
                :key="project.post_id"
                :project="project"
                :is-active="selectedProjectId === project.post_id"
                @click="handleProjectClick(project)"
              />
            </div>
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                :total="total"
                layout="total, sizes, prev, pager, next"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
              />
            </div>
          </div>
        </el-card>
      </el-aside>

      <!-- 右侧详情面板 -->
      <el-main class="detail-main">
        <ProjectDetail
          :detail="currentDetail"
          :loading="detailLoading"
          :like-loading="likeLoading"
          :favorite-loading="favoriteLoading"
          :comment-loading="commentLoading"
          @apply="handleApply"
          @message="handleMessage"
          @like="handleLike"
          @favorite="handleFavorite"
          @comment="handleSubmitComment"
          @update:detail="handleDetailUpdate"
        />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/store/project'
import { getProjectDetail } from '@/api/project'
import { applyAndInvite } from '@/api/cooperation'
import { createConversation } from '@/api/conversation'
import { likePost, unlikePost, favoritePost, unfavoritePost, commentPost } from '@/api/post'
import { useUserStore } from '@/store/user'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectDetail from '@/components/ProjectDetail.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const projectStore = useProjectStore()
const userStore = useUserStore()

const selectedDirection = ref('all')
const selectedProjectId = ref(null)
const currentDetail = ref(null)
const detailLoading = ref(false)
const likeLoading = ref(false)
const favoriteLoading = ref(false)
const commentLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')

// 使用store中的项目和分页信息
const filteredProjects = computed(() => projectStore.projects)
const total = computed(() => projectStore.total)

onMounted(async () => {
  await projectStore.fetchProjects(selectedDirection.value, currentPage.value, pageSize.value, searchKeyword.value)
  if (projectStore.projects.length > 0) {
    handleProjectClick(projectStore.projects[0])
  }
})

const handleSearch = async () => {
  currentPage.value = 1
  await projectStore.fetchProjects(selectedDirection.value, currentPage.value, pageSize.value, searchKeyword.value)
  if (filteredProjects.value.length > 0) {
    handleProjectClick(filteredProjects.value[0])
  } else {
    selectedProjectId.value = null
    currentDetail.value = null
  }
}

const handleDirectionChange = async () => {
  currentPage.value = 1
  await projectStore.fetchProjects(selectedDirection.value, currentPage.value, pageSize.value, searchKeyword.value)
  if (filteredProjects.value.length > 0) {
    handleProjectClick(filteredProjects.value[0])
  } else {
    selectedProjectId.value = null
    currentDetail.value = null
  }
}

const handleProjectClick = async (project) => {
  selectedProjectId.value = project.post_id
  detailLoading.value = true
  
  try {
    const response = await getProjectDetail(project.post_id)
    if (response.code === 200) {
      currentDetail.value = response.data
    } else {
      ElMessage.error(response.msg || '获取项目详情失败')
    }
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

const handleApply = async () => {
  if (!selectedProjectId.value || !currentDetail.value) return
  if (!ensureLoggedIn()) return

  const me = userStore.userInfo
  const isTeacher = me?.identity === 1
  const isStudent = me?.identity === 0
  const isTeacherPost = !!currentDetail.value.teacher_user_id
  const isStudentPost = !!currentDetail.value.student_user_id

  let role
  if (isTeacher && isStudentPost) {
    // 老师对学生发布的信息：邀请
    role = 1
  } else if (isStudent && isTeacherPost) {
    // 学生对老师发布的信息：申请
    role = 0
  } else {
    ElMessage.warning('当前身份与发布者身份相同，无需申请/邀请')
    return
  }

  try {
    await applyAndInvite({
      post_id: selectedProjectId.value,
      role
    })
    ElMessage.success(role === 1 ? '邀请已发送' : '申请已提交')
  } catch (error) {
    // 提取后端返回的具体错误消息
    const errorMsg = error.response?.data?.error || error.message || '操作失败'
    ElMessage.error(errorMsg)
    console.error(error)
  }
}

const handleMessage = async () => {
  if (!selectedProjectId.value || !currentDetail.value) return
  
  try {
    const receiverId = currentDetail.value.teacher_user_id || userStore.userInfo?.user_id
    
    const response = await createConversation({
      post_id: selectedProjectId.value,
      receiver_id: receiverId
    })
    
    router.push({
      name: 'Message',
      query: { conversationId: response.conversation_id }
    })
  } catch (error) {
    ElMessage.error('创建会话失败')
    console.error(error)
  }
}

const ensureLoggedIn = () => {
  if (!userStore.userInfo?.user_id) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return false
  }
  return true
}

const handleLike = async () => {
  if (!ensureLoggedIn() || !currentDetail.value) return
  
  likeLoading.value = true
  try {
    if (currentDetail.value.is_liked) {
      await unlikePost({ post_id: currentDetail.value.post_id })
      currentDetail.value.is_liked = false
      currentDetail.value.like_num = Math.max(0, (currentDetail.value.like_num || 0) - 1)
      ElMessage.success('取消点赞成功')
    } else {
      await likePost({ post_id: currentDetail.value.post_id })
      currentDetail.value.is_liked = true
      currentDetail.value.like_num = (currentDetail.value.like_num || 0) + 1
      ElMessage.success('点赞成功')
    }
  } catch (error) {
    ElMessage.error(currentDetail.value.is_liked ? '取消点赞失败' : '点赞失败')
    console.error(error)
  } finally {
    likeLoading.value = false
  }
}

const handleFavorite = async () => {
  if (!ensureLoggedIn() || !currentDetail.value) return
  
  favoriteLoading.value = true
  try {
    if (currentDetail.value.is_favorited) {
      await unfavoritePost({ post_id: currentDetail.value.post_id })
      currentDetail.value.is_favorited = false
      currentDetail.value.favorite_num = Math.max(0, (currentDetail.value.favorite_num || 0) - 1)
      ElMessage.success('取消收藏成功')
    } else {
      await favoritePost({ post_id: currentDetail.value.post_id })
      currentDetail.value.is_favorited = true
      currentDetail.value.favorite_num = (currentDetail.value.favorite_num || 0) + 1
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error(currentDetail.value.is_favorited ? '取消收藏失败' : '收藏失败')
    console.error(error)
  } finally {
    favoriteLoading.value = false
  }
}

const handleSubmitComment = async (commentText) => {
  if (!ensureLoggedIn() || !currentDetail.value) return
  
  commentLoading.value = true
  try {
    await commentPost({
      post_id: currentDetail.value.post_id,
      comment: commentText
    })
    ElMessage.success('评论成功')
    currentDetail.value.comment_num = (currentDetail.value.comment_num || 0) + 1
  } catch (error) {
    ElMessage.error('评论失败')
    console.error(error)
  } finally {
    commentLoading.value = false
  }
}

const handleSizeChange = async (size) => {
  pageSize.value = size
  currentPage.value = 1
  await projectStore.fetchProjects(selectedDirection.value, currentPage.value, pageSize.value, searchKeyword.value)
  if (filteredProjects.value.length > 0) {
    handleProjectClick(filteredProjects.value[0])
  } else {
    selectedProjectId.value = null
    currentDetail.value = null
  }
}

const handlePageChange = async (page) => {
  currentPage.value = page
  await projectStore.fetchProjects(selectedDirection.value, currentPage.value, pageSize.value, searchKeyword.value)
  if (filteredProjects.value.length > 0) {
    handleProjectClick(filteredProjects.value[0])
  } else {
    selectedProjectId.value = null
    currentDetail.value = null
  }
}

const handleDetailUpdate = (updatedDetail) => {
  currentDetail.value = updatedDetail
  // 更新列表中的项目信息
  const projectIndex = projectStore.projects.findIndex(p => p.post_id === updatedDetail.post_id)
  if (projectIndex !== -1) {
    projectStore.projects[projectIndex] = {
      ...projectStore.projects[projectIndex],
      like_num: updatedDetail.like_num,
      favorite_num: updatedDetail.favorite_num,
      comment_num: updatedDetail.comment_num
    }
  }
}
</script>

<style scoped>
.project-list-container {
  height: calc(100vh - 100px);
}

.list-layout {
  height: 100%;
  background: #f8fafc;
}

.list-aside {
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

.aside-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  overflow: hidden;
}

.card-body-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.search-container {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.search-container :deep(.el-input) {
  border-radius: 4px;
}

.aside-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.aside-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  min-height: 0; /* 确保flex子元素可以正确收缩 */
}

.loading-container,
.empty-container {
  padding: 20px;
}

.pagination-container {
  flex-shrink: 0; /* 防止分页组件被压缩 */
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.detail-main {
  padding: 20px;
  overflow-y: auto;
  background: white;
}
</style>

