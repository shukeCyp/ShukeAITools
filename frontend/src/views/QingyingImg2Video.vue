<template>
  <div class="qingying-img2video-page">

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><VideoCamera /></el-icon>
          </div>
          <h1 class="page-title">智谱清影图生视频</h1>
        </div>
        <div class="status-section">
          <!-- 导入文件夹按钮 -->
          <el-button 
            type="primary" 
            size="large"
            @click="showImportFolderDialog = true"
            :loading="importFolderLoading"
            class="import-btn"
          >
            <el-icon><FolderOpened /></el-icon>
            导入文件夹
          </el-button>
          
          <el-button 
            type="success" 
            size="large"
            @click="showBatchAddDialog"
            :loading="batchAddLoading"
            class="import-btn"
          >
            <el-icon><Plus /></el-icon>
            批量添加
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
            @click="batchRetryTasks"
            :loading="batchRetryLoading"
            class="batch-retry-btn"
          >
            <el-icon><RefreshRight /></el-icon>
            批量重试失败任务
          </el-button>
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
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="prompt" label="提示词" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="prompt-content">{{ row.prompt || '-' }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="params" label="参数" width="160" align="center">
            <template #default="{ row }">
              <div class="param-info">
                <el-tag size="small" type="primary">{{ row.generation_mode || '-' }}</el-tag>
                <el-tag size="small" type="warning">{{ row.frame_rate }}FPS</el-tag>
                <el-tag size="small" type="success">{{ row.resolution }}</el-tag>
                <el-tag size="small" type="info">{{ row.duration }}</el-tag>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getStatusType(row.status)"
                :class="['status-tag', { 'processing-tag': row.status === 1 }]"
              >
                <el-icon v-if="row.status === 1" class="rotating-icon"><Loading /></el-icon>
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right" align="center">
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
                
                <el-button 
                  v-if="row.status === 3"
                  type="warning" 
                  size="small"
                  @click="retryTask(row)"
                  class="action-btn"
                >
                  <el-icon><RefreshRight /></el-icon>
                  重试
                </el-button>
                <el-button 
                  v-if="row.status === 2 && row.video_url"
                  type="success" 
                  size="small"
                  @click="openVideo(row.video_url)"
                  class="action-btn"
                >
                  <el-icon><VideoPlay /></el-icon>
                  查看
                </el-button>
                <el-popconfirm
                  title="确定要删除这个任务吗？"
                  @confirm="deleteTask(row.id)"
                >
                  <template #reference>
                    <el-button 
                      type="danger" 
                      size="small"
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
        <div class="pagination-container">
          <el-pagination
            :current-page="pagination.page"
            :page-size="pagination.page_size"
            :page-sizes="[10, 20, 50, 100, 500, 1000]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建智谱清影图生视频任务"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" :rules="createFormRules" ref="createFormRef" label-width="120px">
        <el-form-item label="上传图片" prop="image" required>
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept="image/*"
            :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将图片拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 jpg/png/gif 格式，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="提示词" prop="prompt" required>
          <el-input
            v-model="createForm.prompt"
            type="textarea"
            :rows="3"
            placeholder="请输入视频生成提示词，描述您希望生成的视频内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="生成模式" prop="generation_mode">
          <el-radio-group v-model="createForm.generation_mode">
            <el-radio value="fast">速度更快</el-radio>
            <el-radio value="quality">质量更佳</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频帧率" prop="frame_rate">
          <el-radio-group v-model="createForm.frame_rate">
            <el-radio value="30">30 FPS</el-radio>
            <el-radio value="60">60 FPS</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频分辨率" prop="resolution">
          <el-radio-group v-model="createForm.resolution">
            <el-radio value="720p">720P</el-radio>
            <el-radio value="1080p">1080P</el-radio>
            <el-radio value="4k">4K</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频时长" prop="duration">
          <el-radio-group v-model="createForm.duration">
            <el-radio value="5s">5秒</el-radio>
            <el-radio value="10s">10秒</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="AI音效" prop="ai_audio">
          <el-switch v-model="createForm.ai_audio" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="createTask"
            :loading="createLoading"
          >
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入文件夹参数对话框 -->
    <el-dialog
      v-model="showImportFolderDialog"
      title="导入文件夹参数设置"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="importFolderForm" ref="importFolderFormRef" label-width="120px">
        <el-form-item label="生成模式" prop="generation_mode">
          <el-radio-group v-model="importFolderForm.generation_mode">
            <el-radio value="fast">速度更快</el-radio>
            <el-radio value="quality">质量更佳</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频帧率" prop="frame_rate">
          <el-radio-group v-model="importFolderForm.frame_rate">
            <el-radio value="30">30 FPS</el-radio>
            <el-radio value="60">60 FPS</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频分辨率" prop="resolution">
          <el-radio-group v-model="importFolderForm.resolution">
            <el-radio value="720p">720P</el-radio>
            <el-radio value="1080p">1080P</el-radio>
            <el-radio value="4k">4K</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="视频时长" prop="duration">
          <el-radio-group v-model="importFolderForm.duration">
            <el-radio value="5s">5秒</el-radio>
            <el-radio value="10s">10秒</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="AI音效" prop="ai_audio">
          <el-switch v-model="importFolderForm.ai_audio" />
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
        <div class="dialog-footer">
          <el-button @click="showImportFolderDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmImportFolder"
            :loading="importFolderLoading"
          >
            确定并选择文件夹
          </el-button>
        </div>
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
          <div class="settings-grid-compact">
            <el-form-item label="模式：" class="compact-form-item">
              <el-radio-group v-model="batchAddForm.generation_mode" size="small">
                <el-radio value="fast">速度更快</el-radio>
                <el-radio value="quality">质量更佳</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="帧率：" class="compact-form-item">
              <el-radio-group v-model="batchAddForm.frame_rate" size="small">
                <el-radio value="30">30 FPS</el-radio>
                <el-radio value="60">60 FPS</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="分辨率：" class="compact-form-item">
              <el-radio-group v-model="batchAddForm.resolution" size="small">
                <el-radio value="720p">720P</el-radio>
                <el-radio value="1080p">1080P</el-radio>
                <el-radio value="4k">4K</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="时长：" class="compact-form-item">
              <el-radio-group v-model="batchAddForm.duration" size="small">
                <el-radio value="5s">5秒</el-radio>
                <el-radio value="10s">10秒</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="AI音效：" class="compact-form-item">
              <el-switch v-model="batchAddForm.ai_audio" size="small" />
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
            <el-icon size="48" class="upload-icon"><Upload /></el-icon>
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
              <el-button size="small" @click="clearAllTasks" type="danger">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
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
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="generateAIPrompt(index)"
                      class="ai-generate-btn"
                    >
                      <el-icon><Magic /></el-icon>
                      AI生成
                    </el-button>
                    <el-button 
                      size="small" 
                      type="text" 
                      @click="removeTask(index)" 
                      class="delete-text-btn"
                    >
                      删除
                    </el-button>
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
          <el-button @click="batchAddDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitBatchTasks" 
            :loading="batchAddLoading"
            :disabled="imageTaskList.length === 0"
          >
            <el-icon><Plus /></el-icon>
            创建任务 ({{ imageTaskList.length }})
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, 
  Clock, 
  Loading, 
  Select, 
  Close, 
  Plus, 
  Refresh, 
  RefreshRight, 
  Delete, 
  Upload, 
  Picture,
  Download,
  FolderOpened,
  VideoCamera,
  CircleCheckFilled,
  CircleCloseFilled,
  VideoPlay,
  MagicStick as Magic
} from '@element-plus/icons-vue'
import { qingyingImg2videoAPI } from '@/utils/api'

