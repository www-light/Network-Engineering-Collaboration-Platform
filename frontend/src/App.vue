<template>
  <div id="app">
    <el-container v-if="showHeader" class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="logo">
            <el-icon><Connection /></el-icon>
            网络工程协作平台
          </h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            :router="true"
            class="header-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/projects">
              <el-icon><Document /></el-icon>
              <span>项目列表</span>
            </el-menu-item>
            <el-menu-item v-if="userStore.isLoggedIn" @click="handlePublishClick">
              <el-icon><Plus /></el-icon>
              <span>发布项目</span>
            </el-menu-item>
            <el-menu-item v-if="userStore.isLoggedIn" index="/cooperation">
              <el-icon><Link /></el-icon>
              <span>合作流程</span>
            </el-menu-item>
            <el-menu-item v-if="userStore.isLoggedIn" index="/message">
              <el-icon><Message /></el-icon>
              <span>站内私信</span>
            </el-menu-item>
            <el-menu-item v-if="userStore.isLoggedIn" index="/profile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
            <el-menu-item v-if="!userStore.isLoggedIn" index="/login">
              <el-icon><UserFilled /></el-icon>
              <span>登录</span>
            </el-menu-item>
            <el-menu-item v-else @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessageBox, ElMessage } from 'element-plus'
import { checkUnfinished } from '@/api/cooperation'
import {
  House,
  Document,
  Plus,
  Link,
  Message,
  User,
  UserFilled,
  SwitchButton,
  Connection
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showHeader = computed(() => {
  return route.name !== 'Login' && route.name !== 'Register'
})

const activeMenu = computed(() => {
  return route.path
})

const handlePublishClick = async () => {
  try {
    const response = await checkUnfinished()
    if (response.has_unfinished) {
      ElMessage.error('存在未完成的合作流程，请先完成后再发布')
      return
    }
    router.push('/publish')
  } catch (error) {
    console.error('检查合作流程失败:', error)
    ElMessage.error('检查合作流程失败')
  }
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
.app-container {
  min-height: 100vh;
  background: #f8fafc;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 100%;
}

.logo {
  color: white;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-menu {
  background: transparent;
  border: none;
}

.header-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.9);
  border-bottom: 2px solid transparent;
}

.header-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.header-menu :deep(.el-menu-item.is-active) {
  color: white;
  border-bottom-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.app-main {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
</style>
