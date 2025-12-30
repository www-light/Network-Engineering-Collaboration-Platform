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
            <div class="project-list">
              <div v-if="projectStore.loading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="filteredProjects.length === 0" class="empty-container">
                <el-empty description="暂无项目" />
              </div>
              <ProjectCard
                v-else
                v-for="project in paginatedProjects"
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
          @apply="handleApply"
          @message="handleMessage"
        />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/store/project'
import { getResearchDetail, getCompetitionDetail } from '@/api/project'
import { applyAndInvite } from '@/api/cooperation'
import { createConversation } from '@/api/conversation'
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
const currentPage = ref(1)
const pageSize = ref(20)

// 由于后端已经支持筛选，这里直接使用store中的projects
const filteredProjects = computed(() => projectStore.projects)

const total = computed(() => filteredProjects.value.length)

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProjects.value.slice(start, end)
})

onMounted(async () => {
  await projectStore.fetchProjects()
  if (projectStore.projects.length > 0) {
    handleProjectClick(projectStore.projects[0])
  }
})

const handleDirectionChange = async () => {
  await projectStore.fetchProjects(selectedDirection.value === 'all' ? null : selectedDirection.value)
  currentPage.value = 1
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
    if (project.post_type === 'research') {
      const detail = await getResearchDetail(project.post_id)
      currentDetail.value = { ...detail, post_type: 'research' }
    } else if (project.post_type === 'competition') {
      const detail = await getCompetitionDetail(project.post_id)
      currentDetail.value = { ...detail, post_type: 'competition' }
    }
  } catch (error) {
    ElMessage.error('获取项目详情失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

const handleApply = async () => {
  if (!selectedProjectId.value) return
  
  try {
    const { value: roleStr } = await ElMessageBox.prompt('请选择角色：0-申请者, 1-邀请者', '申请/邀请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'number',
      inputPlaceholder: '0或1'
    })
    
    const role = parseInt(roleStr || '0')
    await applyAndInvite({
      post_id: selectedProjectId.value,
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
  if (!selectedProjectId.value || !currentDetail.value) return
  
  try {
    const receiverId = currentDetail.value.teacher_id || userStore.userInfo?.user_id
    
    const response = await createConversation({
      post_id: selectedProjectId.value,
      receiver_id: receiverId
    })
    
    router.push(`/message/${response.conversation_id}`)
  } catch (error) {
    ElMessage.error('创建会话失败')
    console.error(error)
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handlePageChange = (page) => {
  currentPage.value = page
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

