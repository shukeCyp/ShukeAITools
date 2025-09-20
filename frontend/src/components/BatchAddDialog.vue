<template>
  <el-dialog
    v-model="dialogVisible"
    title=""
    width="100%"
    fullscreen
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
    class="batch-add-dialog"
  >
    <!-- 右上角关闭按钮 -->
    <div class="close-button" @click="handleClose">
      <el-icon><Close /></el-icon>
    </div>

    <div class="dialog-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <div class="panel-header">
          <div class="panel-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <h3 class="panel-title">生成配置</h3>
        </div>

        <!-- 即梦配置 -->
        <div v-if="serviceType === 'jimeng'" class="config-section">
          <div class="config-group">
            <label class="config-label">模型选择</label>
            <div class="radio-group-custom">
              <div 
                v-for="model in jimengModels" 
                :key="model.value"
                class="radio-option"
                :class="{ active: formData.model === model.value }"
                @click="formData.model = model.value"
              >
                <div class="radio-content">
                  <span class="radio-title">{{ model.label }}</span>
                  <span class="radio-desc">{{ model.desc }}</span>
                </div>
                <div class="radio-indicator">
                  <div class="indicator-dot"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="config-group">
            <label class="config-label">视频时长</label>
            <div class="chip-group">
              <div 
                v-for="duration in getJimengDurations" 
                :key="duration.value"
                class="chip-option"
                :class="{ active: formData.duration === duration.value }"
                @click="formData.duration = duration.value"
              >
                {{ duration.label }}
              </div>
            </div>
          </div>


        </div>

        <!-- 清影配置 -->
        <div v-if="serviceType === 'qingying'" class="config-section">
          <div class="config-group">
            <label class="config-label">生成模式</label>
            <div class="radio-group-custom">
              <div 
                v-for="mode in qingyingModes" 
                :key="mode.value"
                class="radio-option"
                :class="{ active: formData.mode === mode.value }"
                @click="formData.mode = mode.value"
              >
                <div class="radio-content">
                  <span class="radio-title">{{ mode.label }}</span>
                  <span class="radio-desc">{{ mode.desc }}</span>
                </div>
                <div class="radio-indicator">
                  <div class="indicator-dot"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="config-group">
            <label class="config-label">帧率</label>
            <div class="chip-group">
              <div 
                v-for="fps in qingyingFps" 
                :key="fps.value"
                class="chip-option"
                :class="{ active: formData.fps === fps.value }"
                @click="formData.fps = fps.value"
              >
                {{ fps.label }}
              </div>
            </div>
          </div>

          <div class="config-group">
            <label class="config-label">分辨率</label>
            <div class="chip-group">
              <div 
                v-for="resolution in qingyingResolutions" 
                :key="resolution.value"
                class="chip-option"
                :class="{ active: formData.resolution === resolution.value }"
                @click="formData.resolution = resolution.value"
              >
                {{ resolution.label }}
              </div>
            </div>
          </div>

          <div class="config-group">
            <label class="config-label">视频时长</label>
            <div class="chip-group">
              <div 
                v-for="duration in qingyingDurations" 
                :key="duration.value"
                class="chip-option"
                :class="{ active: formData.qingyingDuration === duration.value }"
                @click="formData.qingyingDuration = duration.value"
              >
                {{ duration.label }}
              </div>
            </div>
          </div>

          <div class="config-group">
            <label class="config-label">AI音效</label>
            <div class="switch-group">
              <el-switch
                v-model="formData.aiSound"
                active-text="开启"
                inactive-text="关闭"
                active-color="var(--macaron-success)"
                inactive-color="var(--macaron-muted)"
              />
            </div>
          </div>


        </div>
      </div>

      <!-- 右侧上传区域 -->
      <div 
        class="upload-panel"
        @drop.prevent="handleDrop"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
      >
        <!-- 拖拽上传区域 -->
        <div 
          v-show="tasks.length === 0"
          class="upload-area"
          :class="{ 'drag-over': isDragOver }"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/*"
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div class="upload-content">
            <div class="upload-icon">
              <el-icon size="48"><Plus /></el-icon>
            </div>
            <div class="upload-text">
              <h3>拖拽图片到此处</h3>
              <p>或点击选择图片文件</p>
              <span class="upload-hint">支持 JPG、PNG 格式，建议尺寸 1:1</span>
            </div>
          </div>
        </div>

        <!-- 任务列表 -->
        <div v-if="tasks.length > 0" class="task-section">
          <div class="task-header">
            <h4>已添加 {{ tasks.length }} 个任务</h4>
            <div class="task-actions">
              <el-button
                type="warning"
                size="small"
                @click="triggerFileInput"
              >
                <template #icon>
                  <el-icon><Plus /></el-icon>
                </template>
                继续添加
              </el-button>
              <el-button
                class="btn-clear"
                size="small"
                @click="clearAllTasks"
              >
                <template #icon>
                  <el-icon><Delete /></el-icon>
                </template>
                清空全部
              </el-button>
            </div>
          </div>

          <!-- 任务滑动展示 -->
          <div class="task-carousel">
            <div class="carousel-container" ref="carouselContainer">
              <div 
                class="carousel-track"
                :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
                @wheel="handleWheel"
                @touchstart="handleTouchStart"
                @touchmove="handleTouchMove"
                @touchend="handleTouchEnd"
              >
                <div
                  v-for="(task, index) in tasks"
                  :key="task.id"
                  class="task-slide"
                  @click="setCurrentIndex(index)"
                >
                  <div class="task-card" :class="{ active: currentIndex === index }">
                    <div class="task-image">
                      <img :src="task.preview" :alt="`任务 ${index + 1}`" />
                    </div>
                    <div class="task-info">
                      <div class="task-name">{{ task.file.name }}</div>
                      <div class="task-size">{{ formatFileSize(task.file.size) }}</div>
                    </div>
                    
                    <!-- 每个图片的提示词输入框 -->
                    <div class="task-prompt">
                      <el-input
                        v-model="task.prompt"
                        type="textarea"
                        :rows="4"
                        :maxlength="500"
                        :placeholder="serviceType === 'jimeng' ? '为这张图片描述生成视频的提示词...' : '为这张图片描述生成视频的提示词...'"
                        show-word-limit
                        resize="none"
                        @click.stop
                      />
                    </div>
                    
                    <el-button
                      class="btn-remove"
                      size="small"
                      circle
                      tooltip="删除"
                      @click.stop="removeTask(index)"
                    >
                      <template #icon>
                        <el-icon><Close /></el-icon>
                      </template>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 指示器 -->
            <div v-if="tasks.length > 1" class="carousel-indicators">
              <div
                v-for="(task, index) in tasks"
                :key="task.id"
                class="indicator"
                :class="{ active: currentIndex === index }"
                @click="setCurrentIndex(index)"
              ></div>
            </div>
          </div>
        </div>

        <!-- 拖拽提示区域（当有任务时显示） -->
        <div v-if="tasks.length > 0" class="drop-hint-area" :class="{ 'drag-over': isDragOver }">
          <div class="drop-hint-content">
            <div class="drop-hint-icon">
              <el-icon size="32"><Plus /></el-icon>
            </div>
            <div class="drop-hint-text">
              <span>拖拽图片到此处继续添加</span>
              <small>或点击"继续添加"按钮</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作区 -->
    <template #footer>
      <div class="dialog-footer">
        <div class="footer-info">
          <span v-if="tasks.length > 0" class="task-count">
            共 {{ tasks.length }} 个任务
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            class="btn-start-generate"
            :disabled="tasks.length === 0"
            :loading="isSubmitting"
            @click="handleSubmit"
          >
            <template #icon>
              <el-icon><MagicStick /></el-icon>
            </template>
            开始生成 ({{ tasks.length }})
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'

import {
  Close,
  FullScreen,
  Aim,
  UploadFilled,
  Plus,
  Delete,
  MagicStick,
  VideoPlay,
  Setting,
  Fold
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  serviceType: {
    type: String,
    default: 'jimeng'
  }
})

// Emits
const emit = defineEmits(['update:visible', 'submit'])

// 状态
const isDragOver = ref(false)
const isSubmitting = ref(false)
const currentIndex = ref(0) // Changed from currentPage to currentIndex
const tasks = ref([]) // Changed from imageTaskList to tasks

// 配置选项
const jimengModels = ref([
  { value: 'Video 3.0', label: 'Video 3.0', desc: '最新模型，质量更佳' },
  { value: 'Video S2.0 Pro', label: 'Video S2.0 Pro', desc: '专业版本，稳定可靠' }
])

// 即梦时长选项 - 根据模型动态生成
const getJimengDurations = computed(() => {
  if (formData.model === 'Video S2.0 Pro') {
    return [{ value: 5, label: '5秒' }] // Video S2.0 Pro只支持5秒
  } else {
    return [
      { value: 5, label: '5秒' },
      { value: 10, label: '10秒' }
    ] // Video 3.0支持5秒和10秒
  }
})

const qingyingModes = ref([
  { value: 'fast', label: '速度更快', desc: '快速生成，适合批量处理' },
  { value: 'quality', label: '质量更佳', desc: '高质量输出，细节更丰富' }
])

const qingyingFps = ref([
  { value: '30', label: '30 FPS' },
  { value: '60', label: '60 FPS' }
])

const qingyingResolutions = ref([
  { value: '720p', label: '720P' },
  { value: '1080p', label: '1080P' },
  { value: '4k', label: '4K' }
])

const qingyingDurations = ref([
  { value: '5s', label: '5秒' },
  { value: '10s', label: '10秒' }
])

// 表单数据
const formData = reactive({
  // 即梦配置
  model: 'Video 3.0',
  duration: 5, // 默认5秒
  prompt: '', // 即梦提示词
  // 清影配置
  mode: 'fast',
  fps: '30',
  resolution: '1080p',
  qingyingDuration: '5s', // 重命名清影的时长属性避免冲突
  qingyingPrompt: '', // 清影提示词
  aiSound: false
})

// 监听即梦模型变化，自动调整时长选项
watch(() => formData.model, (newModel) => {
  if (newModel === 'Video S2.0 Pro' && formData.duration === 10) {
    // 如果切换到S2.0 Pro且当前选择了10秒，自动切换到5秒
    formData.duration = 5
    ElMessage.info('Video S2.0 Pro 仅支持5秒时长，已自动调整')
  }
})

// 触摸相关
const touchStartX = ref(0) // Changed from touchStartY to touchStartX
const swipeThreshold = 30

// Refs
const fileInput = ref(null)
const carouselContainer = ref(null) // Changed from swipeContainer to carouselContainer

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})



// 文件处理
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addImageFiles(files)
  event.target.value = ''
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  addImageFiles(imageFiles)
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const addImageFiles = (files) => {
  if (files.length === 0) {
    ElMessage.warning('请选择图片文件')
    return
  }

  if (tasks.value.length + files.length > 100) {
    ElMessage.warning('最多支持100张图片')
    return
  }

  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      tasks.value.push({
        id: Date.now() + Math.random(),
        file,
        preview: e.target.result,
        prompt: ''
      })
    }
    reader.readAsDataURL(file)
  })

  ElMessage.success(`成功添加 ${files.length} 张图片`)
}

// 任务管理
const removeTask = (index) => {
  tasks.value.splice(index, 1)
  if (currentIndex.value >= tasks.value.length && tasks.value.length > 0) {
    currentIndex.value = tasks.value.length - 1
  }
}

const clearAllTasks = () => {
  tasks.value = []
  currentIndex.value = 0
}

const generateAIPrompt = async (index) => {
  ElMessage.info('AI提示词生成功能开发中...')
}

// 分页导航
const setCurrentIndex = (index) => { // Changed from goToPage to setCurrentIndex
  if (index >= 0 && index < tasks.value.length) {
    currentIndex.value = index
  }
}

const nextPage = () => {
  if (currentIndex.value < tasks.value.length - 1) {
    currentIndex.value++
  }
}

const prevPage = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

// 触摸事件
const handleTouchStart = (event) => {
  touchStartX.value = event.touches[0].clientX
}

const handleTouchMove = (event) => {
  event.preventDefault()
}

const handleTouchEnd = (event) => {
  if (tasks.value.length <= 1) return
  
  const touchEndX = event.changedTouches[0].clientX
  const deltaX = touchStartX.value - touchEndX

  if (Math.abs(deltaX) > swipeThreshold) {
    if (deltaX > 0) {
      nextPage()
    } else {
      prevPage()
    }
  }
}

// 滚轮事件
const handleWheel = (event) => {
  if (tasks.value.length <= 1) return
  
  event.preventDefault()
  if (event.deltaY > 0) { // 向下滚动切换到下一个
    nextPage()
  } else if (event.deltaY < 0) { // 向上滚动切换到上一个
    prevPage()
  }
}

// 键盘事件
const handleKeydown = (event) => {
  if (tasks.value.length <= 1) return
  
  switch (event.key) {
    case 'ArrowUp':
      event.preventDefault()
      prevPage()
      break
    case 'ArrowDown':
      event.preventDefault()
      nextPage()
      break
    case 'Home':
      event.preventDefault()
      currentIndex.value = 0
      break
    case 'End':
      event.preventDefault()
      currentIndex.value = tasks.value.length - 1
      break
  }
}

// 工具函数
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 对话框操作
const handleClose = () => {
  emit('update:visible', false)
  // 重置状态
  tasks.value = []
  currentIndex.value = 0
  isDragOver.value = false
}

const handleSubmit = async () => {
  if (tasks.value.length === 0) {
    ElMessage.warning('请先添加图片')
    return
  }

  isSubmitting.value = true
  
  try {
    const submitData = {
      tasks: tasks.value,
      config: { ...formData },
      serviceType: props.serviceType
    }
    
    emit('submit', submitData)
    
  } finally {
    isSubmitting.value = false
  }
}

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      carouselContainer.value?.focus()
    })
  }
})
</script>

<style scoped>
@import '../styles/macaron-colors.css';

.batch-add-dialog {
  --primary-color: #6366f1;
  --primary-light: #8b5cf6;
  --success-color: #10b981; 
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #3b82f6;
  --text-primary: #1f2937;
  --text-regular: #374151;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --border-light: #f3f4f6;
  --fill-base: #f9fafb;
  --background-base: #ffffff;
  --shadow-light: 0 4px 16px rgba(0, 0, 0, 0.06);
  --shadow-medium: 0 8px 32px rgba(0, 0, 0, 0.1);
  --shadow-heavy: 0 16px 48px rgba(0, 0, 0, 0.15);
}

/* 添加一些全局动画效果 */
.batch-add-dialog * {
  box-sizing: border-box;
}

