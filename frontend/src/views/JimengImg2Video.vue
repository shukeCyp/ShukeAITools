<template>
  <div class="jimeng-page">
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
          <ActionButton
            type="primary"
            size="large"
            @click="showImportFolderDialog"
            :loading="importFolderLoading"
            class="add-task-btn"
          >
            <template #icon>
              <el-icon><FolderOpened /></el-icon>
            </template>
            导入文件夹
          </ActionButton>
          
          <ActionButton
            type="success"
            size="large"
            @click="showBatchAddDialog"
            :loading="batchAddLoading"
            class="add-task-btn"
          >
            <template #icon>
              <el-icon><Plus /></el-icon>
            </template>
            批量添加
          </ActionButton>
          
          <ActionButton
            type="warning"
            size="large"
            @click="showTableImportDialog"
            :loading="tableImportLoading"
            class="add-task-btn"
          >
            <template #icon>
              <el-icon><Upload /></el-icon>
            </template>
            表格导入
          </ActionButton>
        </div>
      </div>
    </div>

    <!-- 统计概览 -->
    <StatusCountDisplay :stats="normalizedStats" />

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
          <ActionButton
            @click="refreshTasks"
            :loading="loading"
            class="refresh-btn"
          >
            <template #icon>
              <Refresh />
            </template>
            刷新
          </ActionButton>
          <!-- 批量重试按钮 -->
          <ActionButton
            type="warning"
            @click="batchRetryFailedTasks"
            :loading="batchRetryLoading"
            class="batch-retry-btn"
          >
            <template #icon>
              <RefreshRight />
            </template>
            批量重试
          </ActionButton>
          <!-- 批量操作按钮 -->
          <ActionButton
            type="danger"
            @click="batchDeleteTasks"
            :disabled="selectedTasks.length === 0"
          >
            <template #icon>
              <Delete />
            </template>
            批量删除 ({{ selectedTasks.length }})
          </ActionButton>
          
          <ActionButton
            type="success"
            @click="batchDownloadVideos"
            :disabled="selectedCompletedTasks.length === 0"
            :loading="batchDownloadLoading"
          >
            <template #icon>
              <Download />
            </template>
            批量下载 ({{ selectedCompletedTasks.length }})
          </ActionButton>
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

          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <!-- 失败原因图标 -->
                <el-tooltip 
                  v-if="row.status === 3" 
                  placement="top" 
                  :content="getFailureTooltipContent(row)" 
                  raw-content
                >
                  <el-icon class="failure-icon" size="18">
                    <CircleCloseFilled />
                  </el-icon>
                </el-tooltip>
                
                <!-- 查看视频按钮 -->
                <ActionButton
                  v-if="row.video_url"
                  size="small"
                  type="info"
                  @click="previewVideo(row.video_url)"
                  class="action-btn"
                >
                  <template #icon>
                    <VideoPlay />
                  </template>
                  查看
                </ActionButton>
                
                <!-- 下载视频按钮 -->
                <ActionButton
                  v-if="row.video_url"
                  size="small"
                  type="success"
                  @click="downloadVideo(row)"
                  class="action-btn"
                >
                  <template #icon>
                    <Download />
                  </template>
                  下载
                </ActionButton>
                
                <!-- 重试按钮 -->
                <ActionButton
                  v-if="row.status === 3"
                  size="small"
                  type="warning"
                  :disabled="row.status === 1"
                  @click="retryTask(row.id)"
                  class="action-btn"
                >
                  <template #icon>
                    <RefreshRight />
                  </template>
                  重试
                </ActionButton>
                
                <!-- 删除按钮 -->
                <ActionButton
                  size="small"
                  type="danger"
                  :disabled="row.status === 1"
                  @click="deleteTask(row.id)"
                  class="action-btn"
                >
                  删除
                </ActionButton>
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
        <el-form-item label="添加提示词">
          <el-switch v-model="importFolderForm.usePrompt" />
        </el-form-item>
        <el-form-item v-if="importFolderForm.usePrompt" label="提示词内容">
          <el-input
            v-model="importFolderForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入提示词，将应用于本次导入的所有任务"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <ActionButton @click="importFolderDialogVisible = false">取消</ActionButton>
          <ActionButton type="primary" @click="confirmImportFolder" :loading="importFolderLoading">
            确认并选择文件夹
          </ActionButton>
        </span>
      </template>
    </el-dialog>

    <!-- 批量添加对话框 -->
    <el-dialog
      v-model="batchAddDialogVisible"
      width="40%"
      max-width="600px"
      destroy-on-close
      :show-close="false"
      :show-header="false"
      class="batch-add-dialog"
      @close="resetBatchAddDialog"
    >
      <div 
        class="batch-add-wrapper"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        :class="{ 'drag-over': isDragOver }"
      >
        <div class="batch-add-scrollable">
          <input 
            ref="fileInput"
            type="file"
            multiple
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />

          <!-- 生成设置 -->
          <div class="generation-settings-compact">
            <div class="settings-row-compact">
              <el-form-item label="模型：" class="compact-form-item">
                <el-radio-group v-model="batchAddForm.model" size="small">
                  <el-radio value="Video 3.0">Video 3.0</el-radio>
                  <el-radio value="Video S2.0 Pro">Video S2.0 Pro</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="时长：" class="compact-form-item">
                <el-radio-group v-model="batchAddForm.second" size="small">
                  <el-radio :value="5">5秒</el-radio>
                  <el-radio :value="10" v-if="batchAddForm.model === 'Video 3.0'">10秒</el-radio>
                </el-radio-group>
              </el-form-item>
            </div>
          </div>

          <!-- 拖拽上传区域 -->
          <div 
            class="drag-upload-area"
            v-show="imageTaskList.length === 0"
            @click="triggerFileInput"
          >
            <div class="upload-content">
              <el-icon size="48" class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">
                <p class="primary-text">拖拽图片到此处，或点击选择图片</p>
                <p class="secondary-text">支持 jpg、png、gif 等格式</p>
              </div>
            </div>
          </div>

          <!-- 图片任务列表 -->
          <div class="image-task-list" v-if="imageTaskList.length > 0">
            <div class="list-header">
              <h4>待生成任务 ({{ imageTaskList.length }})</h4>
              <div class="header-actions">
                <ActionButton size="small" @click="clearAllTasks" type="danger">
                  <template #icon>
                    <Delete />
                  </template>
                  清空
                </ActionButton>
              </div>
            </div>
            
            <div 
              class="task-pagination-container" 
              ref="paginationContainer"
              @touchstart="handleTouchStart"
              @touchmove="handleTouchMove"
              @touchend="handleTouchEnd"
              @wheel="handleWheel"
            >
              <div 
                class="task-pagination-wrapper" 
                :style="{ transform: `translateY(-${currentPage * 100}%)` }"
              >
                <div 
                  v-for="(task, index) in imageTaskList" 
                  :key="index"
                  class="task-page"
                >
                  <div class="task-item">
                    <div class="task-image-container">
                      <div class="task-image">
                        <img :src="task.previewUrl" :alt="task.file.name" />
                      </div>
                    </div>
                    <div class="task-content">
                      <div class="task-prompt-container">
                        <el-input
                          v-model="task.prompt"
                          type="textarea"
                          :rows="13"
                          placeholder="请输入提示词（可选）"
                          maxlength="500"
                          show-word-limit
                          class="prompt-textarea"
                        />
                        <div class="button-group">
                          <ActionButton
                            size="small"
                            type="primary"
                            @click="generateAIPrompt(index)"
                            class="ai-generate-btn"
                          >
                            <template #icon>
                              <Magic />
                            </template>
                            AI生成
                          </ActionButton>
                          <ActionButton
                            size="small"
                            text
                            @click="removeTask(index)"
                            class="delete-text-btn"
                          >
                            删除
                          </ActionButton>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <ActionButton @click="batchAddDialogVisible = false">取消</ActionButton>
          <ActionButton
            type="primary"
            @click="submitBatchTasks"
            :loading="batchAddLoading"
            :disabled="imageTaskList.length === 0"
          >
            <template #icon>
              <Plus />
            </template>
            创建任务 ({{ imageTaskList.length }})
          </ActionButton>
        </span>
      </template>
    </el-dialog>

    <!-- 表格导入对话框 -->
    <el-dialog
      v-model="tableImportDialogVisible"
      title="表格导入"
      width="80%"
      max-width="1000px"
      destroy-on-close
      @close="resetTableImportDialog"
    >
      <div class="table-import-container">
        <!-- 文件选择区域 -->
        <div class="file-select-area" v-if="tableData.length === 0">
          <input 
            ref="tableFileInput"
            type="file"
            accept=".csv,.xlsx,.xls"
            style="display: none"
            @change="handleTableFileSelect"
          />
          <div 
            class="upload-drag-area" 
            @click="triggerTableFileInput"
            @drop="handleTableFileDrop"
            @dragover.prevent
            @dragenter.prevent
          >
            <div class="upload-content">
              <el-icon size="64" class="upload-icon"><Upload /></el-icon>
              <div class="upload-text">
                <h3 class="primary-text">点击选择表格文件或拖拽到此处</h3>
                <p class="secondary-text">支持 CSV、Excel (.xlsx, .xls) 格式</p>
                <p class="hint-text">固定格式: 图片路径 | 提示词 | 秒数</p>
                <div class="template-download">
                  <ActionButton
                    type="primary"
                    size="small"
                    @click.stop="downloadTemplate"
                    plain
                  >
                    <template #icon>
                      <Download />
                    </template>
                    下载表格模板
                  </ActionButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据预览区域 -->
        <div class="data-preview-area" v-if="tableData.length > 0">


          <!-- 数据预览 -->
          <div class="data-preview">
            <div class="preview-header">
              <h4>数据预览 (共 {{ tableData.length }} 行，显示前 10 行)</h4>
              <ActionButton size="small" @click="resetTableImportDialog">
                <template #icon>
                  <Close />
                </template>
                重新选择文件
              </ActionButton>
            </div>
            
            <div class="preview-table">
              <el-table :data="previewData" border stripe max-height="300">
                <el-table-column 
                  v-for="header in tableHeaders" 
                  :key="header" 
                  :prop="header" 
                  :label="header"
                  min-width="120"
                  show-overflow-tooltip
                >
                  <template #default="{ row }">
                    <span>{{ row[header] }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <ActionButton @click="tableImportDialogVisible = false">取消</ActionButton>
          <ActionButton
            type="primary"
            @click="submitTableImportTasks"
            :loading="tableImportLoading"
            :disabled="tableData.length === 0"
          >
            <template #icon>
              <Plus />
            </template>
            创建任务 ({{ tableData.length }})
          </ActionButton>
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
  Delete, 
  Download,
  Refresh,
  RefreshRight,
  Plus,
  UploadFilled,
  Upload,
  Close,
  MagicStick as Magic,
  CircleCloseFilled,
  Loading
} from '@element-plus/icons-vue'
import { img2videoAPI } from '@/utils/api'
import * as ElementPlus from 'element-plus'
import * as XLSX from 'xlsx'
import StatusCountDisplay from '@/components/StatusCountDisplay.vue'
import ActionButton from '@/components/common/ActionButton.vue'

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

