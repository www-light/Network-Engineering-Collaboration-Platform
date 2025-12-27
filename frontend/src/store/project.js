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
      const data = await getProjects()
      projects.value = data
      if (direction) {
        currentDirection.value = direction
      }
    } catch (error) {
      console.error('获取项目列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 筛选项目
  const filteredProjects = computed(() => {
    if (currentDirection.value === 'all') {
      return projects.value
    }
    return projects.value.filter(p => p.post_type === currentDirection.value)
  })

  return {
    projects,
    currentDirection,
    loading,
    filteredProjects,
    fetchProjects
  }
})