/* 滚动条美化 */
.config-panel::-webkit-scrollbar {
  width: 6px;
}

.config-panel::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.config-panel::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  border-radius: 3px;
}

.config-panel::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
}

/* 加载动画效果 */
@keyframes shimmer {
  0% {
    background-position: -468px 0;
  }
  100% {
    background-position: 468px 0;
  }
}

.radio-option:hover .radio-content,
.chip-option:hover {
  position: relative;
  overflow: hidden;
}

.radio-option:hover .radio-content::before,
.chip-option:hover::before {
  animation: shimmer 1.5s infinite linear;
}

/* 增强焦点样式 */
.radio-option:focus-visible,
.chip-option:focus-visible,
.task-card:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 增强按钮样式 */
/* 按钮样式已移至全局样式 */

/* 增强开关样式 */
:deep(.el-switch) {
  height: 28px !important;
}

:deep(.el-switch__core) {
  border-radius: 14px !important;
  height: 28px !important;
  width: 52px !important;
}

:deep(.el-switch__action) {
  width: 24px !important;
  height: 24px !important;
  border-radius: 12px !important;
}

/* 文件输入隐藏 */
input[type="file"] {
  position: absolute;
  left: -9999px;
  opacity: 0;
  pointer-events: none;
}

:deep(.el-dialog) {
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
  height: 100vh;
  max-height: 100vh;
  margin: 0 !important;
  top: 0 !important;
  left: 0 !important;
  transform: none !important;
}

