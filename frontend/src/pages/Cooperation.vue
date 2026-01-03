<template>
  <div class="cooperation-container">
    <div class="cooperation-header">
      <h2>
        <el-icon><Link /></el-icon>
        合作流程
      </h2>
      <el-button type="primary" @click="handleCheckUnfinished">
        <el-icon><Search /></el-icon>
        检查未完成流程
      </el-button>
    </div>

    <el-skeleton v-if="loading" :rows="3" animated />

    <div v-else-if="cooperations.length > 0" class="cooperation-grid">
      <el-card
        v-for="coop in cooperations"
        :key="coop.cooperation_id"
        shadow="hover"
        class="cooperation-card"
      >
        <!-- 卡片头部：项目名称和状态标签 -->
        <template #header>
          <div class="card-header">
            <h4 class="project-name">{{ coop.post_name }}</h4>
            <el-tag :type="getStatusType(coop.status)" effect="light" size="small">
              {{ getStatusText(coop.status) }}
            </el-tag>
          </div>
        </template>

        <!-- 卡片内容：双方信息 -->
        <div class="card-content">
          <div class="info-row">
            <span class="label">教师：</span>
            <span class="value">{{ coop.teacher_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">学生：</span>
            <span class="value">{{ coop.student_name }}</span>
          </div>
          <div class="role-badge">
            <el-tag
              :type="coop.role === 0 ? 'info' : 'success'"
              size="small"
            >
              {{ coop.role === 0 ? '邀请' : '申请' }}
            </el-tag>
          </div>
        </div>

        <!-- 时间戳 -->
        <div class="timestamp">
          <span v-if="coop.confirmed_at">
            确认时间：{{ formatDate(coop.confirmed_at) }}
          </span>
          <span v-else>
            发起时间：{{ formatDate(coop.created_at) }}
          </span>
        </div>

        <!-- 操作按钮 -->
        <template #footer>
          <div class="card-footer">
            <div v-if="coop.status === 2" class="action-buttons">
              <!-- 待确认状态：根据角色显示不同按钮 -->
              <el-button
                v-if="canApprove(coop)"
                type="success"
                size="small"
                @click="handleApprove(coop)"
              >
                <el-icon><Check /></el-icon>
                同意
              </el-button>
              <el-button
                v-if="canReject(coop)"
                type="danger"
                size="small"
                @click="handleReject(coop)"
              >
                <el-icon><Close /></el-icon>
                拒绝
              </el-button>
              <el-button
                v-if="canCancel(coop)"
                type="info"
                size="small"
                @click="handleCancel(coop)"
              >
                <el-icon><Delete /></el-icon>
                取消
              </el-button>
            </div>
            <div v-else class="status-button">
              <!-- 已完成/已拒绝/已取消状态 -->
              <el-button
                :type="getStatusType(coop.status)"
                size="small"
                disabled
              >
                {{ getStatusText(coop.status) }}
              </el-button>
            </div>
          </div>
        </template>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="暂无合作流程" />

    <!-- 分页控件 -->
    <div v-if="cooperations.length > 0" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import {
  listCooperations,
  checkUnfinished,
  approveApplication,
  rejectApplication,
  rejectInvitation,
  agreeInvite,
  cancelApply,
  cancelInvite
} from '@/api/cooperation'
import {
  Link,
  Search,
  Check,
  Close,
  Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const cooperations = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const totalPages = ref(0)

// 计算用户是否是教师/学生
const userInfo = computed(() => userStore.userInfo)
const isTeacher = computed(() => userInfo.value?.identity === 1)
const isStudent = computed(() => userInfo.value?.identity === 0)

onMounted(() => {
  loadCooperations()
})

const loadCooperations = async () => {
  loading.value = true
  try {
    const response = await listCooperations(currentPage.value, pageSize.value)
    console.log('合作流程数据:', response) // 调试用
    // 后端直接返回数据对象，不需要 .data
    cooperations.value = response.results || []
    total.value = response.count || 0
    totalPages.value = response.total_pages || 0
  } catch (error) {
    console.error('获取合作流程失败:', error)
    ElMessage.error('获取合作流程失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (newPage) => {
  currentPage.value = newPage
  loadCooperations()
}

const handlePageSizeChange = (newPageSize) => {
  pageSize.value = newPageSize
  currentPage.value = 1
  loadCooperations()
}

const handleCheckUnfinished = async () => {
  try {
    const response = await checkUnfinished()
    // 后端直接返回数据对象，不需要 .data
    if (response.has_unfinished) {
      ElMessage.warning('存在未完成的合作流程')
      await loadCooperations()
    } else {
      ElMessage.success('没有未完成的合作流程')
    }
  } catch (error) {
    ElMessage.error('检查失败')
    console.error(error)
  }
}

// 判断是否显示"同意"按钮（只有接收方能同意）
const canApprove = (coop) => {
  if (coop.status !== 2) return false
  
  // role=0: 邀请（教师发起，学生接收） - 学生可以同意
  // role=1: 申请（学生发起，教师接收） - 教师可以同意
  if (coop.role === 0) {
    return isStudent.value // 邀请由学生同意
  } else {
    return isTeacher.value // 申请由教师同意
  }
}

// 判断是否显示"拒绝"按钮（只有接收方能拒绝）
const canReject = (coop) => {
  if (coop.status !== 2) return false
  
  // role=0: 邀请（教师发起，学生接收） - 学生可以拒绝
  // role=1: 申请（学生发起，教师接收） - 教师可以拒绝
  if (coop.role === 0) {
    return isStudent.value // 邀请由学生拒绝
  } else {
    return isTeacher.value // 申请由教师拒绝
  }
}

// 判断是否显示"取消"按钮（只有发起方能取消）
const canCancel = (coop) => {
  if (coop.status !== 2) return false
  
  // role=0: 邀请（教师发起） - 教师可以取消
  // role=1: 申请（学生发起） - 学生可以取消
  if (coop.role === 0) {
    return isTeacher.value // 邀请由教师取消
  } else {
    return isStudent.value // 申请由学生取消
  }
}

const handleApprove = async (coop) => {
  try {
    await ElMessageBox.confirm('确定要同意此合作吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 根据角色判断调用哪个API
    if (coop.role === 0) {
      // 邀请：学生同意邀请
      await agreeInvite({ cooperation_id: coop.cooperation_id })
    } else {
      // 申请：教师批准申请
      await approveApplication({ cooperation_id: coop.cooperation_id })
    }

    ElMessage.success('已同意合作')
    await loadCooperations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const handleReject = async (coop) => {
  try {
    await ElMessageBox.confirm('确定要拒绝此合作吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 根据角色调用对应的拒绝API
    if (coop.role === 0) {
      // 邀请：学生拒绝邀请
      await rejectInvitation({ cooperation_id: coop.cooperation_id })
    } else {
      // 申请：教师拒绝申请
      await rejectApplication({ cooperation_id: coop.cooperation_id })
    }

    ElMessage.success('已拒绝')
    await loadCooperations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const handleCancel = async (coop) => {
  try {
    await ElMessageBox.confirm('确定要取消此合作吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 根据角色调用对应的取消API
    if (coop.role === 0) {
      // 邀请：取消邀请
      await cancelInvite({ cooperation_id: coop.cooperation_id })
    } else {
      // 申请：取消申请
      await cancelApply({ cooperation_id: coop.cooperation_id })
    }

    ElMessage.success('已取消')
    await loadCooperations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  const map = {
    2: 'warning',    // 待确认
    3: 'success',    // 已确认
    4: 'danger',     // 被拒绝
    5: 'info'        // 已取消
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    2: '待双方确认',
    3: '已确认合作',
    4: '被拒绝',
    5: '已取消'
  }
  return map[status] || '未知'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '---'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.cooperation-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.cooperation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.cooperation-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.cooperation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cooperation-card {
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.cooperation-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.project-name {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
  word-break: break-word;
  max-height: 3em;
  overflow: hidden;
}

.card-content {
  margin-bottom: 16px;
  padding: 0;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-row:last-of-type {
  margin-bottom: 8px;
}

.label {
  color: #909399;
  min-width: 50px;
  font-weight: 500;
}

.value {
  color: #303133;
  flex: 1;
  word-break: break-all;
}

.role-badge {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.timestamp {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  padding: 8px 0;
  border-top: 1px solid #ebeef5;
}

.card-footer {
  padding: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 70px;
}

.status-button {
  display: flex;
}

.status-button .el-button {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cooperation-container {
    padding: 12px;
  }

  .cooperation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .cooperation-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
  }

  .cooperation-header h2 {
    font-size: 20px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
    flex: none;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}
</style>