// 响应式数据
const loading = ref(false)
const tasks = ref([])
const selectedTasks = ref([])

const stats = reactive({
  total_tasks: 0,
  today_tasks: 0,
  pending_tasks: 0,
  processing_tasks: 0,
  completed_tasks: 0,
  failed_tasks: 0
})

// 分页数据
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 创建任务相关
const showCreateDialog = ref(false)
const createLoading = ref(false)
const createFormRef = ref()
const uploadRef = ref()

const createForm = reactive({
  image: null,
  prompt: '',
  generation_mode: 'fast',
  frame_rate: '30',
  resolution: '720p',
  duration: '5s',
  ai_audio: false
})

const createFormRules = {
  image: [
    { required: true, message: '请选择要上传的图片', trigger: 'change' }
  ],
  prompt: [
    { required: true, message: '请输入提示词', trigger: 'blur' },
    { min: 1, max: 500, message: '提示词长度在 1 到 500 个字符', trigger: 'blur' }
  ]
}

// 操作相关
const batchRetryLoading = ref(false)
const batchDownloadLoading = ref(false)
const importFolderLoading = ref(false)

// 批量添加相关状态
const batchAddLoading = ref(false)
const batchAddDialogVisible = ref(false)
const isDragOver = ref(false)
const imageTaskList = ref([])
const fileInput = ref(null)
const currentPage = ref(0)
const paginationContainer = ref(null)