// 统一数据格式的计算属性
const normalizedStats = computed(() => ({
  total: stats.total_tasks || 0,
  queued: stats.pending_tasks || 0,
  processing: stats.processing_tasks || 0,
  completed: stats.completed_tasks || 0,
  failed: stats.failed_tasks || 0
}))

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
    })

// 导入相关状态
const importFolderLoading = ref(false)
const batchDownloadLoading = ref(false)

// 批量添加相关状态
const batchAddLoading = ref(false)
const batchAddDialogVisible = ref(false)
const isDragOver = ref(false)
const imageTaskList = ref([])
const fileInput = ref(null)
const currentPage = ref(0)
const paginationContainer = ref(null)

// 批量重试状态
const batchRetryLoading = ref(false)

// 表格导入相关状态
const tableImportLoading = ref(false)
const tableImportDialogVisible = ref(false)
const tableFileInput = ref(null)
const tableData = ref([])
const tableHeaders = ref([])
const previewData = ref([])
const importSettings = reactive({
  model: 'Video 3.0',
  defaultDuration: 5
})



// 预览相关状态
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')
const videoPreviewVisible = ref(false)
const previewVideoUrl = ref('')

// 导入文件夹对话框状态
const importFolderDialogVisible = ref(false)
const importFolderForm = reactive({
  model: 'Video 3.0',
  second: 5,
  usePrompt: false,
  prompt: ''
})

