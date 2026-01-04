<template>
  <div class="profile-container">
    <el-card shadow="never" class="profile-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><User /></el-icon>
            个人中心
          </h2>
        </div>
      </template>
      <div class="profile-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">
            {{ userStore.userInfo?.user_id }}
          </el-descriptions-item>
          <el-descriptions-item label="身份">
            <el-tag :type="userStore.isTeacher ? 'success' : 'info'" effect="light">
              {{ userStore.isTeacher ? '教师' : '学生' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="账号">
            {{ userStore.userInfo?.account }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ userStore.userInfo?.name || '未设置' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="profile-actions">
          <el-button type="primary" @click="handleEdit">
            <el-icon><Edit /></el-icon>
            编辑资料
          </el-button>
          <el-button @click="handleChangePassword">
            <el-icon><Lock /></el-icon>
            修改密码
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户发布项目列表 -->
    <el-card shadow="never" class="projects-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Document /></el-icon>
            我发布的项目
          </h2>
        </div>
      </template>
      <div class="projects-content">
        <div v-if="projectsLoading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else-if="userProjects.length === 0" class="empty-container">
          <el-empty description="暂无发布的项目" :image-size="100" />
        </div>
        <div v-else class="projects-list">
          <ProjectCard
            v-for="project in userProjects"
            :key="project.post_id"
            :project="project"
            :is-active="selectedProjectId === project.post_id"
            @click="() => handleProjectClick(project)"
          />
        </div>
      </div>
    </el-card>

    <!-- 项目详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      @close="handleCloseDetail"
      :show-close="false"
      destroy-on-close
      class="project-detail-dialog"
    >
      <template #header="{ close }">
        <div class="dialog-header">
          <span class="dialog-title">项目详情</span>
          <el-button
            type="text"
            @click="handleCloseDetail"
            class="close-button"
            :icon="Close"
            circle
            size="large"
          />
        </div>
      </template>
      <ProjectDetail
        :detail="currentDetail"
        :loading="detailLoading"
        :like-loading="likeLoading"
        :favorite-loading="favoriteLoading"
        :comment-loading="commentLoading"
        :show-actions="false"
        :readonly="true"
        :allow-edit-recruit-status="true"
        @apply="handleApply"
        @message="handleMessage"
        @like="handleLike"
        @favorite="handleFavorite"
        @comment="handleComment"
        @update:detail="handleDetailUpdate"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { User, Edit, Lock, Document, Close } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getProjects, getProjectDetail } from '@/api/project'
import { likePost, unlikePost, favoritePost, unfavoritePost, commentPost } from '@/api/post'
import ProjectCard from '@/components/ProjectCard.vue'
import ProjectDetail from '@/components/ProjectDetail.vue'

const userStore = useUserStore()

const userProjects = ref([])
const projectsLoading = ref(false)
const selectedProjectId = ref(null)
const showDetailDialog = ref(false)
const currentDetail = ref(null)
const detailLoading = ref(false)
const likeLoading = ref(false)
const favoriteLoading = ref(false)
const commentLoading = ref(false)

// 加载用户发布的项目
const loadUserProjects = async () => {
  if (!userStore.userInfo?.user_id) return
  
  projectsLoading.value = true
  try {
    const response = await getProjects({
      user_id: userStore.userInfo.user_id,
      page: 1,
      page_size: 100
    })
    
    if (response.code === 200 && response.data) {
      userProjects.value = response.data.items || []
    } else {
      userProjects.value = []
      ElMessage.warning(response.msg || '获取项目列表失败')
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    userProjects.value = []
    ElMessage.error('获取项目列表失败')
  } finally {
    projectsLoading.value = false
  }
}

// 点击项目卡片
const handleProjectClick = async (project) => {
  selectedProjectId.value = project.post_id
  // 先重置状态
  currentDetail.value = null
  detailLoading.value = true
  // 打开弹窗
  showDetailDialog.value = true
  
  try {
    const response = await getProjectDetail(project.post_id)
    if (response.code === 200 && response.data) {
      currentDetail.value = response.data
    } else {
      ElMessage.error(response.msg || '获取项目详情失败')
      // 不关闭弹窗，让用户看到错误信息
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败: ' + (error.message || '未知错误'))
    // 不关闭弹窗，让用户看到错误信息
  } finally {
    detailLoading.value = false
  }
}

// 关闭详情弹窗
const handleCloseDetail = () => {
  showDetailDialog.value = false
  selectedProjectId.value = null
  currentDetail.value = null
}

// 申请/邀请
const handleApply = () => {
  ElMessage.info('申请/邀请功能')
}

// 私信
const handleMessage = () => {
  ElMessage.info('私信功能')
}

// 点赞（只显示数据，不执行操作）
// 点赞数和收藏数已从 getProjectDetail 接口获取并显示在 currentDetail 中
const handleLike = () => {
  // 不执行任何操作，仅用于占位
  // 点赞数和收藏数会从 currentDetail.value.like_num 和 currentDetail.value.favorite_num 中显示
  return
}

// 收藏（只显示数据，不执行操作）
// 点赞数和收藏数已从 getProjectDetail 接口获取并显示在 currentDetail 中
const handleFavorite = () => {
  // 不执行任何操作，仅用于占位
  // 点赞数和收藏数会从 currentDetail.value.like_num 和 currentDetail.value.favorite_num 中显示
  return
}

// 评论（只显示评论内容，不执行评论操作）
// 评论内容已从 getProjectDetail 接口获取并显示在 currentDetail 中
const handleComment = () => {
  // 不执行任何操作，仅用于占位
  // 评论列表会从 ProjectDetail 组件内部通过 getComments 接口加载并显示
  return
}

// 处理详情更新（包括招募状态更新）
const handleDetailUpdate = (updatedDetail) => {
  currentDetail.value = updatedDetail
  // 更新列表中的项目信息
  const projectIndex = userProjects.value.findIndex(p => p.post_id === updatedDetail.post_id)
  if (projectIndex !== -1) {
    userProjects.value[projectIndex] = {
      ...userProjects.value[projectIndex],
      recruit_status: updatedDetail.recruit_status
    }
  }
}

const handleEdit = () => {
  ElMessageBox.alert('编辑资料功能待实现', '提示', {
    confirmButtonText: '确定'
  })
}

const handleChangePassword = () => {
  ElMessageBox.alert('修改密码功能待实现', '提示', {
    confirmButtonText: '确定'
  })
}

onMounted(() => {
  loadUserProjects()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
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

.profile-content {
  padding: 20px 0;
}

.profile-actions {
  margin-top: 30px;
  display: flex;
  gap: 12px;
}

.projects-card {
  border-radius: 12px;
  background: white;
}

.projects-content {
  padding: 20px 0;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 20px;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 0;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.close-button {
  font-size: 20px;
  color: #909399;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #409eff;
  background-color: #f0f2f5;
}

:deep(.project-detail-dialog) {
  .el-dialog__body {
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
  }
}
</style>

