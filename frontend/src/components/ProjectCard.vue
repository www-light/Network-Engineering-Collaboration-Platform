<template>
  <el-card
    :class="['project-card', { active: isActive }]"
    shadow="hover"
    @click="$emit('click')"
  >
    <div class="card-content">
      <div class="card-header">
        <div class="header-left">
          <el-tag :type="getTagType(project.post_type)" size="small" effect="light">
            {{ getTypeName(project.post_type) }}
          </el-tag>
          <span class="title">{{ project.title }}</span>
        </div>
        <div class="header-right">
          <!-- 科研项目：显示技术栈 -->
          <div v-if="project.post_type === 'research' && project.tech_stack && project.tech_stack.length > 0" class="header-tags">
            <el-tag
              v-for="(stack, index) in project.tech_stack.slice(0, 2)"
              :key="index"
              size="small"
              type="success"
              effect="plain"
              style="margin-left: 4px;"
            >
              {{ stack }}
            </el-tag>
            <span v-if="project.tech_stack.length > 2" class="more-tags">+{{ project.tech_stack.length - 2 }}</span>
          </div>
          <!-- 个人技能：显示技能和熟练度 -->
          <div v-if="project.post_type === 'personal' && project.skills && project.skills.length > 0" class="header-tags">
            <el-tag
              v-for="(skill, index) in project.skills.slice(0, 2)"
              :key="'skill-' + index"
              size="small"
              type="primary"
              effect="plain"
              style="margin-left: 4px;"
            >
              {{ skill.skill_name }}({{ skill.skill_degree === 'skillful' ? '熟练' : '了解' }})
            </el-tag>
          </div>
        </div>
      </div>
      <div class="card-info">
        <div class="teacher">
          <el-icon><User /></el-icon>
          <span>{{ project.teacher_name }}</span>
        </div>
        <!-- 附件信息 -->
        <div v-if="project.attachments && project.attachments.length > 0" class="attachments-info">
          <el-icon><Document /></el-icon>
          <span>{{ project.attachments.length }}个附件</span>
        </div>
      </div>
      <div class="card-footer">
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
        <span class="time">{{ formatTime(project.create_time) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { User, Star, Collection, ChatLineRound, Document } from '@element-plus/icons-vue'

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
    personal: '个人技能'
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
  margin-bottom: 16px;
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
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
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

.header-right {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.header-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
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
  margin-left: 16px;
}

.more-tags {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.attachments-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 12px;
  margin-left: 16px;
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.time {
  color: #909399;
  font-size: 12px;
}
</style>

