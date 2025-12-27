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
  </div>
</template>

<script setup>
import { useUserStore } from '@/store/user'
import { User, Edit, Lock } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const userStore = useUserStore()

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
</style>

