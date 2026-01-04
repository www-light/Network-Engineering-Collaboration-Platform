import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getProjects } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  const projects = ref([])
  const currentDirection = ref('all')
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const totalPages = ref(0)

  // 获取项目列表（支持分页、搜索及额外筛选）
  const fetchProjects = async (direction, pageNum = 1, size = 20, search = '', extraFilters = {}) => {
    loading.value = true
    try {
      // 构建查询参数
      const params = {
        page: pageNum,
        page_size: size
      }
      if (direction && direction !== 'all') {
        params.post_type = direction
      }
      if (search && search.trim()) {
        params.search = search.trim()
      }
      if (extraFilters.tech_stack && extraFilters.tech_stack.trim()) {
        params.tech_stack = extraFilters.tech_stack.trim()
      }
      if (extraFilters.time_cycle && extraFilters.time_cycle !== 'all') {
        params.time_cycle = extraFilters.time_cycle
      }
      if (extraFilters.recruit_status && extraFilters.recruit_status !== 'all') {
        params.recruit_status = extraFilters.recruit_status
      }
      
      const response = await getProjects(params)
      
      // 处理响应
      if (response && response.code === 200 && response.data !== undefined) {
        const data = response.data
        // 新格式：包含分页信息
        if (data.items) {
          projects.value = data.items || []
          total.value = data.total || 0
          page.value = data.page || 1
          pageSize.value = data.page_size || 20
          totalPages.value = data.total_pages || 0
        } else if (Array.isArray(data)) {
          // 兼容旧格式（直接返回数组）
          projects.value = data
          total.value = data.length
        } else {
          projects.value = []
          total.value = 0
        }
      } else if (Array.isArray(response)) {
        // 兼容旧格式（直接返回数组）
        projects.value = response
        total.value = response.length
      } else {
        projects.value = []
        total.value = 0
      }
      
      if (direction) {
        currentDirection.value = direction
      }
    } catch (error) {
      console.error('获取项目列表失败:', error)
      projects.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    currentDirection,
    loading,
    total,
    page,
    pageSize,
    totalPages,
    fetchProjects
  }
})