// 批量添加表单数据
const batchAddForm = reactive({
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



// 显示批量添加对话框
const showBatchAddDialog = () => {
  batchAddDialogVisible.value = true
}

// 重置批量添加对话框
const resetBatchAddDialog = () => {
  imageTaskList.value = []
  isDragOver.value = false
  batchAddForm.model = 'Video 3.0'
  batchAddForm.second = 5
  resetPagination()
}

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addFilesToTaskList(files)
  // 清空input，允许重复选择同一文件
  event.target.value = ''
}

// 处理拖拽悬停
const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

// 处理拖拽离开
const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

// 处理拖拽放下
const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer?.files || [])
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  
  if (imageFiles.length !== files.length) {
    ElMessage.warning('只支持图片文件，其他类型文件已被过滤')
  }
  
  if (imageFiles.length > 0) {
    addFilesToTaskList(imageFiles)
  }
}

// 添加文件到任务列表
const addFilesToTaskList = (files) => {
  files.forEach(file => {
    if (!file.type.startsWith('image/')) {
      return
    }
    
    // 检查是否已存在相同文件
    const exists = imageTaskList.value.some(task => 
      task.file.name === file.name && task.file.size === file.size
    )
    
    if (!exists) {
      const previewUrl = URL.createObjectURL(file)
      imageTaskList.value.push({
        file,
        previewUrl,
        prompt: ''
      })
    }
  })
  
  if (files.length > 0) {
    ElMessage.success(`已添加 ${files.length} 个图片`)
  }
}

