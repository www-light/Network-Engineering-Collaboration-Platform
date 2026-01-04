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
          <!-- 招募状态标签（仅科研和竞赛项目显示） -->
          <el-tag 
            v-if="(project.post_type === 'research' || project.post_type === 'competition') && project.recruit_status !== undefined"
            :type="project.recruit_status === 0 ? 'success' : 'info'"
            size="small"
            effect="plain"
            style="margin-left: 8px;"
          >
            {{ project.recruit_status === 0 ? '正在招募' : '招募截止' }}
          </el-tag>
        </div>
        <div class="header-right">
          <!-- 科研项目：显示技术栈（完整字符串） -->
          <div v-if="project.post_type === 'research' && project.tech_stack" class="header-tags">
            <el-tag
              size="small"
              type="success"
              effect="plain"
              style="margin-left: 4px;"
            >
              {{ truncateText(project.tech_stack) }}
            </el-tag>
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
              {{ truncateText(skill.skill_name + '(' + (skill.skill_degree === 'skillful' ? '熟练' : '了解') + ')') }}
            </el-tag>
          </div>
          <div v-if="project.post_type === 'personal' && project.skill_score !== undefined" class="score-pill">
            评分 {{ formatScore(project.skill_score) }}
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

const formatScore = (value) => {
  const num = Number(value)
  if (Number.isNaN(num)) return '--'
  return num.toFixed(2)
}
// 截断文本：显示前10个字母或5个汉字，超过则添加省略号
const truncateText = (text) => {
  if (!text) return ''
  
  // 计算字符长度：中文字符算2个位置，英文字符算1个位置
  let length = 0
  let charCount = 0
  const maxLength = 10 // 最多10个字符位置（相当于10个字母或5个汉字）
  
  for (let i = 0; i < text.length; i++) {
    const char = text[i]
    // 判断是否为中文字符（包括中文标点）
    const isChinese = /[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]/.test(char)
    
    if (isChinese) {
      length += 2 // 中文字符占2个位置
    } else {
      length += 1 // 英文字符占1个位置
    }
    
    charCount++
    
    // 如果超过最大长度，截断并添加省略号
    if (length > maxLength) {
      return text.substring(0, charCount - 1) + '...'
    }
  }
  
  // 如果没超过长度，返回原文本
  return text
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
  gap: 6px;
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

.score-pill {
  background: #f0f9ff;
  color: #409eff;
  border: 1px solid #a0cfff;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
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

