<template>
  <div class="register-container">
    <div class="register-background">
      <div class="register-card-wrapper">
        <el-card class="register-card" shadow="always">
          <template #header>
            <div class="card-header">
              <h2>
                <el-icon><UserFilled /></el-icon>
                注册
              </h2>
            </div>
          </template>
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="100px"
            @submit.prevent="handleRegister"
          >
            <el-form-item label="身份" prop="identity">
              <el-radio-group v-model="form.identity" @change="handleIdentityChange">
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
                :placeholder="form.identity === 0 ? '请输入学号' : '请输入教工号'"
                clearable
                size="large"
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="姓名" prop="name">
              <el-input
                v-model="form.name"
                placeholder="请输入姓名"
                clearable
                size="large"
              >
                <template #prefix>
                  <el-icon><Edit /></el-icon>
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
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                show-password
                clearable
                size="large"
                @keyup.enter="handleRegister"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item
              v-if="form.identity === 0"
              label="年级"
              prop="extra.grade"
            >
              <el-input
                v-model="form.extra.grade"
                placeholder="请输入年级"
                clearable
                size="large"
              />
            </el-form-item>
            <el-form-item
              v-if="form.identity === 1"
              label="职称"
              prop="extra.title"
            >
              <el-input
                v-model="form.extra.title"
                placeholder="请输入职称"
                clearable
                size="large"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="handleRegister"
                :loading="loading"
                size="large"
                style="width: 100%"
              >
                注册
              </el-button>
            </el-form-item>
            <el-form-item>
              <div class="login-link">
                已有账号？
                <el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
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
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { UserFilled, User, Avatar, Lock, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  identity: 0,
  account: '',
  name: '',
  password: '',
  confirmPassword: '',
  extra: {
    grade: '',
    title: ''
  }
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  account: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  'extra.grade': [
    { required: true, message: '请输入年级', trigger: 'blur' }
  ],
  'extra.title': [
    { required: true, message: '请输入职称', trigger: 'blur' }
  ]
}

const handleIdentityChange = () => {
  form.extra.grade = ''
  form.extra.title = ''
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const registerData = {
          identity: form.identity,
          account: form.account,
          name: form.name,
          password: form.password,
          extra: form.identity === 0
            ? { grade: form.extra.grade }
            : { title: form.extra.title }
        }
        await userStore.registerUser(registerData)
        router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-background {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-card-wrapper {
  width: 100%;
  max-width: 560px;
}

.register-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
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

.login-link {
  text-align: center;
  width: 100%;
  color: #606266;
  font-size: 14px;
}
</style>