// 移除任务
const removeTask = (index) => {
  const task = imageTaskList.value[index]
  if (task.previewUrl) {
    URL.revokeObjectURL(task.previewUrl)
  }
  imageTaskList.value.splice(index, 1)
}

// 清空所有任务
const clearAllTasks = () => {
  imageTaskList.value.forEach(task => {
    if (task.previewUrl) {
      URL.revokeObjectURL(task.previewUrl)
    }
  })
  imageTaskList.value = []
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// AI生成提示词
const generateAIPrompt = (index) => {
  ElMessage.info('功能正在开发中，敬请期待！')
}

// 分页滑动相关
let touchStartY = 0
let touchEndY = 0

const handleTouchStart = (event) => {
  touchStartY = event.touches[0].clientY
}

const handleTouchMove = (event) => {
  event.preventDefault()
}

const handleTouchEnd = (event) => {
  touchEndY = event.changedTouches[0].clientY
  handleSwipe()
}

const handleWheel = (event) => {
  event.preventDefault()
  if (event.deltaY > 0) {
    nextPage()
  } else {
    prevPage()
  }
}

const handleSwipe = () => {
  const swipeThreshold = 50
  const diff = touchStartY - touchEndY
  
  if (Math.abs(diff) > swipeThreshold) {
    if (diff > 0) {
      nextPage()
    } else {
      prevPage()
    }
  }
}

const nextPage = () => {
  if (currentPage.value < imageTaskList.value.length - 1) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
  }
}

// 重置分页
const resetPagination = () => {
  currentPage.value = 0
}

