import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8888/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response.status, response.data)
    return response
  },
  error => {
    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

// 账号相关API
export const accountAPI = {
  // 获取所有账号
  getAccounts: () => api.get('/jimeng/accounts'),
  
  // 批量添加账号
  addAccounts: (accountsText) => api.post('/jimeng/accounts', { accounts_text: accountsText }),
  
  // 删除指定账号
  deleteAccount: (accountId) => api.delete(`/jimeng/accounts/${accountId}`),
  
  // 清空所有账号
  clearAllAccounts: () => api.delete('/jimeng/accounts/clear'),
  
  // 获取账号使用统计
  getUsageStats: () => api.get('/jimeng/accounts/usage-stats'),
  
  // 健康检查
  healthCheck: () => api.get('/health')
}

// 文生图任务相关API
export const text2imgAPI = {
  // 获取任务列表
  getTasks: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.get(`/jimeng/text2img/tasks${query ? '?' + query : ''}`)
  },
  
  // 创建新任务
  createTask: (taskData) => api.post('/jimeng/text2img/tasks', taskData),
  
  // 更新任务
  updateTask: (taskId, updateData) => api.put(`/jimeng/text2img/tasks/${taskId}`, updateData),
  
  // 删除任务
  deleteTask: (taskId) => api.delete(`/jimeng/text2img/tasks/${taskId}`),
  
  // 批量删除任务
  batchDeleteTasks: (taskIds) => api.delete('/jimeng/text2img/tasks/batch', { data: { task_ids: taskIds } }),
  
  // 获取统计信息
  getStats: () => api.get('/jimeng/text2img/stats'),
  
  // 重试失败任务
  retryTask: (taskId) => api.post(`/jimeng/text2img/tasks/${taskId}/retry`),
  
  // 批量下载图片
  batchDownload: (taskIds) => api.post('/jimeng/text2img/tasks/batch-download', { task_ids: taskIds })
}

// 图生视频任务相关API
export const img2videoAPI = {
  // 获取任务列表
  getTasks: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.get(`/img2video/tasks${query ? '?' + query : ''}`)
  },
  
  // 创建新任务
  createTask: (taskData) => api.post('/img2video/tasks', taskData),
  
  // 更新任务
  updateTask: (taskId, updateData) => api.put(`/img2video/tasks/${taskId}`, updateData),
  
  // 删除任务
  deleteTask: (taskId) => api.delete(`/img2video/tasks/${taskId}`),
  
  // 批量删除任务
  batchDeleteTasks: (taskIds) => api.delete('/img2video/tasks/batch', { task_ids: taskIds }),
  
  // 获取统计信息
  getStats: () => api.get('/img2video/stats')
}

// 配置管理相关API
export const configAPI = {
  // 获取所有配置
  getAllConfigs: () => api.get('/config'),
  
  // 获取指定配置
  getConfig: (key) => api.get(`/config/${key}`),
  
  // 更新指定配置
  updateConfig: (key, value, description = null) => api.put(`/config/${key}`, { 
    value: value,
    description: description 
  }),
  
  // 批量更新配置
  updateBatchConfigs: (configs) => api.put('/config/batch', { configs: configs }),
  
  // 删除指定配置
  deleteConfig: (key) => api.delete(`/config/${key}`),
  
  // 初始化默认配置
  initDefaultConfigs: () => api.post('/config/init')
}

// 任务管理器相关API
export const taskManagerAPI = {
  // 获取任务管理器状态
  getStatus: () => api.get('/task-manager/status'),
  
  // 启动任务管理器
  start: () => api.post('/task-manager/start'),
  
  // 停止任务管理器
  stop: () => api.post('/task-manager/stop'),
  
  // 暂停任务管理器
  pause: () => api.post('/task-manager/pause'),
  
  // 恢复任务管理器
  resume: () => api.post('/task-manager/resume'),
  
  // 获取任务汇总信息
  getSummary: () => api.get('/task-manager/summary'),
  
  // 获取线程详细信息
  getThreads: () => api.get('/task-manager/threads'),
  
  // 健康检查
  health: () => api.get('/task-manager/health')
}

export default api