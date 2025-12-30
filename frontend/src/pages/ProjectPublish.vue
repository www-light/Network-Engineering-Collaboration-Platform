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
            <el-radio v-if="userStore.isTeacher" label="research">科研项目</el-radio>
            <el-radio v-if="userStore.isTeacher" label="competition">大创/竞赛</el-radio>
            <el-radio v-if="userStore.isStudent" label="personal">个人技能</el-radio>
            <!-- <el-radio label="personal">个人项目</el-radio> -->
          </el-radio-group>
        </el-form-item>

        <!-- 科研项目表单 -->
        <template v-if="form.post_type === 'research'">
          <el-form-item label="项目名称" prop="research_name">
            <el-input v-model="form.research_name" placeholder="请输入项目名称" />
          </el-form-item>
          <el-form-item label="研究方向" prop="research_direction">
            <el-input v-model="form.research_direction" placeholder="如 “人工智能 / 网络安全” 等" />
          </el-form-item>
          <el-form-item label="技术栈" prop="tech_stack">
            <el-input v-model="form.tech_stack" placeholder="如 “java / python / 机器学习” 等" />
          </el-form-item>
          <el-form-item label="招募人数" prop="recruit_quantity">
            <el-input-number v-model="form.recruit_quantity" :min="1" :max="5" />
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
            <el-select v-model="form.competition_type" placeholder="请选择竞赛类型" style="width: 220px;">
              <el-option label="大创项目" value="C" />
              <el-option label="学科竞赛" value="D" />
              <el-option label="企业合作竞赛" value="E" />
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
          <el-form-item label="组队要求" prop="team_require">
            <el-input v-model="form.team_require" placeholder="如 “需1名算法 + 2名开发”"/>
          </el-form-item>
          <el-form-item label="指导方式" prop="guide_way">
            <el-select v-model="form.guide_way" placeholder="请选择指导方式" style="width: 220px;">
              <el-option label="线上" value="C" />
              <el-option label="线下" value="D" />
            </el-select>
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

        <!-- 个人项目表单 -->
        <template v-if="form.post_type === 'personal'">
          <el-form-item label="专业方向" prop="major">
            <el-input v-model="form.major" placeholder="请输入专业方向" />
          </el-form-item>
          <el-form-item label="掌握技术" prop="skill">
            <el-input v-model="form.skill" placeholder="请输入掌握技术" />
          </el-form-item>
          <el-form-item label="掌握程度" prop="skill_degree">
            <el-select v-model="form.skill_degree" placeholder="请选择技术掌握程度" style="width: 220px;">
              <el-option label="了解" value="C" />
              <el-option label="熟练" value="D" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目经历" prop="project_experience">
            <el-input
              v-model="form.project_experience"
              type="textarea"
              :rows="4"
              placeholder="请输入项目经历" 
            />
          </el-form-item>
          <el-form-item label="附带链接" prop="experience_link">
            <el-input v-model="form.experience_link" placeholder="请输入附 GitHub 链接 / 作品 demo" />
          </el-form-item>
          
          <el-form-item label="兴趣领域" prop="habit_tag">
            <div class="tag-scroll-x">
              <div class="tag-flex-row">
                <el-check-tag
                  v-for="tag in tagsList"
                  :key="tag.tag_id"
                  :checked="form.habit_tag.includes(tag.tag_id)"
                  @change="() => toggleTag(tag.tag_id)"
                >
                  {{ tag.name }}
                </el-check-tag>
                <el-button
                  class="tag-create"
                  type="primary"
                  text
                  @click="handleCreateTag"
                  :loading="tagsLoading"
                >
                  + 自定义标签
                </el-button>
              </div>
            </div>
            <div class="tag-tip">
              已选 {{ form.habit_tag.length }}/3
            </div>
          </el-form-item>

          <el-form-item label="可投入时间" prop="spend_time">
            <el-input v-model="form.spend_time" placeholder="如 “每周15小时”" />
          </el-form-item>
          <el-form-item label="期待合作类型" prop="expect_worktype">
            <el-select v-model="form.expect_worktype" placeholder="请选择期待合作类型" style="width: 220px;">
              <el-option label="科研" value="C" />
              <el-option label="大创" value="D" />
              <el-option label="竞赛" value="E" />
            </el-select>
          </el-form-item>
          <el-form-item label="合作意愿声名" prop="filter">
            <el-select v-model="form.filter" placeholder="请输入项目筛选条件" style="width: 220px;">
              <el-option label="所有项目" value="C" />
              <el-option label="可接受跨方向合作" value="D" />
              <el-option label="优先本地项目" value="E" />
            </el-select>
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
              <div class="el-upload__tip">
                支持PDF、Word等格式文件
                <template v-if="form.post_type === 'research'">，上传项目立项书或往期成果</template>
                <template v-else-if="form.post_type === 'competition'">，上传历年获奖案例和备赛资料</template>
                <template v-else-if="form.post_type === 'personal'">，上传个人简历或技能证书</template>
              </div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { Plus, Upload, Check, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTags, createTag } from '@/api/tag'
