<template>
  <el-card
    :class="['project-card', { active: isActive }]"
    shadow="hover"
    @click="$emit('click')"
  >
    <div class="card-content">
      <div class="card-header">
        <el-tag :type="getTagType(project.post_type)" size="small" effect="light">
          {{ getTypeName(project.post_type) }}
        </el-tag>
        <span class="title">{{ project.title }}</span>
      </div>
      <div class="card-info">
        <div class="teacher">
          <el-icon><User /></el-icon>
          <span>{{ project.teacher_name }}</span>
        </div>
        <div class="stats">
          <span class="stat-item">
            <el-icon><Star /></el-icon>
            {{ project.like_num }}
          </span>
          <span class="stat-item">
            <el-icon><Collection /></el-icon>
            {{ project.favorite_num }}
          </span>
          <span class="stat-item">
            <el-icon><ChatLineRound /></el-icon>
            {{ project.comment_num }}
          </span>
        </div>
      </div>
      <div class="card-footer">
        <span class="time">{{ formatTime(project.create_time) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { User, Star, Collection, ChatLineRound } from '@element-plus/icons-vue'

defineProps({
  project: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const getTagType = (type) => {
  const map = {
    research: 'success',
    competition: 'warning',
    personal: 'info'
  }
  return map[type] || 'info'
}

const getTypeName = (type) => {
  const map = {
    research: '科研项目',
    competition: '大创/竞赛',
    personal: '个人项目'
  }
  return map[type] || type
}

const formatTime = (time) => {
  const date = new Date(time)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.project-card {
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.project-card.active {
  border-color: #409eff;
  background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
}

.card-content {
  padding: 8px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-info {
  margin-bottom: 12px;
}

.teacher {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.time {
  color: #909399;
  font-size: 12px;
}
</style>

