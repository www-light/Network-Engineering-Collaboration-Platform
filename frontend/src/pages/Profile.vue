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
        <!-- 加载中 -->
        <el-skeleton v-if="loading" :rows="10" animated />
        
        <!-- 内容区 -->
        <div v-else>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">
              {{ profileData?.user_id }}
            </el-descriptions-item>
            <el-descriptions-item label="身份">
              <el-tag :type="profileData?.identity === 1 ? 'success' : 'info'" effect="light">
                {{ profileData?.identity === 1 ? '教师' : '学生' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="账号">
              {{ profileData?.account }}
            </el-descriptions-item>
            <el-descriptions-item label="姓名">
              {{ profileData?.name }}
            </el-descriptions-item>
            <!-- 学生专有字段 -->
            <el-descriptions-item v-if="profileData?.identity === 0" label="年级">
              {{ getGradeName(profileData?.extra?.grade) }}
            </el-descriptions-item>
            <!-- 教师专有字段 -->
            <template v-if="profileData?.identity === 1">
              <el-descriptions-item label="职称">
                {{ profileData?.extra?.title }}
              </el-descriptions-item>
              <el-descriptions-item label="组队成功率">
                <el-progress 
                  :percentage="profileData?.success_rate || 0"
                  :color="getSuccessRateColor(profileData?.success_rate)"
                  :stroke-width="8"
                />
                <span class="stat-text">{{ profileData?.approved_cooperations }}/{{ profileData?.total_cooperations }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="往期指导成果" :span="2">
                <div class="achievements-display" v-if="!editingAchievements">
                  <p v-if="profileData?.past_achievements">{{ profileData?.past_achievements }}</p>
                  <p v-else class="placeholder">暂无成果信息</p>
                </div>
                <el-input
                  v-else
                  v-model="editedAchievements"
                  type="textarea"
                  :rows="5"
                  placeholder="输入往期指导成果..."
                />
              </el-descriptions-item>
            </template>
          </el-descriptions>

          <div class="profile-actions">
            <!-- 教师编辑成果按钮 -->
            <el-button 
              v-if="profileData?.identity === 1"
              :type="editingAchievements ? 'success' : 'primary'"
              @click="toggleEditAchievements"
            >
              <el-icon><Edit /></el-icon>
              {{ editingAchievements ? '保存成果' : '编辑成果' }}
            </el-button>
            <el-button v-if="editingAchievements" @click="cancelEditAchievements">
              <el-icon><CloseBold /></el-icon>
              取消编辑
            </el-button>
            <el-button @click="handleChangePassword">
              <el-icon><Lock /></el-icon>
              修改密码
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { useRouter } from 'vue-router'
import { User, Edit, Lock, CloseBold } from '@element-plus/icons-vue'
import { getUserProfile, updateUserProfile } from '@/api/auth'
import { ElMessageBox, ElMessage } from 'element-plus'

// 定义组件名
defineOptions({
  name: 'UserProfile'
})

const userStore = useUserStore()
const router = useRouter()

const profileData = ref(null)
const loading = ref(false)
const editingAchievements = ref(false)
const editedAchievements = ref('')

const gradeMap = {
  1: '大一',
  2: '大二',
  3: '大三',
  4: '大四'
}

const getGradeName = (grade) => {
  return gradeMap[grade] || '未知'
}

const getSuccessRateColor = (rate) => {
  if (rate >= 80) return '#67c23a'
  if (rate >= 60) return '#e6a23c'
  return '#f56c6c'
}

onMounted(async () => {
  await loadProfile()
})

const loadProfile = async () => {
  loading.value = true
  try {
    const response = await getUserProfile()
    if (response.code === 200) {
      profileData.value = response.data
      editedAchievements.value = response.data?.past_achievements || ''
    } else {
      ElMessage.error(response.msg || '获取资料失败')
    }
  } catch (error) {
    ElMessage.error('获取资料失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const toggleEditAchievements = async () => {
  if (editingAchievements.value) {
    // 保存成果
    try {
      const response = await updateUserProfile({
        past_achievements: editedAchievements.value
      })
      if (response.code === 200) {
        profileData.value = response.data
        editingAchievements.value = false
        ElMessage.success('保存成功')
      } else {
        ElMessage.error(response.msg || '保存失败')
      }
    } catch (error) {
      ElMessage.error('保存失败')
      console.error(error)
    }
  } else {
    editingAchievements.value = true
  }
}

const cancelEditAchievements = () => {
  editingAchievements.value = false
  editedAchievements.value = profileData.value?.past_achievements || ''
}

const handleChangePassword = () => {
  ElMessageBox.alert('修改密码功能待实现', '提示', {
    confirmButtonText: '确定'
  })
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    userStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}
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

.achievements-display {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 100px;
  white-space: pre-wrap;
  word-break: break-word;
}

.placeholder {
  color: #909399;
  margin: 0;
}

.stat-text {
  margin-left: 12px;
  color: #606266;
  font-size: 14px;
}

.profile-actions {
  margin-top: 30px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>