:deep(.el-overlay) {
  margin: 0 !important;
  padding: 0 !important;
}

:deep(.el-dialog__body) {
  padding: 0;
  height: calc(100vh - 140px);
  min-height: calc(100vh - 140px);
  max-height: calc(100vh - 140px);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28px 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.service-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.service-icon {
  color: white;
  padding: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.service-title {
  font-size: 26px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 15px;
  opacity: 0.9;
  margin-top: 6px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 16px;
}

.dialog-content {
  display: flex;
  height: 100%;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
}

/* 左侧配置面板 */
.config-panel {
  width: 340px;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  height: 100%;
  max-height: calc(100vh - 140px);
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
}

.panel-icon {
  color: white;
  font-size: 20px;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.config-section {
  margin-bottom: 24px;
}

.config-group {
  margin-bottom: 28px;
}

.config-group .config-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  position: relative;
  padding-left: 12px;
}

.config-group .config-label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  border-radius: 2px;
}

.radio-group-custom {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 马卡龙色系单选框 */
.radio-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border: 2px solid #fed7aa;
  border-radius: 16px;
  background: #fef7f0;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(254, 215, 170, 0.15);
}

.radio-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.1) 0%, rgba(234, 88, 12, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.radio-option:hover {
  border-color: #fb923c;
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(251, 146, 60, 0.25);
  background: #fef3f0;
}

.radio-option:hover::before {
  opacity: 1;
}

.radio-option.active {
  border-color: #7c3aed;
  background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(124, 58, 237, 0.4);
}

/* 为不同的单选框添加不同的马卡龙色 */
.radio-option:nth-child(1) {
  background: #fef7f0;
  border-color: #fed7aa;
}

.radio-option:nth-child(1):hover {
  background: #fef3f0;
  border-color: #fb923c;
  box-shadow: 0 8px 32px rgba(251, 146, 60, 0.25);
}

.radio-option:nth-child(1).active {
  background: linear-gradient(135deg, #fb923c 0%, #ea580c 100%);
  border-color: #ea580c;
  box-shadow: 0 12px 40px rgba(234, 88, 12, 0.4);
}

.radio-option:nth-child(2) {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.radio-option:nth-child(2):hover {
  background: #e0f2fe;
  border-color: #38bdf8;
  box-shadow: 0 8px 32px rgba(56, 189, 248, 0.25);
}

.radio-option:nth-child(2).active {
  background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
  border-color: #0284c7;
  box-shadow: 0 12px 40px rgba(2, 132, 199, 0.4);
}

.radio-option:nth-child(3) {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.radio-option:nth-child(3):hover {
  background: #dcfce7;
  border-color: #4ade80;
  box-shadow: 0 8px 32px rgba(74, 222, 128, 0.25);
}

.radio-option:nth-child(3).active {
  background: linear-gradient(135deg, #4ade80 0%, #16a34a 100%);
  border-color: #16a34a;
  box-shadow: 0 12px 40px rgba(22, 163, 74, 0.4);
}

.radio-option:nth-child(4) {
  background: #fdf4ff;
  border-color: #e9d5ff;
}

.radio-option:nth-child(4):hover {
  background: #f3e8ff;
  border-color: #a855f7;
  box-shadow: 0 8px 32px rgba(168, 85, 247, 0.25);
}

.radio-option:nth-child(4).active {
  background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
  border-color: #7c3aed;
  box-shadow: 0 12px 40px rgba(124, 58, 237, 0.4);
}

.radio-option.active .radio-content .radio-title {
  color: white !important;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.radio-option.active .radio-content .radio-desc {
  color: rgba(255, 255, 255, 0.95) !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.radio-option .radio-content {
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

.radio-option .radio-title {
  font-size: 16px;
  font-weight: 700;
  color: #7c2d12;
  margin-bottom: 4px;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
}

.radio-option .radio-desc {
  font-size: 13px;
  color: #a16207;
  line-height: 1.4;
  font-weight: 500;
}

.radio-option .radio-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.1);
  border: 2px solid var(--border-color);
  transition: all 0.4s ease;
  position: relative;
  z-index: 1;
}

.radio-option:hover .radio-indicator {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.2);
}

.radio-option.active .radio-indicator {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.6);
}

.radio-option .indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary-color);
  opacity: 0;
  transform: scale(0);
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.radio-option.active .indicator-dot {
  background: white;
  opacity: 1;
  transform: scale(1);
}

.chip-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.chip-option {
  padding: 10px 18px;
  border: 2px solid var(--border-color);
  border-radius: 24px;
  background: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chip-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chip-option:hover {
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
}

.chip-option:hover::before {
  opacity: 1;
}

.chip-option:hover {
  color: white;
}

.chip-option.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); /* 蓝色渐变背景 */
  color: white !important;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4); /* 蓝色阴影 */
}

.chip-option.active::before {
  opacity: 1;
}

.switch-group {
  margin-top: 16px;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.input-group {
  margin-top: 16px;
}

.prompt-input {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:deep(.prompt-input .el-textarea__inner) {
  border-radius: 12px !important;
  border: 2px solid var(--border-light) !important;
  background: white !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 12px 16px !important;
  resize: none !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

:deep(.prompt-input .el-textarea__inner:focus) {
  border-color: var(--primary-color) !important;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
}

:deep(.prompt-input .el-input__count) {
  background: transparent !important;
  font-size: 12px !important;
  color: var(--text-secondary) !important;
}

/* 右侧上传区域 */
.upload-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  height: 100%;
  overflow: hidden;
  position: relative;
}

.upload-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 70%, rgba(99, 102, 241, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
  animation: subtle-pulse 8s ease-in-out infinite;
}

@keyframes subtle-pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.7;
  }
}

.upload-panel > * {
  position: relative;
  z-index: 1;
}

/* 上传区域 */
.upload-area {
  flex: 1;
  border: 3px dashed var(--border-color);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 400px;
  background: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(79, 70, 229, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.02);
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(99, 102, 241, 0.15);
}

.upload-area:hover::before,
.upload-area.drag-over::before {
  opacity: 1;
}

.upload-content {
  text-align: center;
  padding: 48px 32px;
  position: relative;
  z-index: 1;
}

.upload-icon {
  color: var(--primary-color);
  margin-bottom: 24px;
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
}

.upload-text h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, var(--text-primary) 0%, #374151 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.upload-text p {
  font-size: 16px;
  color: var(--text-regular);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.upload-hint {
  font-size: 14px;
  color: var(--text-secondary);
  display: block;
  margin-top: 16px;
  padding: 12px 20px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

/* 任务列表 */
.task-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  animation: fade-in-up 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.task-header h4 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-header h4::before {
  content: '';
  width: 6px;
  height: 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  border-radius: 3px;
}

.task-actions {
  display: flex;
  gap: 12px;
}

/* 任务滑动展示 */
.task-carousel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  background: white;
  border: 1px solid var(--border-light);
  overflow: hidden;
  position: relative;
  outline: none;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
}

.carousel-container {
  flex: 1;
  overflow-x: hidden;
  scroll-behavior: smooth;
}

.carousel-track {
  display: flex;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.task-slide {
  flex: 0 0 100%;
  min-width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 20px;
}

.task-slide:hover {
  transform: scale(1.02);
}

.task-slide.active {
  transform: scale(1.03);
}

.task-card {
  display: flex;
  align-items: center;
  padding: 32px;
  gap: 32px;
  width: 100%;
  border-radius: 20px;
  background: linear-gradient(135deg, #fafbfc 0%, white 100%);
  border: 2px solid transparent;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.task-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(79, 70, 229, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.task-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(99, 102, 241, 0.2);
}

.task-card:hover::before {
  opacity: 1;
}

.task-card.active {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 20px 60px rgba(99, 102, 241, 0.4);
}

.task-image {
  width: 160px; /* 增加宽度 */
  height: 120px; /* 减少高度，形成16:12的比例 */
  flex-shrink: 0;
  border-radius: 16px;
  overflow: hidden;
  background: #f8fafc; /* 统一背景色 */
  border: 2px solid var(--border-light);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  display: flex; /* 添加flex布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
}

.task-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为contain确保图片完整显示 */
  background: #f8fafc; /* 添加背景色填充空白区域 */
  transition: transform 0.4s ease;
}

.task-card:hover .task-image img {
  transform: scale(1.05);
}

.task-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  position: relative;
  z-index: 1;
}

.task-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937; /* 深色文字 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 8px;
}

.task-size {
  font-size: 14px;
  color: #374151; /* 深色次要文字 */
  padding: 6px 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 20px;
  display: inline-block;
  width: fit-content;
}

/* 每个任务的提示词输入框 */
.task-prompt {
  margin-top: 16px;
  position: relative;
  z-index: 1;
}

.task-prompt :deep(.el-textarea) {
  width: 100%;
}

.task-prompt :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  transition: all 0.3s ease;
  padding: 16px 18px;
  min-height: 120px;
  min-width: 420px;
}

.task-prompt :deep(.el-textarea__inner):focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.task-prompt :deep(.el-input__count) {
  color: #9ca3af;
  font-size: 12px;
  background: transparent;
}

/* 指示器 */
.carousel-indicators {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, white 100%);
  border-top: 1px solid var(--border-light);
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border-color);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.indicator:hover {
  background: var(--text-secondary);
  transform: scale(1.3);
}

