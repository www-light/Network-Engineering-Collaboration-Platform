<template>
  <div class="login-container">
    <div class="login-background">
      <div class="login-card-wrapper">
        <el-card class="login-card" shadow="always">
          <template #header>
            <div class="card-header">
              <h2>
                <el-icon><UserFilled /></el-icon>
                登录
              </h2>
            </div>
          </template>
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="80px"
            @submit.prevent="handleLogin"
          >
            <el-form-item label="身份" prop="identity">
              <el-radio-group v-model="form.identity"
              data-testid="identity-select">
                <el-radio :label="0">
                  <el-icon><User /></el-icon>
                  学生
                </el-radio>
                <el-radio :label="1">
                  <el-icon><Avatar /></el-icon>
                  教师
                </el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="账号" prop="account">
              <el-input
                v-model="form.account"
                placeholder="请输入学号/教工号"
                clearable
                size="large"
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
                clearable
                size="large"
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                size="large"
                style="width: 100%"
              >
                登录
              </el-button>
            </el-form-item>
            <el-form-item>
              <div class="register-link">
                还没有账号？
                <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'
import { UserFilled, User, Avatar, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  identity: 0,
  account: '',
  password: ''
})

const rules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.loginUser(form)
        const redirect = route.query.redirect || '/'
        router.push(redirect)
      } catch (error) {
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-background {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card-wrapper {
  width: 100%;
  max-width: 480px;
}

.login-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 24px;
}

.register-link {
  text-align: center;
  width: 100%;
  color: #606266;
  font-size: 14px;
}
</style>