// 提交批量任务
const submitBatchTasks = async () => {
  if (imageTaskList.value.length === 0) {
    ElMessage.warning('请先添加图片')
    return
  }

  try {
    batchAddLoading.value = true
    
    // 创建FormData对象
    const formData = new FormData()
    
    // 添加配置参数
    formData.append('model', batchAddForm.model)
    formData.append('second', batchAddForm.second)
    
    // 添加所有图片文件和对应的提示词
    imageTaskList.value.forEach((task, index) => {
      formData.append('images', task.file)
      formData.append(`prompts[${index}]`, task.prompt || '')
    })
    
    const response = await img2videoAPI.batchAddTasks(formData)
    
    if (response.data.success) {
      ElMessage.success(`成功创建 ${imageTaskList.value.length} 个任务`)
      batchAddDialogVisible.value = false
      resetBatchAddDialog()
      
      // 刷新任务列表
      setTimeout(() => {
        loadTasks()
        loadStats()
      }, 1000)
    } else {
      ElMessage.error(response.data.message || '创建任务失败')
    }
  } catch (error) {
    console.error('创建批量任务失败:', error)
    ElMessage.error('创建任务失败')
  } finally {
    batchAddLoading.value = false
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

const downloadVideo = async (row) => {
  if (!row.video_url) {
    ElMessage.warning('没有可下载的视频')
    return
  }
  
  try {
    // 创建一个临时的a标签来触发下载
    const link = document.createElement('a')
    link.href = row.video_url
    link.download = `video_${row.id}.mp4`
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('开始下载视频')
  } catch (error) {
    console.error('下载视频失败:', error)
    ElMessage.error('下载视频失败')
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

// 获取失败原因文本
const getFailureReasonText = (reason) => {
  switch (reason) {
    case 'WEB_INTERACTION_FAILED':
      return '网页交互失败'
    case 'TASK_ID_NOT_OBTAINED':
      return '任务ID获取失败'
    case 'GENERATION_FAILED':
      return '生成失败'
    case 'OTHER_ERROR':
      return '其他错误'
    default:
      return reason || '未知错误'
  }
}

// 获取失败原因tooltip内容
const getFailureTooltipContent = (row) => {
  const reasonText = getFailureReasonText(row.failure_reason)
  if (row.error_message) {
    return `<div><strong>失败原因:</strong> ${reasonText}</div><div><strong>详细信息:</strong> ${row.error_message}</div>`
  }
  return `<div><strong>失败原因:</strong> ${reasonText}</div>`
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

    // 批量重试
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



// 显示导入文件夹对话框
const showImportFolderDialog = () => {
  importFolderDialogVisible.value = true
}

// 显示表格导入对话框
const showTableImportDialog = () => {
  tableImportDialogVisible.value = true
}

// 触发表格文件选择
const triggerTableFileInput = () => {
  tableFileInput.value?.click()
}

// 处理表格文件选择
const handleTableFileSelect = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  try {
    tableImportLoading.value = true
    await parseTableFile(file)
  } catch (error) {
    console.error('解析表格文件失败:', error)
    ElMessage.error('解析表格文件失败')
  } finally {
    tableImportLoading.value = false
    event.target.value = ''
  }
}

// 处理表格文件拖拽
const handleTableFileDrop = async (event) => {
  event.preventDefault()
  const files = event.dataTransfer?.files
  if (!files || files.length === 0) return
  
  const file = files[0]
  try {
    tableImportLoading.value = true
    await parseTableFile(file)
  } catch (error) {
    console.error('解析表格文件失败:', error)
    ElMessage.error('解析表格文件失败')
  } finally {
    tableImportLoading.value = false
  }
}

// 解析表格文件
const parseTableFile = async (file) => {
  const fileExtension = file.name.split('.').pop()?.toLowerCase()
  
  if (!['csv', 'xlsx', 'xls'].includes(fileExtension)) {
    throw new Error('不支持的文件格式，请选择CSV或Excel文件')
  }
  
  if (fileExtension === 'csv') {
    await parseCSVFile(file)
  } else {
    await parseExcelFile(file)
  }
}

// 解析CSV文件
const parseCSVFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const text = e.target?.result
        const lines = text.split('\n').filter(line => line.trim())
        
        if (lines.length < 2) {
          reject(new Error('表格数据不完整'))
          return
        }
        
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
        const data = lines.slice(1).map(line => {
          const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
          const row = {}
          headers.forEach((header, index) => {
            row[header] = values[index] || ''
          })
          return row
        })
        
        tableHeaders.value = headers
        tableData.value = data
        previewData.value = data.slice(0, 10) // 只预览前10行
        
        ElMessage.success(`成功解析 ${data.length} 行数据`)
        resolve(data)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsText(file, 'utf-8')
  })
}

// 解析Excel文件
const parseExcelFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const arrayBuffer = new Uint8Array(e.target?.result)
        const workbook = XLSX.read(arrayBuffer, { type: 'array' })
        
        // 获取第一个工作表
        const firstSheetName = workbook.SheetNames[0]
        if (!firstSheetName) {
          reject(new Error('Excel文件中没有找到工作表'))
          return
        }
        
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
        
        if (jsonData.length < 2) {
          reject(new Error('表格数据不完整'))
          return
        }
        
        // 获取表头和数据
        const headers = jsonData[0].map(h => String(h).trim())
        const rows = jsonData.slice(1).map(row => {
          const rowData = {}
          headers.forEach((header, index) => {
            rowData[header] = String(row[index] || '').trim()
          })
          return rowData
        }).filter(row => {
          // 过滤掉空行
          return Object.values(row).some(value => value !== '')
        })
        
        tableHeaders.value = headers
        tableData.value = rows
        previewData.value = rows.slice(0, 10) // 只预览前10行
        
        resolve()
      } catch (error) {
        reject(new Error('Excel文件解析失败: ' + error.message))
      }
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

