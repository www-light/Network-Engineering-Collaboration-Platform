<template>
  <div class="cooperation-container">
    <el-card shadow="never" class="cooperation-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Link /></el-icon>
            合作流程
          </h2>
          <el-button type="primary" @click="handleCheckUnfinished">
            <el-icon><Search /></el-icon>
            检查未完成流程
          </el-button>
        </div>
      </template>
      <div class="cooperation-content">
        <el-timeline v-if="cooperations.length > 0">
          <el-timeline-item
            v-for="coop in cooperations"
            :key="coop.id"
            :timestamp="coop.time"
            placement="top"
            :color="getStatusColor(coop.status)"
          >
            <el-card shadow="hover" class="cooperation-item-card">
              <div class="cooperation-item">
                <div class="item-header">
                  <h4>{{ coop.title }}</h4>
                  <el-tag :type="getStatusType(coop.status)" size="small" effect="light">
                    {{ coop.status }}
                  </el-tag>
                </div>
                <div class="item-content">
                  <p>{{ coop.description }}</p>
                </div>
                <div class="item-actions" v-if="coop.status === '待确认'">
                  <el-button type="success" size="small" @click="handleConfirm(coop.id)">
                    <el-icon><Check /></el-icon>
                    确认
                  </el-button>
                  <el-button type="danger" size="small" @click="handleReject(coop.id)">
                    <el-icon><Close /></el-icon>
                    拒绝
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无合作流程" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { checkUnfinished, confirmCooperation, rejectCooperation } from '@/api/cooperation'
import { Link, Search, Check, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const cooperations = ref([])
const loading = ref(false)

onMounted(() => {
  loadCooperations()
})

const loadCooperations = async () => {
  loading.value = true
  try {
    // TODO: 调用获取合作流程列表接口
    cooperations.value = []
  } catch (error) {
    console.error('获取合作流程失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCheckUnfinished = async () => {
  try {
    const response = await checkUnfinished()
    if (response.has_unfinished) {
      ElMessage.warning('存在未完成的合作流程')
      loadCooperations()
    } else {
      ElMessage.success('没有未完成的合作流程')
    }
  } catch (error) {
    ElMessage.error('检查失败')
    console.error(error)
  }
}

const handleConfirm = async (coId) => {
  try {
    await ElMessageBox.confirm('确定要确认此合作吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await confirmCooperation(coId)
    ElMessage.success('确认成功')
    loadCooperations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认失败')
      console.error(error)
    }
  }
}

const handleReject = async (coId) => {
  try {
    await ElMessageBox.confirm('确定要拒绝此合作吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await rejectCooperation(coId)
    ElMessage.success('已拒绝')
    loadCooperations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const getStatusType = (status) => {
  const map = {
    '已完成': 'success',
    '待确认': 'warning',
    '已拒绝': 'danger',
    '进行中': 'info'
  }
  return map[status] || 'info'
}

const getStatusColor = (status) => {
  const map = {
    '已完成': '#67c23a',
    '待确认': '#e6a23c',
    '已拒绝': '#f56c6c',
    '进行中': '#409eff'
  }
  return map[status] || '#909399'
}
</script>

<style scoped>
.cooperation-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.cooperation-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cooperation-content {
  padding: 20px 0;
}

.cooperation-item-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.cooperation-item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cooperation-item {
  padding: 8px 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-header h4 {
  margin: 0;
  color: #303133;
}

.item-content {
  margin-bottom: 12px;
  color: #606266;
  line-height: 1.6;
}

.item-actions {
  display: flex;
  gap: 8px;
}
</style>

