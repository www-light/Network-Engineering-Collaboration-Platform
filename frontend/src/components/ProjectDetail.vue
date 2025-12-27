<template>
  <div class="project-detail">
    <el-card v-if="loading" shadow="never">
      <el-skeleton :rows="8" animated />
    </el-card>
    <el-card v-else-if="detail" shadow="never" class="detail-card">
      <template #header>
        <div class="detail-header">
          <h2>{{ getTitle() }}</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleApply">
              <el-icon><Link /></el-icon>
              申请/邀请
            </el-button>
            <el-button @click="handleMessage">
              <el-icon><Message /></el-icon>
              私信
            </el-button>
          </div>
        </div>
      </template>
      <div class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">
            {{ getTitle() }}
          </el-descriptions-item>
          <el-descriptions-item label="发布教师">
            {{ getTeacherName() }}
          </el-descriptions-item>
          <template v-if="detail.post_type === 'research'">
            <el-descriptions-item label="研究方向">
              {{ detail.research_direction }}
            </el-descriptions-item>
            <el-descriptions-item label="技术栈">
              {{ detail.tech_stack }}
            </el-descriptions-item>
            <el-descriptions-item label="招募人数">
              {{ detail.recruit_quantity }}人
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ detail.starttime }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ detail.endtime }}
            </el-descriptions-item>
            <el-descriptions-item label="预期成果" :span="2">
              {{ detail.outcome }}
            </el-descriptions-item>
            <el-descriptions-item label="联系方式" :span="2">
              {{ detail.contact }}
            </el-descriptions-item>
            <el-descriptions-item v-if="detail.appendix" label="附件" :span="2">
              <el-link
                type="primary"
                @click="handleDownload(detail.appendix)"
              >
                <el-icon><Download /></el-icon>
                下载附件
              </el-link>
            </el-descriptions-item>
          </template>
          <template v-else-if="detail.post_type === 'competition'">
            <el-descriptions-item label="竞赛类型">
              {{ detail.competition_type }}
            </el-descriptions-item>
            <el-descriptions-item label="截止时间">
              {{ detail.deadline }}
            </el-descriptions-item>
            <el-descriptions-item label="团队要求" :span="2">
              {{ detail.team_require }}
            </el-descriptions-item>
            <el-descriptions-item label="指导方式" :span="2">
              {{ detail.guide_way }}
            </el-descriptions-item>
            <el-descriptions-item label="奖励" :span="2">
              {{ detail.reward }}
            </el-descriptions-item>
            <el-descriptions-item v-if="detail.appendix" label="附件" :span="2">
              <el-link
                type="primary"
                @click="handleDownload(detail.appendix)"
              >
                <el-icon><Download /></el-icon>
                下载附件
              </el-link>
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
    </el-card>
    <el-empty v-else description="暂无项目详情" />
  </div>
</template>

<script setup>
import { Link, Message, Download } from '@element-plus/icons-vue'
import { downloadFile } from '@/api/project'
import { ElMessage } from 'element-plus'

const props = defineProps({
  detail: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['apply', 'message'])

const getTitle = () => {
  if (!props.detail) return ''
  if (props.detail.post_type === 'research') {
    return props.detail.research_name
  } else if (props.detail.post_type === 'competition') {
    return props.detail.competition_name
  }
  return ''
}

const getTeacherName = () => {
  if (!props.detail) return ''
  if (props.detail.post_type === 'research') {
    return props.detail.teacher_name
  }
  return ''
}

const handleApply = () => {
  emit('apply')
}

const handleMessage = () => {
  emit('message')
}
const handleDownload = async (url) => {
  try {
    await downloadFile(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}
</script>

<style scoped>
.project-detail {
  height: 100%;
}

.detail-card {
  border-radius: 12px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  padding: 20px 0;
}
</style>