// 自动识别列


// 重置表格导入对话框
const resetTableImportDialog = () => {
  tableData.value = []
  tableHeaders.value = []
  previewData.value = []
  importSettings.model = 'Video 3.0'
  importSettings.defaultDuration = 5
}

// 提交表格导入任务
const submitTableImportTasks = async () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('请先选择并解析表格文件')
    return
  }
  
  if (tableHeaders.value.length < 3) {
    ElMessage.warning('表格至少需要3列：图片路径、提示词、秒数')
    return
  }
  
  try {
    tableImportLoading.value = true
    
    // 按固定格式构建任务列表：第1列图片路径，第2列提示词，第3列秒数
    const tasks = tableData.value.map(row => {
      const rowValues = Object.values(row)
      return {
        image_path: rowValues[0] || '',
        prompt: rowValues[1] || '',
        model: importSettings.model,
        second: parseInt(rowValues[2]) || importSettings.defaultDuration
      }
    }).filter(task => task.image_path.trim() !== '') // 过滤空的图片路径
    
    if (tasks.length === 0) {
      ElMessage.warning('没有有效的任务数据')
      return
    }
    
    // 调用API批量创建任务
    const response = await img2videoAPI.batchCreateTasksFromTable(tasks)
    
    if (response.data.success) {
      ElMessage.success(`成功创建 ${tasks.length} 个任务`)
      tableImportDialogVisible.value = false
      resetTableImportDialog()
      
      // 刷新任务列表
      setTimeout(() => {
        loadTasks()
        loadStats()
      }, 1000)
    } else {
      ElMessage.error(response.data.message || '创建任务失败')
    }
  } catch (error) {
    console.error('表格导入失败:', error)
    ElMessage.error('表格导入失败')
  } finally {
    tableImportLoading.value = false
  }
}