// 导入文件夹相关
const showImportFolderDialog = ref(false)
const importFolderFormRef = ref()
const importFolderForm = reactive({
  generation_mode: 'fast',
  frame_rate: '30',
  resolution: '720p',
  duration: '5s',
  ai_audio: false,
  usePrompt: false,
  prompt: ''
})

// 批量添加表单数据
const batchAddForm = reactive({
  generation_mode: 'fast',
  frame_rate: '30',
  resolution: '720p',
  duration: '5s',
  ai_audio: false
})



// 筛选相关
const statusFilter = ref(null)

// 文件列表
const fileList = ref([])

// 计算属性
const selectedCompletedTasks = computed(() => {
  return selectedTasks.value.filter(task => task.status === 2 && task.video_url)
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
    
    const response = await qingyingImg2videoAPI.getTasks(params)
    
    if (response.data.success) {
      tasks.value = response.data.data || []
      pagination.total = response.data.pagination?.total || 0
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
    const response = await qingyingImg2videoAPI.getStats()
    if (response.data.success) {
      Object.assign(stats, response.data.data)
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const getStatusType = (status) => {
  const statusTypes = {
    0: 'info',     // 排队中
    1: 'warning',  // 生成中
    2: 'success',  // 已完成
    3: 'danger'    // 失败
  }
  return statusTypes[status] || 'info'
}

const getStatusText = (status) => {
  const statusTexts = {
    0: '排队中',
    1: '生成中',
    2: '已完成',
    3: '失败'
  }
  return statusTexts[status] || '未知'
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

// 截断文本函数
const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 获取失败原因tooltip内容
const getFailureTooltipContent = (row) => {
  const reasonText = getFailureReasonText(row.failure_reason)
  if (row.error_message) {
    return `<div><strong>失败原因:</strong> ${reasonText}</div><div><strong>详细信息:</strong> ${row.error_message}</div>`
  }
  return `<div><strong>失败原因:</strong> ${reasonText}</div>`
}

const getImageFilename = (imagePath) => {
  if (!imagePath) return '-'
  return imagePath.split('/').pop() || imagePath
}

const handleFileChange = (file) => {
  createForm.image = file.raw
}

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const isTaskSelectable = (row) => {
  return true // 允许选择所有任务
}

const previewImage = (imagePath) => {
  if (imagePath) {
    const imageUrl = `data:image/jpeg;base64,${imagePath}`
    window.open(imageUrl, '_blank')
  }
}

const refreshTasks = async () => {
  await loadTasks()
  await loadStats()
}

const createTask = async () => {
  if (!createFormRef.value) return
  
  try {
    const valid = await createFormRef.value.validate()
    if (!valid) return
    
    if (!createForm.image) {
      ElMessage.error('请选择要上传的图片')
      return
    }
    
    createLoading.value = true
    
    const formData = new FormData()
    formData.append('image', createForm.image)
    formData.append('prompt', createForm.prompt)
    formData.append('generation_mode', createForm.generation_mode)
    formData.append('frame_rate', createForm.frame_rate)
    formData.append('resolution', createForm.resolution)
    formData.append('duration', createForm.duration)
    formData.append('ai_audio', createForm.ai_audio)
    
    const response = await qingyingImg2videoAPI.createTask(formData)
    
    if (response.data.success) {
      ElMessage.success('任务创建成功')
      showCreateDialog.value = false
      
      // 重置表单
      createFormRef.value.resetFields()
      createForm.image = null
      fileList.value = []
      
      await refreshTasks()
    } else {
      ElMessage.error(response.data.message || '任务创建失败')
    }
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error('创建任务失败')
  } finally {
    createLoading.value = false
  }
}

const retryTask = async (task) => {
  try {
    task.retrying = true
    
    const response = await qingyingImg2videoAPI.retryTask(task.id)
    
    if (response.data.success) {
      ElMessage.success('重试任务成功')
      await refreshTasks()
    } else {
      ElMessage.error(response.data.message || '重试任务失败')
    }
  } catch (error) {
    console.error('重试任务失败:', error)
    ElMessage.error('重试任务失败')
  } finally {
    task.retrying = false
  }
}

const deleteTask = async (taskId) => {
  try {
    const response = await qingyingImg2videoAPI.deleteTask(taskId)
    
    if (response.data.success) {
      ElMessage.success('删除任务成功')
      await refreshTasks()
    } else {
      ElMessage.error(response.data.message || '删除任务失败')
    }
  } catch (error) {
    console.error('删除任务失败:', error)
    ElMessage.error('删除任务失败')
  }
}

const batchRetryTasks = async () => {
  const failedTasks = tasks.value.filter(task => task.status === 3)
  
  if (failedTasks.length === 0) {
    ElMessage.warning('没有失败的任务需要重试')
    return
  }
  
  try {
    batchRetryLoading.value = true
    
    const taskIds = failedTasks.map(task => task.id)
    const response = await qingyingImg2videoAPI.batchRetryTasks(taskIds)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '批量重试成功')
      await refreshTasks()
    } else {
      ElMessage.error(response.data.message || '批量重试失败')
    }
  } catch (error) {
    console.error('批量重试失败:', error)
    ElMessage.error('批量重试失败')
  } finally {
    batchRetryLoading.value = false
  }
}

const batchDownloadVideos = async () => {
  if (selectedCompletedTasks.value.length === 0) {
    ElMessage.warning('请先选择已完成的任务')
    return
  }
  
  try {
    batchDownloadLoading.value = true
    
    const taskIds = selectedCompletedTasks.value.map(task => task.id)
    const response = await qingyingImg2videoAPI.batchDownloadVideos(taskIds)
    
    if (response.data.success) {
      ElMessage.success(response.data.message)
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

const batchDeleteTasks = async () => {
  if (selectedTasks.value.length === 0) {
    ElMessage.warning('请选择要删除的任务')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTasks.value.length} 个任务吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const taskIds = selectedTasks.value.map(task => task.id)
    const response = await qingyingImg2videoAPI.batchDeleteTasks(taskIds)

    if (response.data.success) {
      ElMessage.success(response.data.message || '批量删除成功')
      await refreshTasks()
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

const confirmImportFolder = async () => {
  try {
    importFolderLoading.value = true
    
    // 调用后端API导入文件夹（后端会处理文件选择）
    const response = await qingyingImg2videoAPI.importFolder({
      generation_mode: importFolderForm.generation_mode,
      frame_rate: importFolderForm.frame_rate,
      resolution: importFolderForm.resolution,
      duration: importFolderForm.duration,
      ai_audio: importFolderForm.ai_audio,
      use_prompt: importFolderForm.usePrompt,
      prompt: importFolderForm.prompt
    })
    
    if (response.data.success) {
      ElMessage.success("文件选择器已调用打开，请小化浏览器返回桌面选择文件夹")
      if (importFolderForm.usePrompt && importFolderForm.prompt) {
        ElMessage.info(`已设置提示词: ${importFolderForm.prompt}`)
      }
      showImportFolderDialog.value = false
      // 延迟刷新任务列表
      setTimeout(() => {
        refreshTasks()
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

// 显示批量添加对话框
const showBatchAddDialog = () => {
  batchAddDialogVisible.value = true
}

// 重置批量添加对话框
const resetBatchAddDialog = () => {
  imageTaskList.value = []
  isDragOver.value = false
  batchAddForm.generation_mode = 'fast'
  batchAddForm.frame_rate = '30'
  batchAddForm.resolution = '720p'
  batchAddForm.duration = '5s'
  batchAddForm.ai_audio = false
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
    formData.append('generation_mode', batchAddForm.generation_mode)
    formData.append('frame_rate', batchAddForm.frame_rate)
    formData.append('resolution', batchAddForm.resolution)
    formData.append('duration', batchAddForm.duration)
    formData.append('ai_audio', batchAddForm.ai_audio)
    
    // 添加所有图片文件和对应的提示词
    imageTaskList.value.forEach((task, index) => {
      formData.append('images', task.file)
      formData.append(`prompts[${index}]`, task.prompt || '')
    })
    
    const response = await qingyingImg2videoAPI.batchAddTasks(formData)
    
    if (response.data.success) {
      ElMessage.success(`成功创建 ${imageTaskList.value.length} 个任务`)
      batchAddDialogVisible.value = false
      resetBatchAddDialog()
      
      // 刷新任务列表
      setTimeout(() => {
        refreshTasks()
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



const openVideo = (videoUrl) => {
  if (videoUrl) {
    window.open(videoUrl, '_blank')
  }
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadTasks()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadTasks()
}

const handleStatusFilter = (value) => {
  pagination.page = 1 // 重置页码到第一页
  loadTasks()
}

// 生命周期
onMounted(() => {
  refreshTasks()
})

onActivated(() => {
  refreshTasks()
})
</script>

<style scoped>
.qingying-img2video-page {
  padding: 16px 24px;
  min-height: calc(100vh - 64px);
  height: 100%;
  overflow-y: auto;
  position: relative;
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
}

.batch-retry-btn {
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: white;
}

.batch-retry-btn:hover {
  background-color: #ebb563;
}

/* 表格容器样式 */
.task-table-container {
  padding: 24px 32px;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.modern-table :deep(.el-table__header-wrapper th) {
  background-color: #f8fafc;
  color: #374151;
  font-weight: 600;
}

.modern-table :deep(.el-table__header-wrapper th:first-child) {
  border-top-left-radius: 12px;
}

.modern-table :deep(.el-table__header-wrapper th:last-child) {
  border-top-right-radius: 12px;
}

.modern-table :deep(.el-table__body-wrapper tr:last-child td:first-child) {
  border-bottom-left-radius: 12px;
}

.modern-table :deep(.el-table__body-wrapper tr:last-child td:last-child) {
  border-bottom-right-radius: 12px;
}

.image-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.image-filename {
  flex: 1;
  font-size: 14px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

  .preview-btn {
    flex-shrink: 0;
  }

  .prompt-content {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
    word-break: break-all;
    max-height: 40px; /* 限制提示词高度 */
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .param-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

.status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-tag .el-icon {
  font-size: 16px;
  vertical-align: middle;
}

.processing-tag .rotating-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  min-width: 60px;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    padding: 24px;
  }
  
  .panel-title {
    padding: 20px 24px;
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .task-table-container {
    padding: 24px 16px;
  }
}

@media (max-width: 768px) {
  .qingying-img2video-page {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 16px;
  }
  
  .header-content {
    padding: 20px 24px;
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .status-section {
    justify-content: center;
  }
  
  .stats-overview {
    margin-bottom: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    padding: 20px;
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .toolbar-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .task-table-container {
    padding: 16px;
    overflow-x: auto;
  }
}

@media (max-width: 480px) {
  .status-section {
    flex-direction: column;
    gap: 12px;
  }
  
  .status-section .el-button {
    width: 100%;
  }
  
  .toolbar-actions .el-button {
    width: 100%;
  }
}

/* 批量添加对话框样式 */
.batch-add-dialog {
  --el-dialog-padding-primary: 0;
}

.batch-add-dialog .el-dialog__body {
  padding: 0;
  max-height: 70vh;
  overflow: hidden;
}

.batch-add-wrapper {
  position: relative;
  height: 100%;
}

.batch-add-wrapper.drag-over {
  background: rgba(102, 126, 234, 0.05);
  border: 2px dashed var(--primary-color);
}

.batch-add-scrollable {
  padding: 20px;
  height: 70vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.drag-upload-area {
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-lg);
  padding: 48px 24px;
  text-align: center;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}



.drag-upload-area:hover {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.02);
}

.drag-upload-area.drag-over {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
  transform: scale(1.02);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  color: var(--primary-color);
  opacity: 0.6;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.primary-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.secondary-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.image-task-list {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid var(--border-light);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.list-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.task-item {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  transition: var(--transition);
  width: 95%;
  min-height: 280px;
  max-width: 600px;
  margin: 0 auto;
  align-items: stretch;
  box-sizing: border-box;
}

.task-item:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(102, 126, 234, 0.3);
}



.generation-settings-compact {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  border: 1px solid var(--border-light);
}

.settings-grid-compact {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.compact-form-item {
  margin-bottom: 0;
}

.compact-form-item .el-form-item__label {
  font-size: 14px;
  font-weight: 500;
}

.task-image-container {
  flex: 1;
  min-width: 0;
  max-width: 200px;
}

.task-image {
  width: 100%;
  min-height: 200px;
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.task-image img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

.task-content {
  flex: 2;
  display: flex;
  align-items: stretch;
  padding: 0 16px;
  min-width: 0;
}

.task-prompt-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-textarea {
  flex: 1;
}

.button-group {
  display: flex;
  gap: 8px;
  align-items: center;
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

/* 分页滑动样式 */
.task-pagination-container {
  height: 350px;
  overflow: hidden;
  position: relative;
  touch-action: pan-y;
}

.task-pagination-wrapper {
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  height: 100%;
}

.task-page {
  height: 100%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.generation-settings {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid var(--border-light);
}

.generation-settings h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px 48px;
  align-items: start;
}

/* 失败原因图标样式 */
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

.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: center;
}

.settings-grid .el-form-item {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .task-item {
    flex-direction: column;
  }

  .task-image {
    width: 100%;
    height: 120px;
    align-self: center;
  }
}
</style> 