<template>
  <div class="jimeng-digital-human-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><Avatar /></el-icon>
          </div>
          <h1 class="page-title">即梦数字人</h1>
        </div>
        <div class="status-section">
          <el-button 
            type="primary" 
            size="large"
            @click="showUploadDialog = true"
            class="add-task-btn"
          >
            <el-icon><Plus /></el-icon>
            创建任务
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
            <div class="stat-value">{{ stats.total || 0 }}</div>
            <div class="stat-label">总任务</div>
          </div>
        </div>
        <div class="stat-card pending">
          <div class="stat-icon">
            <el-icon size="24"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.today || 0 }}</div>
            <div class="stat-label">今日任务</div>
          </div>
        </div>
        <div class="stat-card processing">
          <div class="stat-icon">
            <el-icon size="24"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.in_progress || 0 }}</div>
            <div class="stat-label">生成中</div>
          </div>
        </div>
        <div class="stat-card completed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCheckFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completed || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        <div class="stat-card failed">
          <div class="stat-icon">
            <el-icon size="24"><CircleCloseFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.failed || 0 }}</div>
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
            @change="loadTasks"
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
          <el-button 
            type="warning" 
            @click="batchRetryFailedTasks"
            class="batch-retry-btn"
          >
            <el-icon><RefreshRight /></el-icon>
            批量重试失败任务
          </el-button>
          <el-button 
            type="success" 
            @click="batchDownloadVideos" 
            :disabled="selectedCompletedTasks.length === 0"
            :loading="batchDownloadLoading"
            v-if="selectedCompletedTasks.length > 0"
            class="batch-download-btn"
          >
            <el-icon><Download /></el-icon>
            下载选中 ({{ selectedCompletedTasks.length }})
          </el-button>
          <el-popconfirm
            title="确定要删除选中的任务吗？"
            @confirm="batchDeleteSelected"
          >
            <template #reference>
              <el-button 
                type="danger" 
                :disabled="selectedTasks.length === 0"
                class="batch-delete-btn"
              >
                <el-icon><Delete /></el-icon>
                删除选中 ({{ selectedTasks.length }})
              </el-button>
            </template>
          </el-popconfirm>
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
          empty-text="暂无数字人任务"
        >
          <el-table-column 
            type="selection" 
            width="55"
          />
          <el-table-column prop="id" label="ID" width="80" align="center" />
          
          <el-table-column label="图片名称" min-width="200" align="left">
            <template #default="{ row }">
              <div class="file-name-cell">
                <el-icon class="file-icon"><Picture /></el-icon>
                <el-tooltip :content="getImageFileName(row.image_path)" placement="top">
                  <span class="file-name">{{ truncateFileName(getImageFileName(row.image_path), 25) }}</span>
                </el-tooltip>
          </div>
            </template>
          </el-table-column>

          <el-table-column label="音频名称" min-width="200" align="left">
            <template #default="{ row }">
              <div class="file-name-cell">
                <el-icon class="file-icon"><Headphone /></el-icon>
                <el-tooltip :content="getAudioFileName(row.audio_path)" placement="top">
                  <span class="file-name">{{ truncateFileName(getAudioFileName(row.audio_path), 25) }}</span>
                </el-tooltip>
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

          <el-table-column label="操作" width="300" fixed="right" align="center">
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
                  v-if="row.status === 2 && row.video_url" 
                  size="small" 
                  type="primary"
                  @click="previewVideo(row.video_url)"
                >
                  <el-icon><VideoPlay /></el-icon>
                  预览
                </el-button>
                <el-button 
                  v-if="row.status === 2 && row.video_url" 
                  size="small" 
                  type="success"
                  @click="downloadVideo(row.video_url)"
                >
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button 
                  v-if="row.status === 3" 
                  size="small" 
                  type="warning" 
                  @click="retryTask(row.id)"
                >
                  <el-icon><RefreshRight /></el-icon>
                  重试
                </el-button>
                <el-popconfirm
                  title="确定删除这个任务吗？"
                  @confirm="deleteTask(row.id)"
                >
                  <template #reference>
                    <el-button 
                      size="small" 
                      type="danger"
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
          </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100, 500, 1000]"
          :total="totalTasks"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
            </div>
            </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="创建数字人任务"
      width="900px"
      :before-close="resetUploadForm"
      class="create-task-dialog"
    >
      <div class="dialog-content">
        <!-- 左侧预览区域 -->
        <div class="preview-panel">
          <div class="panel-header">
            <h4><el-icon><View /></el-icon> 文件预览</h4>
          </div>

          <!-- 图片预览 -->
          <div class="preview-section">
            <div class="preview-item">
              <div class="preview-header">
                <el-icon><Picture /></el-icon>
                <span>头像图片</span>
                <el-tag v-if="imageFileList.length > 0" type="success" size="small">
                  <el-icon><CircleCheck /></el-icon>
                  已上传
                </el-tag>
            </div>
              
              <div class="preview-content">
                <div v-if="imageFileList.length > 0" class="image-preview-container">
                  <img :src="getPreviewImageUrl(imageFileList[0])" alt="预览图片" />
                  <div class="file-info">
                    <div class="file-name">{{ imageFileList[0].name }}</div>
                    <div class="file-size">{{ formatFileSize(imageFileList[0].size) }}</div>
                  </div>
                </div>
                <div v-else class="empty-preview">
                  <el-icon><Picture /></el-icon>
                  <span>未选择图片</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 音频预览 -->
          <div class="preview-section">
            <div class="preview-item">
              <div class="preview-header">
                <el-icon><Headphone /></el-icon>
                <span>语音文件</span>
                <el-tag v-if="audioFileList.length > 0" type="success" size="small">
                  <el-icon><CircleCheck /></el-icon>
                  已上传
                </el-tag>
            </div>
              
              <div class="preview-content">
                <div v-if="audioFileList.length > 0" class="audio-preview-container">
                  <div class="audio-icon">
                    <el-icon><Headphone /></el-icon>
                  </div>
                  <div class="audio-info">
                    <div class="file-name">{{ audioFileList[0].name }}</div>
                    <div class="file-details">
                      <span class="file-size">{{ formatFileSize(audioFileList[0].size) }}</span>
                      <span v-if="audioInfo.duration" class="duration">{{ audioInfo.duration }}秒</span>
                    </div>
                    <div v-if="audioInfo.duration > 15" class="warning-text">
                      <el-icon><Warning /></el-icon>
                      音频时长超过15秒限制
                    </div>
                  </div>
                </div>
                <div v-else class="empty-preview">
                  <el-icon><Headphone /></el-icon>
                  <span>未选择音频</span>
                </div>
              </div>
            </div>
            </div>
          </div>

        <!-- 右侧上传区域 -->
        <div class="upload-panel">
          <div class="panel-header">
            <h4><el-icon><UploadFilled /></el-icon> 文件上传</h4>
            </div>
          
          <!-- 图片上传 -->
          <div class="upload-section">
            <div class="upload-label">
              <el-icon><Picture /></el-icon>
              头像图片
            </div>
            <el-upload
              ref="imageUploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :limit="1"
              accept="image/*"
              :on-change="handleImageChange"
              :on-remove="handleImageRemove"
              :file-list="imageFileList"
              :show-file-list="false"
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">
                将图片拖到此处，或<em>点击上传</em>
          </div>
              <template #tip>
                <div class="upload-tip">
                  支持 JPG、PNG 格式，文件大小不超过 10MB
                </div>
              </template>
            </el-upload>
        </div>

          <!-- 音频上传 -->
          <div class="upload-section">
            <div class="upload-label">
              <el-icon><Headphone /></el-icon>
              语音文件
            </div>
            <el-upload
              ref="audioUploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :limit="1"
              accept="audio/*"
              :on-change="handleAudioChange"
              :on-remove="handleAudioRemove"
              :file-list="audioFileList"
              :show-file-list="false"
            >
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div class="upload-text">
                将音频拖到此处，或<em>点击上传</em>
          </div>
              <template #tip>
                <div class="upload-tip">
                  支持 MP3、WAV、M4A 格式，时长不超过 15 秒
        </div>
              </template>
            </el-upload>
      </div>
    </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="resetUploadForm" size="large">取消</el-button>
          <el-button 
            type="primary" 
            @click="createTask"
            :loading="uploading"
            :disabled="audioInfo.duration > 15 || imageFileList.length === 0 || audioFileList.length === 0"
            size="large"
          >
            <el-icon v-if="!uploading"><Plus /></el-icon>
            {{ uploading ? '创建中...' : '创建任务' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 视频预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="视频预览"
      width="800px"
    >
      <div class="video-preview-container">
        <video 
          v-if="previewVideoUrl" 
          :src="previewVideoUrl" 
          controls 
          style="width: 100%; max-height: 400px;"
        >
          您的浏览器不支持视频播放
        </video>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onActivated } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Refresh, 
  Delete, 
  Picture,
  Headphone,
  Loading,
  CircleCheckFilled,
  CircleCloseFilled,
  Clock,
  RefreshRight,
  DataAnalysis,
  Calendar,
  UploadFilled,
  Avatar, 
  Document,
  VideoPlay,
  Download,
  View,
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'
import { digitalHumanAPI } from '../utils/api.js'

export default {
  name: 'JimengDigitalHuman',
  components: {
    Plus,
    Refresh,
    Delete,
    Picture,
    Headphone,
    Loading,
    CircleCheckFilled,
    CircleCloseFilled,
    Clock,
    RefreshRight,
    DataAnalysis,
    Calendar,
    UploadFilled,
    Avatar,
    Document,
    VideoPlay,
    Download,
    View,
    Warning,
    CircleCheck
  },
  setup() {
    // 响应式数据
    const tasks = ref([])
    const loading = ref(false)
    const uploading = ref(false)
    
    // 统计数据
    const stats = ref({
      total: 0,
      today: 0,
      in_progress: 0,
      completed: 0,
      failed: 0
    })
    
    // 对话框状态
    const showUploadDialog = ref(false)
    const showPreviewDialog = ref(false)
    const previewVideoUrl = ref('')
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalTasks = ref(0)
    const statusFilter = ref(null)
    const selectedTasks = ref([])
    
    // 上传相关
    const imageUploadRef = ref()
    const audioUploadRef = ref()
    
    // 上传文件列表
    const imageFileList = ref([])
    const audioFileList = ref([])

    // 音频信息
    const audioInfo = reactive({
      duration: 0,
      error: ''
    })


    
    // 批量下载相关
    const batchDownloadLoading = ref(false)

    // 状态相关方法
    const getStatusType = (status) => {
      const typeMap = {
        0: 'info',     // 排队中
        1: 'warning',  // 生成中
        2: 'success',  // 已完成
        3: 'danger'    // 失败
      }
      return typeMap[status] || 'info'
    }

    const getStatusIcon = (status) => {
      const iconMap = {
        0: Clock,
        1: Loading,
        2: CircleCheckFilled,
        3: CircleCloseFilled
      }
      return iconMap[status] || Clock
    }

    const getStatusText = (status) => {
      const statusMap = {
        0: '排队中',
        1: '生成中',
        2: '已完成',
        3: '失败'
      }
      return statusMap[status] || '未知状态'
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

    const formatDateTime = (timestamp) => {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }

    const getImageUrl = (path) => {
      if (!path) return ''
      // 如果路径已经是完整URL，直接返回
      if (path.startsWith('http://') || path.startsWith('https://')) {
        return path
      }
      // 构建本地静态文件URL
      const baseUrl = import.meta.env?.VITE_BACKEND_URL || 'http://localhost:8888'
      return `${baseUrl}/static/${path}`
    }

    const getPreviewImageUrl = (file) => {
      if (!file) return ''
      if (file.raw) {
        // 为本地文件创建预览URL
        return URL.createObjectURL(file.raw)
      }
      if (file.url) {
        return file.url
      }
      return ''
    }

    const handleImageError = (e) => {
      e.target.src = 'https://via.placeholder.com/150' // Fallback image
    }

    // 处理图片上传变化
    const handleImageChange = (file) => {
      if (file.status === 'ready') {
        imageFileList.value = [file]
      } else if (file.status === 'success') {
        imageFileList.value = [file]
      } else if (file.status === 'error') {
        ElMessage.error(`图片上传失败: ${file.response?.message || file.error?.message}`)
        imageFileList.value = []
      }
    }

    // 处理图片移除
    const handleImageRemove = (file) => {
      imageFileList.value = []
    }

    // 处理音频上传变化
    const handleAudioChange = (file) => {
      if (file.status === 'ready') {
        audioFileList.value = [file]
        // 检测音频时长
        getAudioDuration(file.raw)
      } else if (file.status === 'success') {
        audioFileList.value = [file]
      } else if (file.status === 'error') {
        ElMessage.error(`音频上传失败: ${file.response?.message || file.error?.message}`)
        audioFileList.value = []
        audioInfo.duration = 0
      }
    }

    // 处理音频移除
    const handleAudioRemove = (file) => {
      audioFileList.value = []
      audioInfo.duration = 0
      audioInfo.error = ''
    }

    // 获取音频时长
    const getAudioDuration = (file) => {
      const audio = new Audio()
      const url = URL.createObjectURL(file)
      
      audio.addEventListener('loadedmetadata', () => {
        const duration = Math.round(audio.duration * 10) / 10 // 保留一位小数
        audioInfo.duration = duration
        
        if (duration > 15) {
          audioInfo.error = '音频时长超过15秒限制'
          ElMessage.warning('音频时长超过15秒，请选择更短的音频文件')
        } else {
          audioInfo.error = ''
        }
        
        URL.revokeObjectURL(url)
      })
      
      audio.addEventListener('error', () => {
        audioInfo.duration = 0
        audioInfo.error = '无法读取音频文件'
        ElMessage.error('无法读取音频文件信息')
        URL.revokeObjectURL(url)
      })
      
      audio.src = url
    }

    // 加载任务列表
    const loadTasks = async () => {
      try {
        loading.value = true
        const params = {
          page: currentPage.value,
          per_page: pageSize.value
        }
        
        if (statusFilter.value !== null) {
          params.status = statusFilter.value
        }
        
        const response = await digitalHumanAPI.getTasks(params)
        
        if (response.data.success) {
          // 适配新的数据结构
          tasks.value = response.data.data.tasks || []
          totalTasks.value = response.data.data.total || 0
        } else {
          ElMessage.error(response.data.message || '获取任务列表失败')
          tasks.value = []
          totalTasks.value = 0
        }
      } catch (error) {
        console.error('获取任务列表失败:', error)
        ElMessage.error('获取任务列表失败')
        tasks.value = []
        totalTasks.value = 0
      } finally {
        loading.value = false
      }
    }

    // 加载统计数据
    const loadStats = async () => {
      try {
        const response = await digitalHumanAPI.getStats()
        if (response.data.success) {
          // 适配新的数据结构
          const data = response.data.data
          stats.value = {
            total: data.total || 0,
            today: data.today || 0,
            in_progress: data.in_progress || 0,
            completed: data.completed || 0,
            failed: data.failed || 0
          }
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
        stats.value = {
          total: 0,
          today: 0,
          in_progress: 0,
          completed: 0,
          failed: 0
        }
      }
    }

    // 刷新任务
    const refreshTasks = async () => {
      await Promise.all([loadTasks(), loadStats()])
    }

    // 创建任务
    const createTask = async () => {
      if (imageFileList.value.length === 0) {
        ElMessage.warning('请选择头像图片')
        return
      }

      if (audioFileList.value.length === 0) {
        ElMessage.warning('请选择语音文件')
        return
      }

      if (audioInfo.duration > 15) {
        ElMessage.warning('音频时长超过15秒，请重新选择')
        return
      }

      uploading.value = true
      try {
        const formData = new FormData()
        formData.append('image', imageFileList.value[0].raw)
        formData.append('audio', audioFileList.value[0].raw)

        const response = await digitalHumanAPI.createTask(formData)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          showUploadDialog.value = false
          resetUploadForm()
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('创建任务失败:', error)
        ElMessage.error('创建任务失败')
      } finally {
        uploading.value = false
      }
    }

    // 重置上传表单
    const resetUploadForm = () => {
      showUploadDialog.value = false
      imageUploadRef.value?.clearFiles()
      audioUploadRef.value?.clearFiles()
      imageFileList.value = []
      audioFileList.value = []
      audioInfo.duration = 0
      audioInfo.error = ''
    }

    // 删除任务
    const deleteTask = async (taskId) => {
      try {
        await ElMessageBox.confirm('确定删除这个任务吗？', '确认删除', {
          type: 'warning'
        })
        
        const response = await digitalHumanAPI.deleteTask(taskId)
        if (response.data.success) {
          ElMessage.success('任务删除成功')
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除任务失败:', error)
          ElMessage.error('删除任务失败')
        }
      }
    }

    // 重试任务
    const retryTask = async (taskId) => {
      try {
        const response = await digitalHumanAPI.retryTask(taskId)
        if (response.data.success) {
          ElMessage.success('任务已重新排队')
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('重试任务失败:', error)
        ElMessage.error('重试任务失败')
      }
    }

    // 批量重试失败任务
    const batchRetryFailedTasks = async () => {
      try {
        await ElMessageBox.confirm('确定重试所有失败的任务吗？', '确认重试', {
          type: 'warning'
        })
        
        const response = await digitalHumanAPI.batchRetryTasks()
        if (response.data.success) {
          ElMessage.success(response.data.message)
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量重试失败:', error)
          ElMessage.error('批量重试失败')
        }
      }
    }

    // 计算已完成的任务
    const selectedCompletedTasks = computed(() => {
      return selectedTasks.value.filter(task => task.status === 2 && task.video_url)
    })

    // 批量下载视频
    const batchDownloadVideos = async () => {
      if (selectedCompletedTasks.value.length === 0) {
        ElMessage.warning('请先选择已完成的任务')
        return
      }
      
      try {
        batchDownloadLoading.value = true
        
        // 调用后端API批量下载
        const taskIds = selectedCompletedTasks.value.map(task => task.id)
        const response = await digitalHumanAPI.batchDownload(taskIds)
        
        if (response.data.success) {
          ElMessage.success(response.data.message || '开始批量下载，请选择保存文件夹')
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

    // 批量删除选中任务
    const batchDeleteSelected = async () => {
      if (selectedTasks.value.length === 0) {
        ElMessage.warning('请选择要删除的任务')
        return
      }

      try {
        await ElMessageBox.confirm(`确定删除选中的 ${selectedTasks.value.length} 个任务吗？`, '确认删除', {
          type: 'warning'
        })
        
        const taskIds = selectedTasks.value.map(task => task.id)
        const response = await digitalHumanAPI.batchDeleteTasks(taskIds)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          selectedTasks.value = []
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
          ElMessage.error('批量删除失败')
        }
      }
    }



    // 预览视频
    const previewVideo = (videoUrl) => {
      previewVideoUrl.value = videoUrl
      showPreviewDialog.value = true
    }

    // 下载视频
    const downloadVideo = (videoUrl) => {
      const link = document.createElement('a')
      link.href = videoUrl
      link.download = `digital_human_video_${Date.now()}.mp4`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }

    // 表格选择变化
    const handleSelectionChange = (selection) => {
      selectedTasks.value = selection
    }

    // 分页大小变化
    const handleSizeChange = (newSize) => {
      pageSize.value = newSize
      currentPage.value = 1
      loadTasks()
    }

    // 当前页变化
    const handleCurrentChange = (newPage) => {
      currentPage.value = newPage
      loadTasks()
    }

    // 格式化文件大小
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 截断文件名
    const truncateFileName = (name, maxLength) => {
      if (name.length <= maxLength) {
        return name;
      }
      const truncated = name.substring(0, maxLength);
      return `${truncated}...`;
    }

    // 获取图片文件名
    const getImageFileName = (path) => {
      if (!path) return '未选择图片';
      const lastSlashIndex = path.lastIndexOf('/');
      return path.substring(lastSlashIndex + 1);
    }

    // 获取音频文件名
    const getAudioFileName = (path) => {
      if (!path) return '未选择音频';
      const lastSlashIndex = path.lastIndexOf('/');
      return path.substring(lastSlashIndex + 1);
    }

    // 生命周期
    onMounted(() => {
      refreshTasks()
    })

    onActivated(() => {
      refreshTasks()
    })

    return {
      tasks,
      loading,
      uploading,
      stats,
      showUploadDialog,
      showPreviewDialog,
      previewVideoUrl,
      currentPage,
      pageSize,
      totalTasks,
      statusFilter,
      selectedTasks,
      imageUploadRef,
      audioUploadRef,
      imageFileList,
      audioFileList,
      audioInfo,
      batchDownloadLoading,
      selectedCompletedTasks,
      getStatusType,
      getStatusIcon,
      getStatusText,
      getFailureReasonText,
      getFailureTooltipContent,
      truncateText,
      formatDateTime,
      getImageUrl,
      getPreviewImageUrl,
      handleImageError,
      handleImageChange,
      handleImageRemove,
      handleAudioChange,
      handleAudioRemove,
      getAudioDuration,
      loadTasks,
      loadStats,
      refreshTasks,
      createTask,
      resetUploadForm,
      deleteTask,
      retryTask,
      batchRetryFailedTasks,
      batchDownloadVideos,
      batchDeleteSelected,
      previewVideo,
      downloadVideo,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      formatFileSize,
      truncateFileName,
      getImageFileName,
      getAudioFileName
    }
  }
}
</script>

<style scoped>
.jimeng-digital-human-page {
  padding: 16px 24px;
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

.add-task-btn {
  background: var(--primary-gradient);
  border: none;
  color: white;
  border-radius: var(--radius-md);
  font-weight: 600;
  padding: 12px 24px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.add-task-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 统计概览样式 */
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
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.stat-card.processing .stat-icon {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
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

/* 任务管理样式 */
.task-management {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.task-management::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--accent-gradient);
  opacity: 0.02;
  z-index: -1;
}

.panel-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.panel-title h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 600;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.status-filter .el-select {
  width: 150px;
}

.refresh-btn {
  background-color: #E6A23C;
  border-color: #E6A23C;
}

.refresh-btn:hover {
  background-color: #ebb563;
  border-color: #ebb563;
}

.batch-retry-btn {
  background-color: #E6A23C;
  border-color: #E6A23C;
}

.batch-retry-btn:hover {
  background-color: #ebb563;
  border-color: #ebb563;
}



.batch-delete-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;
}

.batch-delete-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
}

.task-table-container {
  overflow-x: auto;
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

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-icon {
  color: #409eff;
  font-size: 16px;
}

.file-name {
  cursor: pointer;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-tag {
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  padding: 4px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-tag.processing-tag {
  background-color: #e1f3d8;
  color: #67c23a;
  border-color: #e1f3d8;
}

.rotating-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-buttons .el-button {
  margin: 0;
  padding: 6px 12px;
  font-size: 12px;
  border-radius: var(--radius-sm);
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
.create-task-dialog {
  border-radius: 12px;
}

.create-task-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.create-task-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.create-task-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.dialog-content {
  display: flex;
  gap: 20px;
  width: 100%;
  padding: 24px;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
  margin-bottom: 12px;
}

.preview-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-item {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
  width: 100%;
  justify-content: space-between;
}

.preview-header .el-tag {
  margin-left: auto;
}

.preview-content {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview-container {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
}

.image-preview-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-preview-container .file-info {
  position: absolute;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 0 0 8px 8px;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: #909399;
  font-size: 14px;
}

.empty-preview .el-icon {
  font-size: 36px;
}

.audio-preview-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.audio-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.audio-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.audio-info .file-name {
  font-weight: 600;
  color: #303133;
}

.audio-info .file-details {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 8px;
}

.audio-info .duration {
  color: #409eff;
  font-weight: 500;
}

.audio-info .warning-text {
  color: #f56c6c;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.upload-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area .el-upload {
  width: 100%;
}

.upload-area .el-upload-dragger {
  width: 100%;
  height: 120px;
}

.upload-area .el-upload-dragger .el-icon {
  font-size: 40px;
  color: #c0c4cc;
}

.upload-area .el-upload-dragger .el-upload__text {
  font-size: 14px;
  color: #606266;
}

.upload-area .el-upload-dragger .el-upload__tip {
  font-size: 12px;
  color: #909399;
}

.upload-area .el-upload-list {
  display: none;
}

.upload-icon {
  font-size: 40px;
  color: #c0c4cc;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.dialog-footer .el-button {
  background-color: #f8f9fa;
  border-color: #e4e7ed;
  color: #606266;
}

.dialog-footer .el-button:hover {
  background-color: #f8f9fa;
  border-color: #e4e7ed;
  color: #409EFF;
}

.dialog-footer .el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
}

.dialog-footer .el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.video-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-digital-human-page {
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
  
  .task-management {
    padding: 24px;
  }
  
  .toolbar-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .status-filter .el-select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
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
  flex-wrap: wrap;
}
</style>