// 确认导入文件夹
const confirmImportFolder = async () => {
  try {
    importFolderLoading.value = true
    const model = importFolderForm.model
    const second = importFolderForm.second
    const usePrompt = importFolderForm.usePrompt
    const prompt = importFolderForm.prompt

    const response = await img2videoAPI.importFolder({
      model,
      second,
      usePrompt,
      prompt
    })

         if (response.data.success) {
       ElMessage.success("文件选择器已调用打开，请小化浏览器返回桌面选择文件夹")
       ElMessage.info(`使用模型: ${model}，时长: ${second}秒${usePrompt ? '，添加提示词' : ''}`)
       if (prompt) {
         ElMessage.info(`提示词: ${prompt}`)
       }
       // 延迟刷新任务列表
       setTimeout(() => {
         loadTasks()
         loadStats()
       }, 2000)
       importFolderDialogVisible.value = false
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

// 下载表格模板
const downloadTemplate = () => {
  // 创建CSV数据 - 只包含表头
  const headers = ['图片路径', '提示词', '秒数']
  
  // 构建CSV内容 - 只有表头行，添加BOM以支持Excel正确显示中文
  const BOM = '\uFEFF'
  const csvContent = BOM + headers.join(',')
  
  // 创建Blob对象，使用UTF-8编码
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  
  // 创建下载链接
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', '图片转视频导入模板.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('模板下载成功')
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
@import '../styles/jimeng-common.css';

/* 页面特定样式 */
.status-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 导入按钮特定样式 */
.import-btn.el-button--success {
  background: var(--success-gradient);
}

.import-btn.el-button--success:hover {
  background: var(--success-gradient);
}

/* 任务管理特定样式 */
.panel-title {
  padding: 24px 32px;
  background: var(--bg-secondary);
}

.refresh-btn {
  padding: 8px 16px;
}

.refresh-btn:hover {
  background-color: #ebb563;
  border-color: #ebb563;
}



/* 图生视频特定样式 */
.image-filename {
  font-size: 13px;
}

.prompt-text {
  font-size: 13px;
  line-height: 1.4;
}

.no-content {
  color: var(--text-muted);
  font-size: 12px;
}

/* 图生视频特定对话框样式 */
.task-item {
  min-height: 280px;
  max-width: 600px;
  width: 95%;
  margin: 0 auto;
  align-items: stretch;
  box-sizing: border-box;
}



/* 图生视频任务特定样式 */
.task-image-container {
  max-width: 200px;
}

.task-image {
  min-height: 200px;
}

.task-content {
  flex: 2;
  padding: 0 16px;
}

.ai-generate-btn {
  white-space: nowrap;
}

.delete-text-btn {
  color: #f56c6c;
  white-space: nowrap;
}

.delete-text-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

/* 图生视频分页特定样式 */
.task-pagination-container {
  height: 350px;
  touch-action: pan-y;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

/* 图生视频响应式样式 */
@media (max-width: 768px) {
  .task-item {
    flex-direction: column;
  }

  .task-image {
    width: 100%;
    height: 120px;
    align-self: center;
  }
}

/* 图生视频失败图标样式 */
.failure-icon {
  color: #f56c6c;
  cursor: help;
  transition: all 0.3s ease;
  border-radius: 50%;
  background: rgba(245, 108, 108, 0.1);
  padding: 2px;
}

.failure-icon:hover {
  color: #e74c3c;
  background: rgba(245, 108, 108, 0.2);
  transform: scale(1.1);
}

/* 操作列按钮布局 */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px;
}

/* 操作按钮样式 */
.action-btn {
  font-size: 12px;
  padding: 4px 8px;
  min-width: auto;
}

.action-btn .el-icon {
  margin-right: 4px;
}

/* 表格导入弹窗样式 */
.table-import-container {
  min-height: 200px;
}

.file-select-area {
  margin: 20px 0;
}

.upload-drag-area {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #fafbfc;
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-drag-area:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.upload-content {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  color: #c0c4cc;
  margin-bottom: 20px;
  transition: color 0.3s ease;
}

.upload-drag-area:hover .upload-icon {
  color: #409eff;
}

.upload-text {
  color: #606266;
}

.upload-text .primary-text {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 12px 0;
}

.upload-text .secondary-text {
  font-size: 14px;
  color: #909399;
  margin: 8px 0;
}

.upload-text .hint-text {
  font-size: 13px;
  color: #c0c4cc;
  margin: 8px 0 20px 0;
}

.template-download {
  margin-top: 16px;
}

.data-preview-area {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.preview-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}






</style>