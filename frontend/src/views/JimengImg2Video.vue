<template>
  <div class="jimeng-img2video-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><VideoPlay /></el-icon>
          </div>
          <h1 class="page-title">即梦图生视频</h1>
        </div>
        <div class="status-section">
          <!-- 导入文件夹按钮 -->
          <el-button 
            type="primary" 
            size="large"
            @click="showImportFolderDialog"
            :loading="importFolderLoading"
            class="import-btn"
          >
            <el-icon><Folder /></el-icon>
            导入文件夹
          </el-button>
          
          <el-button 
            type="success" 
            size="large"
            @click="importFromExcel"
            :loading="importExcelLoading"
            class="import-btn"
          >
            <el-icon><Document /></el-icon>
            导入Excel表格
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
        <div class="stats-grid">
        <div class="stat-card total">
            <div class="stat-icon">
              <el-icon size="24"><Document /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_tasks || 0 }}</div>
            <div class="stat-label">总任务</div>
            </div>
          </div>
        <div class="stat-card pending">
          <div class="stat-icon">
              <el-icon size="24"><Clock /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pending_tasks || 0 }}</div>
            <div class="stat-label">排队中</div>
            </div>
          </div>
        <div class="stat-card processing">
          <div class="stat-icon">
              <el-icon size="24"><Loading /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.processing_tasks || 0 }}</div>
            <div class="stat-label">生成中</div>
            </div>
          </div>
        <div class="stat-card completed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCheckFilled /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completed_tasks || 0 }}</div>
            <div class="stat-label">已完成</div>
            </div>
          </div>
        <div class="stat-card failed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCloseFilled /></el-icon>
            </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.failed_tasks || 0 }}</div>
            <div class="stat-label">失败</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 任务管理 -->
    <div class="task-management">
      <div class="panel-title">
        <h3>任务列表</h3>
        <div class="toolbar-actions">
          <el-select 
            v-model="statusFilter" 
            placeholder="筛选状态"
            clearable
            @change="handleStatusFilter"
            class="status-filter"
          >
            <el-option label="全部" :value="null" />
            <el-option label="排队中" value="0" />
            <el-option label="生成中" value="1" />
            <el-option label="已完成" value="2" />
            <el-option label="失败" value="3" />
          </el-select>
          <el-button 
            @click="refreshTasks"
            :loading="loading"
            class="refresh-btn"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <!-- 批量重试按钮 -->
          <el-button 
            type="warning" 
            @click="batchRetryFailedTasks"
            :loading="batchRetryLoading"
            class="batch-retry-btn"
          >
            <el-icon><RefreshRight /></el-icon>
            批量重试失败任务
          </el-button>
          <el-popconfirm
            title="确定要删除今日前的所有任务吗？此操作不可恢复！"
            @confirm="deleteTasksBeforeToday"
          >
            <template #reference>
              <el-button 
                type="danger" 
                :loading="deleteBeforeTodayLoading"
                class="delete-before-today-btn"
              >
                <el-icon><Delete /></el-icon>
                删除今日前任务
              </el-button>
            </template>
          </el-popconfirm>
          <!-- 批量操作按钮 -->
          <el-button 
            type="danger" 
            @click="batchDeleteTasks" 
            :disabled="selectedTasks.length === 0"
            v-if="selectedTasks.length > 0"
          >
            <el-icon><Delete /></el-icon>
            删除选中 ({{ selectedTasks.length }})
          </el-button>
          
          <el-button 
            type="warning" 
            @click="batchDownloadVideos" 
            :disabled="selectedCompletedTasks.length === 0"
            :loading="batchDownloadLoading"
            v-if="selectedCompletedTasks.length > 0"
          >
            <el-icon><Download /></el-icon>
            下载选中 ({{ selectedCompletedTasks.length }})
          </el-button>
          </div>
        </div>
        
      <!-- 任务表格 -->
      <div class="task-table-container">
        <el-table 
          :data="tasks" 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          class="modern-table"
          stripe
          :header-cell-style="{ background: '#f8fafc', color: '#374151', fontWeight: '600' }"
        >
          <el-table-column 
            type="selection" 
            width="55" 
            :selectable="isTaskSelectable"
          />
          <el-table-column prop="id" label="ID" width="80" align="center" />
          
          <el-table-column label="图片" min-width="200">
            <template #default="{ row }">
              <div class="image-cell">
                <el-tooltip :content="row.image_path || ''" placement="top">
                  <span class="image-filename">{{ getImageFilename(row.image_path) }}</span>
                </el-tooltip>
                <el-button 
                  v-if="row.image_path" 
                  size="small" 
                  type="primary" 
                  link 
                  @click="previewImage(row.image_path)"
                  class="preview-btn"
                >
                  预览
                </el-button>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="提示词" min-width="250">
            <template #default="{ row }">
              <div class="prompt-cell">
                <el-tooltip :content="row.prompt || ''" placement="top">
                  <span class="prompt-text">{{ truncateText(row.prompt || '', 80) }}</span>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="model" label="模型" width="120" align="center">
            <template #default="{ row }">
              <el-tag class="model-tag">{{ row.model || 'Video 3.0' }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="second" label="时长" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" class="duration-tag">{{ row.second || 5 }}s</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
                  <el-tag 
                :type="getStatusType(row.status)"
                :class="['status-tag', { 'processing-tag': row.status === 1 }]"
              >
                <el-icon v-if="row.status === 1" class="rotating-icon"><Loading /></el-icon>
                {{ row.status_text || '-' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="视频" width="120" align="center">
            <template #default="{ row }">
              <el-button 
                v-if="row.video_url" 
                size="small" 
                type="success" 
                @click="previewVideo(row.video_url)"
                class="video-btn"
              >
                <el-icon><VideoPlay /></el-icon>
                查看
              </el-button>
              <span v-else class="no-content">-</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button 
                    size="small" 
                    type="warning"
                  @click="retryTask(row.id)"
                  v-if="row.status === 3"
                  class="action-btn"
                >
                  <el-icon><RefreshRight /></el-icon>
                  重试
                </el-button>
                <el-popconfirm
                  title="确定要删除这个任务吗？"
                  @confirm="deleteTask(row.id)"
                  >
                  <template #reference>
                    <el-button 
                      size="small" 
                      type="danger" 
                      class="action-btn"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
                </div>
            </template>
          </el-table-column>
        </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
            </div>
            </div>
            </div>

    <!-- 图片预览对话框 -->
    <el-dialog 
      v-model="imagePreviewVisible" 
      title="图片预览" 
      width="60%"
      @close="imagePreviewVisible = false"
    >
      <div class="image-preview">
        <img :src="previewImageUrl" alt="预览图片" style="max-width: 100%; height: auto;" />
            </div>
    </el-dialog>

    <!-- 视频预览对话框 -->
    <el-dialog 
      v-model="videoPreviewVisible" 
      title="视频预览" 
      width="70%"
      @close="videoPreviewVisible = false"
    >
      <div class="video-preview">
        <video :src="previewVideoUrl" controls style="max-width: 100%; height: auto;">
          您的浏览器不支持视频播放
        </video>
              </div>
    </el-dialog>

    <!-- 导入文件夹设置对话框 -->
    <el-dialog
      v-model="importFolderDialogVisible"
      title="导入文件夹设置"
      width="400px"
      destroy-on-close
    >
      <el-form :model="importFolderForm" label-width="100px">
        <el-form-item label="视频模型">
          <el-select v-model="importFolderForm.model" placeholder="请选择视频模型">
            <el-option label="Video 3.0" value="Video 3.0" />
            <el-option label="Video S2.0 Pro" value="Video S2.0 Pro" />
          </el-select>
        </el-form-item>
        <el-form-item label="视频时长">
          <el-select v-model="importFolderForm.second" placeholder="请选择视频时长">
            <el-option label="5秒" :value="5" />
            <el-option label="10秒" :value="10" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importFolderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="importFromFolder" :loading="importFolderLoading">
            确认
          </el-button>
        </span>
            </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  VideoPlay,
  FolderOpened, 
  Document,
  Delete, 
  Download,
  Clock,
  Loading,
  CircleCheckFilled,
  CircleCloseFilled,
  Refresh,
  RefreshRight,
  Folder
} from '@element-plus/icons-vue'
import { img2videoAPI } from '@/utils/api'
import * as ElementPlus from 'element-plus'

// 响应式数据
const loading = ref(false)
const tasks = ref([])
const selectedTasks = ref([])
const statusFilter = ref(null)
    const stats = reactive({
  total_tasks: 0,
  pending_tasks: 0,
  processing_tasks: 0,
  completed_tasks: 0,
  failed_tasks: 0
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
    })

// 导入相关状态
const importFolderLoading = ref(false)
const importExcelLoading = ref(false)
const batchDownloadLoading = ref(false)

// 批量重试状态
const batchRetryLoading = ref(false)

// 删除今日前任务状态
const deleteBeforeTodayLoading = ref(false)

// 预览相关状态
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const videoPreviewVisible = ref(false)
const previewVideoUrl = ref('')

// 导入文件夹对话框状态
const importFolderDialogVisible = ref(false)
const importFolderForm = reactive({
  model: 'Video 3.0',
  second: 5
})

// 计算属性
const selectedCompletedTasks = computed(() => {
  if (!selectedTasks.value || !Array.isArray(selectedTasks.value)) {
    return []
  }
  return selectedTasks.value.filter(task => 
    task && 
    task.status === 2 && 
    task.video_url && 
    task.video_url.trim() !== ''
  )
})

// 方法
const loadTasks = async () => {
  try {
    loading.value = true
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    if (statusFilter.value !== null) {
      params.status = statusFilter.value
    }
    
    const response = await img2videoAPI.getTasks(params)
    
    if (response.data.success) {
      tasks.value = response.data.data || []
      pagination.total = response.data.pagination?.total || 0
    } else {
      ElMessage.error(response.data.message || '加载任务列表失败')
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await img2videoAPI.getStats()
    if (response.data.success) {
      Object.assign(stats, response.data.data)
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const importFromFolder = async () => {
  try {
    // 首先询问用户选择模型和时长
    const model = await ElMessageBox.confirm(
      '请选择视频模型',
      '导入文件夹设置',
      {
        confirmButtonText: 'Video 3.0',
        cancelButtonText: 'Video S2.0 Pro',
        distinguishCancelAndClose: true,
        type: 'info'
      }
    ).then(
      () => 'Video 3.0',  // 确认按钮返回Video 3.0
      (action) => action === 'cancel' ? 'Video S2.0 Pro' : null  // 取消按钮返回Video S2.0 Pro，关闭返回null
    )
    
    // 如果用户关闭了对话框，则取消操作
    if (!model) return
    
    // 根据选择的模型，询问用户选择时长
    let second = 5
    if (model === 'Video 3.0') {
      const result = await ElMessageBox.confirm(
        '请选择视频时长',
        '导入文件夹设置',
        {
          confirmButtonText: '5秒',
          cancelButtonText: '10秒',
          distinguishCancelAndClose: true,
          type: 'info'
        }
      ).then(
        () => 5,  // 确认按钮返回5秒
        (action) => action === 'cancel' ? 10 : null  // 取消按钮返回10秒，关闭返回null
      )
      
      // 如果用户关闭了对话框，则取消操作
      if (result === null) return
      
      second = result
    }
    
    // 设置表单值
    importFolderForm.model = model
    importFolderForm.second = second
    
    // 调用API
    importFolderLoading.value = true
    
    // 使用选择的模型和时长
    const response = await img2videoAPI.importFolder({
      model: importFolderForm.model,
      second: importFolderForm.second
    })
    
    if (response.data.success) {
      ElMessage.success(`开始导入文件夹，使用模型: ${importFolderForm.model}，时长: ${importFolderForm.second}秒`)
      // 延迟刷新任务列表
      setTimeout(() => {
        loadTasks()
        loadStats()
      }, 2000)
    } else {
      ElMessage.error(response.data.message || '导入文件夹失败')
    }
  } catch (error) {
    console.error('导入文件夹失败:', error)
    ElMessage.error('导入文件夹失败')
  } finally {
    importFolderLoading.value = false
  }
}

const importFromExcel = async () => {
  try {
    importExcelLoading.value = true
    const response = await img2videoAPI.importExcel()
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '开始导入Excel')
      // 延迟刷新任务列表
      setTimeout(() => {
        loadTasks()
        loadStats()
      }, 2000)
    } else {
      ElMessage.error(response.data.message || '导入Excel失败')
    }
  } catch (error) {
    console.error('导入Excel失败:', error)
    ElMessage.error('导入Excel失败')
  } finally {
    importExcelLoading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection || []
}

const batchDeleteTasks = async () => {
  if (!selectedTasks.value || selectedTasks.value.length === 0) {
    ElMessage.warning('请先选择要删除的任务')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const taskIds = selectedTasks.value.map(task => task.id)
    const response = await img2videoAPI.batchDeleteTasks(taskIds)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '批量删除成功')
      selectedTasks.value = []
      await loadTasks()
      await loadStats()
    } else {
      ElMessage.error(response.data.message || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const batchDownloadVideos = async () => {
  if (!selectedCompletedTasks.value || selectedCompletedTasks.value.length === 0) {
    ElMessage.warning('请先选择已完成的任务')
    return
  }

  try {
    batchDownloadLoading.value = true
    const taskIds = selectedCompletedTasks.value.map(task => task.id)
    const response = await img2videoAPI.batchDownload(taskIds)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '开始批量下载')
    } else {
      ElMessage.error(response.data.message || '批量下载失败')
    }
  } catch (error) {
    console.error('批量下载失败:', error)
    ElMessage.error('批量下载失败')
  } finally {
    batchDownloadLoading.value = false
  }
}

const deleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await img2videoAPI.deleteTask(taskId)
    if (response.data.success) {
      ElMessage.success('删除成功')
      await loadTasks()
      await loadStats()
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }
}

const retryTask = async (taskId) => {
  try {
    const response = await img2videoAPI.retryTask(taskId)
    if (response.data.success) {
      ElMessage.success('任务已重新加入队列')
      await loadTasks()
      await loadStats()
    } else {
      ElMessage.error(response.data.message || '重试失败')
    }
  } catch (error) {
    console.error('重试任务失败:', error)
    ElMessage.error('重试任务失败')
  }
}

const previewImage = (imagePath) => {
  if (imagePath) {
    // 如果是本地路径，需要转换为可访问的URL
    if (imagePath.startsWith('/') || imagePath.includes(':\\')) {
      // 本地文件路径，无法直接预览
      ElMessage.warning('本地图片无法直接预览，请在文件管理器中查看')
      return
    }
    previewImageUrl.value = imagePath
    imagePreviewVisible.value = true
  }
}

const previewVideo = (videoUrl) => {
  if (videoUrl) {
    previewVideoUrl.value = videoUrl
    videoPreviewVisible.value = true
  }
}

const getImageFilename = (imagePath) => {
  if (!imagePath) return '-'
  return imagePath.split(/[/\\]/).pop() || imagePath
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getStatusType = (status) => {
  const statusTypeMap = {
    0: 'info',     // 排队中
    1: 'warning',  // 生成中  
    2: 'success',  // 已完成
    3: 'danger'    // 失败
  }
  return statusTypeMap[status] || 'info'
}

const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadTasks()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadTasks()
}

const handleStatusFilter = () => {
  pagination.page = 1
  loadTasks()
}

const refreshTasks = () => {
  loadTasks()
  loadStats()
}

const isTaskSelectable = (row) => {
  return true // 所有任务都可以选择
}

// 批量重试失败任务
const batchRetryFailedTasks = async () => {
  try {
    batchRetryLoading.value = true
    
    // 获取当前选中的失败任务
    const failedTaskIds = selectedTasks.value
      .filter(task => task.status === 3)
      .map(task => task.id)
    
    let response
    if (failedTaskIds.length > 0) {
      // 如果有选中的失败任务，只重试这些任务
      response = await img2videoAPI.batchRetryTasks(failedTaskIds)
      if (response.data.success) {
        ElMessage.success(`已重新加入队列 ${response.data.data.retry_count} 个任务`)
      } else {
        ElMessage.error(response.data.message || '批量重试失败')
      }
    } else {
      // 如果没有选中的失败任务，重试所有失败任务
      response = await img2videoAPI.batchRetryTasks()
      if (response.data.success) {
        ElMessage.success(`已重新加入队列 ${response.data.data.retry_count} 个任务`)
      } else {
        ElMessage.error(response.data.message || '批量重试失败')
      }
    }
    
    // 刷新任务列表
    refreshTasks()
  } catch (error) {
    console.error('批量重试失败:', error)
    ElMessage.error(error.response?.data?.message || '批量重试失败')
  } finally {
    batchRetryLoading.value = false
  }
}

// 删除今日前的所有任务
const deleteTasksBeforeToday = async () => {
  try {
    deleteBeforeTodayLoading.value = true
    const response = await img2videoAPI.deleteTasksBeforeToday()
    if (response.data.success) {
      ElMessage.success(response.data.message || '今日前的任务已删除')
      await loadTasks()
      await loadStats()
    } else {
      ElMessage.error(response.data.message || '删除今日前任务失败')
    }
  } catch (error) {
    console.error('删除今日前任务失败:', error)
    ElMessage.error(error.response?.data?.message || '删除今日前任务失败')
  } finally {
    deleteBeforeTodayLoading.value = false
  }
}

// 显示导入文件夹对话框
const showImportFolderDialog = () => {
  importFromFolder()
}

// 生命周期
    onMounted(() => {
  loadTasks()
      loadStats()
    })

onActivated(() => {
  loadTasks()
  loadStats()
})

onUnmounted(() => {
  // 清理数据
  tasks.value = []
  selectedTasks.value = []
  Object.assign(stats, {
    total_tasks: 0,
    pending_tasks: 0,
    processing_tasks: 0,
    completed_tasks: 0,
    failed_tasks: 0
  })
})

// 定时刷新
let refreshInterval = null
onMounted(() => {
  refreshInterval = setInterval(() => {
    loadStats()
    // 如果有处理中的任务，也刷新任务列表
    if (stats.processing_tasks > 0) {
      loadTasks()
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.jimeng-img2video-page {
  padding: 16px 24px;
  min-height: calc(100vh - 64px);
  height: 100%;
  overflow-y: auto;
}

/* 页面标题 */
.page-header {
  max-width: 1200px;
  margin: 0 auto 24px auto;
}

.header-content {
  background: var(--bg-primary);
  padding: 24px 32px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.header-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--primary-gradient);
  opacity: 0.03;
  z-index: -1;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  background: var(--primary-gradient);
  color: white;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.import-btn {
  background: var(--primary-gradient);
  border: none;
  color: white;
  border-radius: var(--radius-md);
  font-weight: 600;
  padding: 12px 24px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.import-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.import-btn.el-button--success {
  background: var(--success-gradient);
}

.import-btn.el-button--success:hover {
  background: var(--success-gradient);
}

/* 统计概览 */
.stats-overview {
  max-width: 1200px;
  margin: 0 auto 32px auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.stats-grid::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--secondary-gradient);
  opacity: 0.02;
  z-index: -1;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--primary-gradient);
  transition: var(--transition);
  opacity: 0.05;
  z-index: -1;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-card:hover::before {
  left: 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.stat-card.pending .stat-icon {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stat-card.processing .stat-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.stat-card.completed .stat-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stat-card.failed .stat-icon {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 任务管理 */
.task-management {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.panel-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.panel-title h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-filter {
  width: 120px;
}

.refresh-btn {
  padding: 8px 16px;
}

.refresh-btn:hover {
  background-color: #ebb563;
  border-color: #ebb563;
}

.delete-before-today-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;
}

.delete-before-today-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
}

/* 任务表格 */
.task-table-container {
  padding: 0;
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  overflow: hidden;
}

.modern-table {
  border: none;
  font-size: 14px;
}

.modern-table :deep(.el-table__header-wrapper) {
  border-radius: 0;
}

.modern-table :deep(.el-table__body-wrapper) {
  border-radius: 0;
}

.modern-table :deep(.el-table__row) {
  transition: var(--transition);
}

.modern-table :deep(.el-table__row:hover) {
  background-color: var(--bg-hover) !important;
}

.image-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.image-filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--text-secondary);
}

.preview-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.prompt-cell {
  padding: 8px 0;
}

.prompt-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.4;
  display: block;
}

.model-tag, .duration-tag {
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-sm);
}

.status-tag {
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 4px;
}

.processing-tag {
  animation: pulse 2s infinite;
}

.rotating-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.video-btn {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: var(--radius-sm);
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-btn {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: var(--radius-sm);
}

.no-content {
  color: var(--text-muted);
  font-size: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 24px;
  background: var(--bg-secondary);
}

.image-preview, .video-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-img2video-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
    padding: 20px 24px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .panel-title {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .toolbar-actions {
    justify-content: center;
  }
}
</style>