.indicator:hover::before {
  opacity: 1;
}

.indicator.active {
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  transform: scale(1.5);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

/* 底部 */
.dialog-footer {
  padding: 20px 36px;
  background: linear-gradient(135deg, white 0%, #f8fafc 100%);
  border-top: 2px solid var(--border-light);
  position: sticky;
  bottom: 0;
  z-index: 10;
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-info .task-count {
  font-size: 15px;
  color: white;
  font-weight: 600;
  background: linear-gradient(135deg, var(--primary-color) 0%, #4f46e5 100%);
  padding: 8px 20px;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-info .task-count::before {
  content: '📁';
  font-size: 16px;
}

.footer-actions {
  display: flex;
  gap: 20px;
}

/* 响应式优化 */
@media (max-width: 1200px) {
  .config-panel {
    width: 300px;
    padding: 20px;
  }
  
  .upload-panel {
    padding: 20px;
  }
  
  .task-card {
    flex-direction: column;
    gap: 20px;
    padding: 24px;
  }
  
  .task-image {
    width: 100%;
    height: 160px;
  }
}

@media (max-width: 768px) {
  .dialog-header {
    padding: 20px 24px;
  }
  
  .service-title {
    font-size: 22px;
  }
  
  .service-icon {
    padding: 10px;
  }
  
  .dialog-content {
    flex-direction: column;
  }
  
  .config-panel {
    width: 100%;
    max-height: 350px;
    border-right: none;
    border-bottom: 2px solid var(--border-light);
    padding: 20px;
  }
  
  .upload-panel {
    padding: 20px;
  }
  
  .dialog-footer {
    padding: 20px 24px;
  }
  
  .footer-actions {
    gap: 16px;
  }
}

/* 右上角关闭按钮 */
.close-button {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.close-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.close-button .el-icon {
  font-size: 18px;
  color: #666;
  transition: color 0.3s ease;
}

.close-button:hover .el-icon {
  color: #333;
}

/* 拖拽提示区域 */
.drop-hint-area {
  margin-top: 20px;
  padding: 24px;
  border: 2px dashed #cbd5e1;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.drop-hint-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(79, 70, 229, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.drop-hint-area.drag-over {
  border-color: var(--primary-color);
  background: rgba(99, 102, 241, 0.08);
  transform: scale(1.02);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
}

.drop-hint-area.drag-over::before {
  opacity: 1;
}

.drop-hint-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.drop-hint-icon {
  color: var(--primary-color);
  opacity: 0.8;
  transition: all 0.3s ease;
}

.drop-hint-area.drag-over .drop-hint-icon {
  opacity: 1;
  transform: scale(1.1);
}

.drop-hint-text {
  text-align: left;
}

.drop-hint-text span {
  display: block;
  color: var(--text-regular);
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
  transition: color 0.3s ease;
}

.drop-hint-text small {
  color: var(--text-secondary);
  font-size: 14px;
  transition: color 0.3s ease;
}

.drop-hint-area.drag-over .drop-hint-text span {
  color: var(--primary-color);
}

.drop-hint-area.drag-over .drop-hint-text small {
  color: var(--text-regular);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .drop-hint-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .drop-hint-text {
    text-align: center;
  }
  
  .drop-hint-text span {
    font-size: 15px;
  }
  
  .drop-hint-text small {
    font-size: 13px;
  }
  
  .drop-hint-area {
    padding: 20px 16px;
  }
}
</style> 