import { publishProject } from '@/api/project'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const fileList = ref([])
const tagsList = ref([])
const tagsLoading = ref(false)

const form = reactive({
  post_type: userStore.isStudent ? 'personal' : 'research',
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
  appendix: '',

  major: '',
  skill: '',
  skill_degree: '',
  project_experience: '',
  experience_link: '',
  habit_tag: [],
  spend_time: '',
  expect_worktype: '',
  filter: ''
})

const rules = {
  research_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  research_direction: [{ required: true, message: '请输入研究方向', trigger: 'blur' }],
  tech_stack: [{ required: true, message: '请输入技术栈', trigger: 'blur' }],
  recruit_quantity: [{ required: true, message: '请输入招募人数', trigger: 'blur' }], 
  starttime: [{ required: true, message: '请输入开始时间', trigger: 'blur' }],
  endtime: [{ required: true, message: '请输入结束时间', trigger: 'blur' }],
  outcome: [{ required: true, message: '请输入预期成果', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系方式', trigger: 'blur' }],

  competition_name: [{ required: true, message: '请输入竞赛名称', trigger: 'blur' }],
  competition_type: [{ required: true, message: '请选择竞赛类型', trigger: 'blur' }],
  deadline: [{ required: true, message: '请输入截止时间', trigger: 'blur' }],
  team_require: [{ required: true, message: '请输入团队要求', trigger: 'blur' }],
  guide_way: [{ required: true, message: '请输入指导方式', trigger: 'blur' }],

  major: [{ required: true, message: '请输入专业方向', trigger: 'blur' }],
  skill: [{ required: true, message: '请输入掌握技术', trigger: 'blur' }],
  skill_degree: [{ required: true, message: '请选择技术掌握程度', trigger: 'blur' }],
  spend_time: [{ required: true, message: '请输入可投入时间', trigger: 'blur' }],
  expect_worktype: [{ required: true, message: '请选择期待合作类型', trigger: 'blur' }],
  filter: [{ required: true, message: '请选择项目筛选条件', trigger: 'blur' }],
}

const uploadUrl = computed(() => '/api/')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

const handleTypeChange = () => {
  Object.keys(form).forEach(key => {
    if (key !== 'post_type') {
      if (key === 'habit_tag') {
        form[key] = []
      } else {
        form[key] = ''
      }
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

// 加载标签列表
const loadTags = async () => {
  tagsLoading.value = true
  try {
    const res = await getTags()
    const tags = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : [])
    tagsList.value = tags
  } catch (error) {
    console.error('加载标签失败:', error)
    ElMessage.error('加载标签失败')
  } finally {
    tagsLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 构建提交数据
        const submitData = {
          post_type: form.post_type,
          appendix: form.appendix || ''
        }
        
        // 根据项目类型添加对应字段
        if (form.post_type === 'research') {
          submitData.research_name = form.research_name
          submitData.research_direction = form.research_direction
          submitData.tech_stack = form.tech_stack
          submitData.recruit_quantity = form.recruit_quantity
          submitData.starttime = form.starttime
          submitData.endtime = form.endtime
          submitData.outcome = form.outcome
          submitData.contact = form.contact
        } else if (form.post_type === 'competition') {
          submitData.competition_name = form.competition_name
          submitData.competition_type = form.competition_type
          submitData.deadline = form.deadline
          submitData.team_require = form.team_require
          submitData.guide_way = form.guide_way
          submitData.reward = form.reward || ''
        } else if (form.post_type === 'personal') {
          submitData.major = form.major
          submitData.skill = form.skill
          submitData.skill_degree = form.skill_degree
          submitData.project_experience = form.project_experience || ''
          submitData.experience_link = form.experience_link || ''
          submitData.habit_tag = form.habit_tag || []
          submitData.spend_time = form.spend_time
          submitData.expect_worktype = form.expect_worktype
          submitData.filter = form.filter
        }
        
        // 调用发布项目接口
        const response = await publishProject(submitData)
        
        if (response && response.post_id) {
          ElMessage.success('发布成功')
          router.push('/projects')
        } else {
          ElMessage.error('发布失败，请重试')
        }
      } catch (error) {
        console.error('发布失败:', error)
        const errorMsg = error.response?.data?.msg || error.message || '发布失败，请重试'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

// 切换标签，限制 3 个
const toggleTag = (tagId) => {
  const exists = form.habit_tag.includes(tagId)
  if (exists) {
    form.habit_tag = form.habit_tag.filter(id => id !== tagId)
    return
  }
  if (form.habit_tag.length >= 3) {
    ElMessage.warning('最多选择 3 个标签')
    return
  }
  form.habit_tag = [...form.habit_tag, tagId]
}

// 创建自定义标签
const handleCreateTag = async () => {
  try {
    const { value, action } = await ElMessageBox.prompt('请输入自定义标签名称', '创建标签', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPlaceholder: '如 Python / 前端 / 安全',
      inputValidator: (val) => !!(val && val.trim()) || '标签名称不能为空'
    })
    if (action === 'confirm' && value?.trim()) {
      const inputName = value.trim()
      // 判断标签是否已存在（忽略大小写和前后空格）
      const exists = tagsList.value.some(tag => tag.name.trim().toLowerCase() === inputName.toLowerCase())
      if (exists) {
        ElMessage({
          message: `已创建该标签："${inputName}"` ,
          type: 'error',
          showClose: true
        })
        return
      }
      tagsLoading.value = true
      const res = await createTag(inputName)
      // 检查响应中的code，如果是201表示新创建的标签
      const isNewTag = res?.code === 201
      // 获取标签数据
      const newTag = res?.data || res
      if (newTag?.tag_id) {
        // 新标签插入最前面
        tagsList.value = [newTag, ...tagsList.value.filter(t => t.tag_id !== newTag.tag_id)]
        // 自动选中
        if (!form.habit_tag.includes(newTag.tag_id)) {
          if (form.habit_tag.length >= 3) {
            ElMessage.warning('最多选择 3 个标签')
          } else {
            form.habit_tag = [...form.habit_tag, newTag.tag_id]
          }
        }
        // 如果是新创建的标签（code为201），显示绿色成功提示
        if (isNewTag) {
          ElMessage({
            message: `标签 "${newTag.name}" 创建成功`,
            type: 'success',
            showClose: true
          })
        }
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('创建标签失败:', error)
      ElMessage.error('创建标签失败，请稍后重试')
    }
  } finally {
    tagsLoading.value = false
  }
}

onMounted(() => {
  // 根据用户身份设置默认项目类型
  if (userStore.isStudent && form.post_type !== 'personal') {
    form.post_type = 'personal'
  } else if (userStore.isTeacher && form.post_type === 'personal') {
    form.post_type = 'research'
  }
  loadTags()
})

const handleReset = () => {
  formRef.value?.resetFields()
  fileList.value = []
  form.appendix = ''
  form.habit_tag = []
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

.tag-scroll-x {
  overflow-x: auto;
  padding-bottom: 4px;
}

.tag-flex-row {
  display: flex;
  flex-direction: row;
  gap: 12px;
  min-width: 100%;
}

.tag-flex-row .el-check-tag {
  text-align: center;
  border-radius: 10px;
  padding: 10px 0 10px 0;
  font-weight: 600;
  font-size: 14px;
  min-width: 100px;
}

.tag-create {
  min-width: 100px;
  text-align: center;
  border-radius: 10px;
}

.tag-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>

