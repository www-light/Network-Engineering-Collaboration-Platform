<template>
  <div class="publish-container">
    <el-card shadow="never" class="publish-card">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Plus /></el-icon>
            发布项目
          </h2>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="项目类型" prop="post_type">
          <el-radio-group v-model="form.post_type" @change="handleTypeChange">
            <el-radio label="research">科研项目</el-radio>
            <el-radio label="competition">大创/竞赛</el-radio>
            <el-radio v-if="userStore.isStudent" label="personal">个人项目</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 科研项目表单 -->
        <template v-if="form.post_type === 'research'">
          <el-form-item label="项目名称" prop="research_name">
            <el-input v-model="form.research_name" placeholder="请输入项目名称" />
          </el-form-item>
          <el-form-item label="研究方向" prop="research_direction">
            <el-input v-model="form.research_direction" placeholder="请输入研究方向" />
          </el-form-item>
          <el-form-item label="技术栈" prop="tech_stack">
            <el-input v-model="form.tech_stack" placeholder="请输入技术栈" />
          </el-form-item>
          <el-form-item label="招募人数" prop="recruit_quantity">
            <el-input-number v-model="form.recruit_quantity" :min="1" />
          </el-form-item>
          <el-form-item label="开始时间" prop="starttime">
            <el-date-picker
              v-model="form.starttime"
              type="date"
              placeholder="选择开始时间"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="结束时间" prop="endtime">
            <el-date-picker
              v-model="form.endtime"
              type="date"
              placeholder="选择结束时间"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="预期成果" prop="outcome">
            <el-input
              v-model="form.outcome"
              type="textarea"
              :rows="4"
              placeholder="请输入预期成果"
            />
          </el-form-item>
          <el-form-item label="联系方式" prop="contact">
            <el-input v-model="form.contact" placeholder="请输入联系方式" />
          </el-form-item>
        </template>

        <!-- 大创/竞赛表单 -->
        <template v-else-if="form.post_type === 'competition'">
          <el-form-item label="竞赛名称" prop="competition_name">
            <el-input v-model="form.competition_name" placeholder="请输入竞赛名称" />
          </el-form-item>
          <el-form-item label="竞赛类型" prop="competition_type">
            <el-select v-model="form.competition_type" placeholder="请选择竞赛类型">
              <el-option label="大创" value="C" />
              <el-option label="竞赛" value="D" />
            </el-select>
          </el-form-item>
          <el-form-item label="截止时间" prop="deadline">
            <el-date-picker
              v-model="form.deadline"
              type="date"
              placeholder="选择截止时间"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="团队要求" prop="team_require">
            <el-input
              v-model="form.team_require"
              type="textarea"
              :rows="4"
              placeholder="请输入团队要求"
            />
          </el-form-item>
          <el-form-item label="指导方式" prop="guide_way">
            <el-input
              v-model="form.guide_way"
              type="textarea"
              :rows="4"
              placeholder="请输入指导方式"
            />
          </el-form-item>
          <el-form-item label="奖励" prop="reward">
            <el-input
              v-model="form.reward"
              type="textarea"
              :rows="4"
              placeholder="请输入奖励说明"
            />
          </el-form-item>
        </template>

        <!-- 附件上传 -->
        <el-form-item label="附件">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :file-list="fileList"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传附件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">支持PDF、Word等格式文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading" size="large">
            <el-icon><Check /></el-icon>
            发布项目
          </el-button>
          <el-button @click="handleReset" size="large">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Plus, Upload, Check, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const fileList = ref([])

const form = reactive({
  post_type: 'research',
  research_name: '',
  research_direction: '',
  tech_stack: '',
  recruit_quantity: 1,
  starttime: '',
  endtime: '',
  outcome: '',
  contact: '',
  competition_name: '',
  competition_type: '',
  deadline: '',
  team_require: '',
  guide_way: '',
  reward: '',
  appendix: ''
})

const rules = {
  research_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  research_direction: [{ required: true, message: '请输入研究方向', trigger: 'blur' }],
  competition_name: [{ required: true, message: '请输入竞赛名称', trigger: 'blur' }]
}

const uploadUrl = computed(() => '/api/')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

const handleTypeChange = () => {
  Object.keys(form).forEach(key => {
    if (key !== 'post_type') {
      form[key] = ''
    }
  })
  if (form.post_type === 'research') {
    form.recruit_quantity = 1
  }
}

const handleUploadSuccess = (response) => {
  if (response.code === 200 && response.data) {
    form.appendix = response.data.appendix || ''
    ElMessage.success('上传成功')
  }
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // TODO: 调用发布项目接口
        ElMessage.success('发布成功')
        router.push('/projects')
      } catch (error) {
        ElMessage.error('发布失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  fileList.value = []
  form.appendix = ''
}
</script>

<style scoped>
.publish-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.publish-card {
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
</style>

