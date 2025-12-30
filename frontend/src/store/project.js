import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getProjects } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentDirection = ref('all')
  const loading = ref(false)

  // 获取项目列表
  const fetchProjects = async (direction) => {
    loading.value = true
    try {
      // 构建查询参数，如果指定了方向则传递给后端
      const params = direction && direction !== 'all' ? { post_type: direction } : {}
      const data = await getProjects(params)
      projects.value = data || []
      if (direction) {
        currentDirection.value = direction
      }
    } catch (error) {
      console.error('获取项目列表失败:', error)
      projects.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    currentDirection,
    loading,
    fetchProjects
  }
})

