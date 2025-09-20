<template>
  <div class="jimeng-page task-manager-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><Setting /></el-icon>
          </div>
          <h1 class="page-title">任务管理器</h1>
        </div>
        <div class="status-section">
          <el-tag 
            :type="getStatusTagType()" 
            size="large" 
            class="status-tag"
          >
            <el-icon class="status-icon"><Component :is="getStatusIcon()" /></el-icon>
            {{ getStatusText() }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="panel-header">
        <div class="panel-icon">
          <el-icon size="24"><Setting /></el-icon>
        </div>
        <h3 class="panel-title">系统控制</h3>
      </div>
      <div class="control-buttons">
        <el-button 
          class="btn-create" size="large"
          @click="startManager"
          :disabled="loading.start || status.status === 'running'"
        >
          <span >
            <VideoPlay />
          </span>
          启动系统
        </el-button>
        <el-button 
          class="btn-batch-retry" size="large"
          @click="pauseManager"
          :disabled="loading.pause || status.status !== 'running'"
        >
          <span >
            <VideoPause />
          </span>
          暂停处理
        </el-button>
        <el-button 
          class="btn-refresh" size="large"
          @click="resumeManager"
          :disabled="loading.resume || status.status !== 'paused'"
        >
          <span >
            <VideoPlay />
          </span>
          恢复处理
        </el-button>
        <el-button 
          class="btn-batch-delete" size="large"
          @click="stopManager"
          :disabled="loading.stop || status.status === 'stopped'"
        >
          <span >
            <VideoPause />
          </span>
          停止系统
        </el-button>
      </div>
    </div>

    <!-- 全局统计 -->
    <div class="stats-overview">
      <div class="panel-title">
        <h3>全局统计</h3>
        <el-button class="btn-refresh-data" @click="refreshAll" :disabled="loading.status">
          <el-icon><Refresh /></el-icon> 刷新数据
        </el-button>
      </div>
      <div class="stats-grid">
        <div class="stat-card pending">
          <div class="stat-icon">
            <el-icon size="24"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ summary.global_total?.pending || 0 }}</div>
            <div class="stat-label">排队中</div>
          </div>
        </div>
        <div class="stat-card processing">
          <div class="stat-icon">
            <el-icon size="24"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ summary.global_total?.processing || 0 }}</div>
            <div class="stat-label">处理中</div>
          </div>
        </div>
        <div class="stat-card completed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCheckFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ summary.global_total?.completed || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        <div class="stat-card failed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCloseFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ summary.global_total?.failed || 0 }}</div>
            <div class="stat-label">失败</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 处理线程 -->
    <div class="thread-stats">
      <div class="panel-header">
        <div class="panel-icon">
          <el-icon size="24"><Cpu /></el-icon>
        </div>
        <h3 class="panel-title">处理线程</h3>
        <div class="thread-summary">
          <el-tag size="small" type="info">
            活跃: {{ status.active_threads || 0 }} / {{ status.max_threads || 0 }}
          </el-tag>
        </div>
      </div>
      
      <div class="thread-list">
        <el-table 
          :data="getThreadList()" 
          class="thread-table"
          :show-header="true"
          stripe
          :row-class-name="getRowClassName"
        >
          <el-table-column label="线程ID" width="100" align="center">
            <template #default="{ row }">
              <div class="thread-id-cell">
                <el-icon size="16" :class="['thread-icon', row.status]">
                  <component :is="getThreadIcon(row.status)" />
                </el-icon>
                <span class="thread-number">#{{ row.id }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getThreadTagType(row.status)" size="small">
                {{ getThreadStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="任务信息" min-width="300">
            <template #default="{ row }">
              <div v-if="row.status === 'active'" class="task-info-cell">
                <div class="task-main-info">
                  <span class="task-id">任务 #{{ row.task_id }}</span>
                  <el-tag size="small" class="platform-tag">{{ row.platform }}</el-tag>
                  <el-tag size="small" type="success" v-if="row.task_type">{{ row.task_type }}</el-tag>
                </div>
                <div class="task-details" v-if="row.prompt">
                  <span class="task-prompt" :title="row.prompt">{{ truncateText(row.prompt, 80) }}</span>
                </div>
              </div>
              <div v-else-if="row.status === 'idle'" class="idle-info">
                <span class="idle-text">等待任务分配</span>
              </div>
              <div v-else class="inactive-info">
                <span class="inactive-text">线程未启动</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button 
                v-if="row.status === 'active'" 
                type="warning" 
                size="small" 
                text
                @click="terminateThread(row.id)"
              >
                终止
              </el-button>
              <span v-else class="no-action">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  VideoPlay, 
  VideoPause, 
  Refresh,
  CircleCheckFilled,
  CircleCloseFilled,
  WarningFilled,
  Loading,
  Clock,
  Setting,
  Cpu
} from '@element-plus/icons-vue'
import { taskManagerAPI } from '../utils/api'

export default {
  name: 'TaskManager',
  components: {
    VideoPlay,
    VideoPause, 
    Refresh,
    CircleCheckFilled,
    CircleCloseFilled,
    WarningFilled,
    Loading,
    Clock,
    Setting,
    Cpu
  },
  setup() {
    const status = ref({})
    const summary = ref({})
    const loading = ref({
      status: false,
      start: false,
      stop: false,
      pause: false,
      resume: false
    })
    
    let autoRefreshTimer = null

    // 获取状态文本
    const getStatusText = () => {
      const statusMap = {
        'running': '运行中',
        'stopped': '已停止',
        'paused': '已暂停',
        'error': '异常'
      }
      return statusMap[status.value.status] || '未知'
    }

    // 获取状态标签类型
    const getStatusTagType = () => {
      const typeMap = {
        'running': 'success',
        'stopped': 'info',
        'paused': 'warning',
        'error': 'danger'
      }
      return typeMap[status.value.status] || 'info'
    }

    // 获取状态图标
    const getStatusIcon = () => {
      const iconMap = {
        'running': CircleCheckFilled,
        'stopped': CircleCloseFilled,
        'paused': WarningFilled,
        'error': CircleCloseFilled
      }
      return iconMap[status.value.status] || Loading
    }

    // 格式化运行时间
    const formatUptime = (seconds) => {
      if (!seconds) return '00:00:00'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    // 获取任务状态类型
    const getTaskStatusType = (statusCode) => {
      const typeMap = {
        0: 'info',    // 排队中
        1: 'warning', // 生成中
        2: 'success', // 已完成
        3: 'danger'   // 失败
      }
      return typeMap[statusCode] || 'info'
    }

    // 刷新状态
    const refreshStatus = async () => {
      loading.value.status = true
      try {
        const response = await taskManagerAPI.getStatus()
        if (response.data.success) {
          status.value = response.data.data
        }
      } catch (error) {
        console.error('获取状态失败:', error)
        ElMessage.error('获取任务管理器状态失败')
      } finally {
        loading.value.status = false
      }
    }

    // 刷新汇总信息
    const refreshSummary = async () => {
      try {
        const response = await taskManagerAPI.getSummary()
        if (response.data.success) {
          summary.value = response.data.data
        }
      } catch (error) {
        console.error('获取汇总信息失败:', error)
        ElMessage.error('获取任务汇总信息失败')
      }
    }



    // 启动管理器
    const startManager = async () => {
      loading.value.start = true
      try {
        const response = await taskManagerAPI.start()
        if (response.data.success) {
          ElMessage.success('任务管理器启动成功')
          await refreshStatus()
        } else {
          ElMessage.warning(response.data.message)
        }
      } catch (error) {
        console.error('启动失败:', error)
        ElMessage.error('启动任务管理器失败')
      } finally {
        loading.value.start = false
      }
    }

    // 停止管理器
    const stopManager = async () => {
      loading.value.stop = true
      try {
        const response = await taskManagerAPI.stop()
        if (response.data.success) {
          ElMessage.success('任务管理器停止成功')
          await refreshStatus()
        } else {
          ElMessage.warning(response.data.message)
        }
      } catch (error) {
        console.error('停止失败:', error)
        ElMessage.error('停止任务管理器失败')
      } finally {
        loading.value.stop = false
      }
    }

    // 暂停管理器
    const pauseManager = async () => {
      loading.value.pause = true
      try {
        const response = await taskManagerAPI.pause()
        if (response.data.success) {
          ElMessage.success('任务管理器暂停成功')
          await refreshStatus()
        } else {
          ElMessage.warning(response.data.message)
        }
      } catch (error) {
        console.error('暂停失败:', error)
        ElMessage.error('暂停任务管理器失败')
      } finally {
        loading.value.pause = false
      }
    }

    // 恢复管理器
    const resumeManager = async () => {
      loading.value.resume = true
      try {
        const response = await taskManagerAPI.resume()
        if (response.data.success) {
          ElMessage.success('任务管理器恢复成功')
          await refreshStatus()
        } else {
          ElMessage.warning(response.data.message)
        }
      } catch (error) {
        console.error('恢复失败:', error)
        ElMessage.error('恢复任务管理器失败')
      } finally {
        loading.value.resume = false
      }
    }

    // 全量刷新
    const refreshAll = async () => {
      await Promise.all([
        refreshStatus(),
        refreshSummary(),
        refreshThreads()
      ])
    }

    // 设置自动刷新
    const startAutoRefresh = () => {
      autoRefreshTimer = setInterval(refreshAll, 5000) // 每5秒刷新一次
    }

    const stopAutoRefresh = () => {
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer)
        autoRefreshTimer = null
      }
    }

    // 生命周期
    onMounted(() => {
      refreshAll()
      startAutoRefresh()
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    // 线程数据
    const threads = ref([])
    
    // 获取线程详细信息
    const refreshThreads = async () => {
      try {
        const response = await taskManagerAPI.getThreads()
        if (response.data.success) {
          threads.value = response.data.data || []
        }
      } catch (error) {
        console.error('获取线程信息失败:', error)
        threads.value = []
      }
    }
    
    // 线程相关方法
    const getThreadList = () => {
      return threads.value
    }

    const getThreadIcon = (status) => {
      switch (status) {
        case 'active': return 'Loading'
        case 'idle': return 'Clock'
        default: return 'CircleCloseFilled'
      }
    }

    const getThreadTagType = (status) => {
      switch (status) {
        case 'active': return 'primary'
        case 'idle': return 'warning'
        default: return 'info'
      }
    }

    const getThreadStatusText = (status) => {
      switch (status) {
        case 'active': return '处理中'
        case 'idle': return '空闲'
        default: return '未启动'
      }
    }

    // 新增的辅助方法
    const getRowClassName = ({ row }) => {
      return `thread-row-${row.status}`
    }

    const getProgressColor = (percentage) => {
      if (percentage >= 80) return '#67c23a'
      if (percentage >= 50) return '#409eff'
      if (percentage >= 20) return '#e6a23c'
      return '#f56c6c'
    }

    const formatRuntime = (startTime) => {
      if (!startTime) return '-'
      const now = new Date()
      const diff = Math.floor((now - startTime) / 1000) // 秒
      
      if (diff < 60) return `${diff}s`
      if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`
      return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }

    const terminateThread = (threadId) => {
      ElMessage.warning(`终止线程 #${threadId} 的功能开发中`)
    }

    return {
      status,
      summary,
      threads,
      loading,
      getStatusText,
      getStatusTagType,
      getStatusIcon,
      formatUptime,
      refreshStatus,
      refreshSummary,
      refreshThreads,
      refreshAll,
      startManager,
      stopManager,
      pauseManager,
      resumeManager,
      getThreadList,
      getThreadIcon,
      getThreadTagType,
      getThreadStatusText,
      getRowClassName,
      getProgressColor,
      formatRuntime,
      truncateText,
      terminateThread
    }
  }
}
</script>

<style scoped>
@import '../styles/jimeng-common.css';

.task-manager-page {
  min-height: calc(100vh - 64px);
  padding: 16px 24px;
}

.task-manager-page > * {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

/* 任务管理器页面特定样式 */

.status-tag {
  font-size: 16px;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 600;
}

.status-icon {
  margin-right: 8px;
}

/* 控制面板 */
.control-panel {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.panel-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.control-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.control-btn {
  flex: 1;
  min-width: 140px;
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
}

/* 统计概览 */
.stats-overview {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  border-radius: 16px;
  color: white;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.pending {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.processing {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.completed {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
}

.stat-card.failed {
  background: linear-gradient(135deg, #fd746c 0%, #ff9068 100%);
}

.stat-icon {
  background: rgba(255, 255, 255, 0.2);
  padding: 12px;
  border-radius: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 处理线程 */
.thread-stats {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.panel-header .panel-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-header .panel-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
  margin-left: 12px;
}

.thread-summary {
  display: flex;
  align-items: center;
  gap: 8px;
}

.thread-list {
  margin-top: 20px;
}

.thread-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.thread-table :deep(.el-table__header-wrapper th) {
  background-color: #f8fafc;
  color: #374151;
  font-weight: 600;
  border: none;
}

.thread-table :deep(.el-table__body tr.thread-row-active) {
  background-color: rgba(102, 126, 234, 0.03);
}

.thread-table :deep(.el-table__body tr.thread-row-active:hover) {
  background-color: rgba(102, 126, 234, 0.08) !important;
}

.thread-table :deep(.el-table__body tr.thread-row-idle) {
  background-color: rgba(230, 162, 60, 0.03);
}

.thread-table :deep(.el-table__body tr.thread-row-idle:hover) {
  background-color: rgba(230, 162, 60, 0.08) !important;
}

.thread-table :deep(.el-table__body tr.thread-row-inactive) {
  background-color: rgba(160, 174, 192, 0.03);
}

.thread-table :deep(.el-table__body tr.thread-row-inactive:hover) {
  background-color: rgba(160, 174, 192, 0.08) !important;
}

/* 线程ID单元格 */
.thread-id-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.thread-icon {
  transition: var(--transition);
}

.thread-icon.active {
  color: #667eea;
  animation: spin 2s linear infinite;
}

.thread-icon.idle {
  color: #e6a23c;
}

.thread-icon.inactive {
  color: var(--text-muted);
}

.thread-number {
  font-weight: 600;
  font-family: 'Monaco', 'Menlo', monospace;
}

/* 任务信息单元格 */
.task-info-cell {
  padding: 8px 0;
}

.task-main-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.task-id {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  font-family: 'Monaco', 'Menlo', monospace;
}

.platform-tag {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  font-weight: 500;
}

.task-details {
  margin-top: 4px;
}

.task-prompt {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 100%;
  word-break: break-word;
  display: block;
  padding-left: 4px;
}

/* 空闲和未启动状态 */
.idle-info, .inactive-info {
  text-align: center;
  padding: 12px 0;
  color: var(--text-muted);
}

.idle-text {
  color: #e6a23c;
  font-weight: 500;
}

.inactive-text {
  color: var(--text-muted);
  font-weight: 500;
}

/* 进度单元格 */
.progress-cell {
  padding: 8px 0;
}

.no-progress, .no-runtime, .no-action {
  color: var(--text-muted);
  font-size: 13px;
}

/* 运行时间 */
.runtime {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 动画效果 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-manager-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .platform-grid {
    grid-template-columns: 1fr;
  }
  
  .platform-stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style> 