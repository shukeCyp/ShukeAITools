<template>
  <div class="jimeng-text2img-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><EditPen /></el-icon>
          </div>
          <h1 class="page-title">即梦文生图</h1>
        </div>
        <div class="status-section">
          <el-button 
            type="primary" 
            size="large"
            @click="showAddTaskDialog = true"
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
            <div class="stat-value">{{ stats.queued || 0 }}</div>
            <div class="stat-label">排队中</div>
          </div>
        </div>
        <div class="stat-card processing">
          <div class="stat-icon">
            <el-icon size="24"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.processing || 0 }}</div>
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
              @change="handleStatusFilter"
            class="status-filter"
            >
              <el-option label="全部" :value="null" />
              <el-option label="排队中" value="pending" />
              <el-option label="生成中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
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
              type="success" 
              @click="showBatchAddDialog = true"
            class="batch-add-btn"
            >
            <el-icon><DocumentAdd /></el-icon>
              批量添加
            </el-button>
            <el-button 
              type="success" 
              @click="batchDownloadImages"
              :disabled="selectedCompletedTasks.length === 0"
              :loading="batchDownloadLoading"
              class="batch-download-btn"
            >
              <el-icon v-if="!batchDownloadLoading"><Download /></el-icon>
              {{ batchDownloadLoading ? '请选择文件夹...' : `下载选中 (${selectedCompletedTasks.length})` }}
            </el-button>
            <el-popconfirm
              title="确定要删除选中的任务吗？"
              @confirm="batchDeleteTasks"
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
        >
          <el-table-column 
            type="selection" 
            width="55" 
            :selectable="isTaskSelectable"
          />
          <el-table-column prop="id" label="ID" width="80" align="center" />
          
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
              <el-tag class="model-tag">{{ row.model || '-' }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="ratio" label="分辨率" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" class="ratio-tag">{{ row.ratio || row.aspect_ratio }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="quality" label="清晰度" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getQualityType(row.quality)" class="quality-tag">{{ row.quality || '-' }}</el-tag>
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



          <el-table-column label="操作" width="180" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
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
                  v-if="row.status === 2 && (row.result_image_url || (row.images && row.images.length > 0))"
                  type="primary" 
                  size="small"
                  @click="viewResult(row)"
                  class="action-btn"
                >
                  <el-icon><View /></el-icon>
                  查看
                </el-button>

                <el-popconfirm
                  :title="`确定删除任务 #${row.id} 吗？`"
                  @confirm="deleteTask(row.id)"
                >
                  <template #reference>
                    <el-button 
                      type="danger" 
                      size="small"
                      :disabled="row.status === 1"
                      text
                      class="action-btn delete-btn"
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
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 添加任务对话框 -->
    <el-dialog
      v-model="showAddTaskDialog"
      title="创建文生图任务"
      width="600px"
      class="modern-dialog"
    >
      <el-form 
        :model="taskForm" 
        :rules="taskRules" 
        ref="taskFormRef" 
        label-width="120px"
        class="task-form"
      >
          <el-form-item label="提示词" prop="prompt">
            <el-input
            v-model="taskForm.prompt"
              type="textarea"
              :rows="4"
            placeholder="请输入图像描述提示词..."
            maxlength="1000"
              show-word-limit
            />
          </el-form-item>
          
        <el-form-item label="模型选择" prop="model">
          <el-select v-model="taskForm.model" placeholder="选择生成模型" class="full-width">
            <el-option label="Image 1.4" value="Image 1.4" />
            <el-option label="Image 2.0 Pro" value="Image 2.0 Pro" />
            <el-option label="Image 2.1" value="Image 2.1" />
            <el-option label="Image 3.0" value="Image 3.0" />
            <el-option label="Image 3.1" value="Image 3.1" />
                </el-select>
              </el-form-item>

        <el-form-item label="图像比例" prop="aspect_ratio">
          <el-select v-model="taskForm.aspect_ratio" placeholder="选择图像比例" class="full-width">
            <el-option label="21:9 超宽屏" value="21:9" />
            <el-option label="16:9 横屏" value="16:9" />
            <el-option label="3:2 经典" value="3:2" />
            <el-option label="4:3 传统" value="4:3" />
            <el-option label="1:1 正方形" value="1:1" />
            <el-option label="3:4 肖像" value="3:4" />
            <el-option label="2:3 竖版" value="2:3" />
            <el-option label="9:16 竖屏" value="9:16" />
                </el-select>
              </el-form-item>

        <el-form-item label="图像质量" prop="quality">
          <el-select v-model="taskForm.quality" placeholder="选择图像质量" class="full-width">
            <el-option label="1K" value="1K" />
            </el-select>
          </el-form-item>
        </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showAddTaskDialog = false" class="cancel-btn">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="addTask"
            :loading="addTaskLoading"
            class="confirm-btn"
          >
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量添加对话框 -->
    <el-dialog
      v-model="showBatchAddDialog"
      title="批量添加任务"
      width="700px"
      class="modern-dialog"
    >
      <div class="batch-add-content">
        <div class="tips-section">
          <el-alert
            title="批量添加说明"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>每行一个提示词，将自动创建多个任务</p>
              <p>支持最多100个任务同时创建</p>
            </template>
          </el-alert>
        </div>

        <el-form :model="batchForm" ref="batchFormRef" label-width="120px">
          <el-form-item label="提示词列表" prop="prompts">
          <el-input
              v-model="batchForm.prompts"
            type="textarea"
              :rows="10"
              placeholder="请输入提示词，每行一个..."
              maxlength="10000"
            show-word-limit
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="模型" prop="model">
                <el-select v-model="batchForm.model" class="full-width">
                  <el-option label="Image 1.4" value="Image 1.4" />
                  <el-option label="Image 2.0 Pro" value="Image 2.0 Pro" />
                  <el-option label="Image 2.1" value="Image 2.1" />
                  <el-option label="Image 3.0" value="Image 3.0" />
                  <el-option label="Image 3.1" value="Image 3.1" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="比例" prop="aspect_ratio">
                <el-select v-model="batchForm.aspect_ratio" class="full-width">
                  <el-option label="21:9" value="21:9" />
                  <el-option label="16:9" value="16:9" />
                  <el-option label="3:2" value="3:2" />
                  <el-option label="4:3" value="4:3" />
                  <el-option label="1:1" value="1:1" />
                  <el-option label="3:4" value="3:4" />
                  <el-option label="2:3" value="2:3" />
                  <el-option label="9:16" value="9:16" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="质量" prop="quality">
                <el-select v-model="batchForm.quality" class="full-width">
                  <el-option label="1K" value="1K" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchAddDialog = false" class="cancel-btn">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="batchAddTasks"
            :loading="batchAddLoading"
            class="confirm-btn"
          >
            <el-icon><DocumentAdd /></el-icon>
            批量创建
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看结果对话框 -->
    <el-dialog
      v-model="showResultDialog"
      :title="`任务 #${currentTask?.id} 生成结果`"
      width="800px"
      class="modern-dialog result-dialog"
    >
      <div class="result-content" v-if="currentTask">
        <div class="result-info">
          <h4>任务信息</h4>
          <p><strong>提示词：</strong>{{ currentTask.prompt || '-' }}</p>
          <p><strong>模型：</strong>{{ currentTask.model || '-' }}</p>
          <p><strong>比例：</strong>{{ currentTask.ratio || currentTask.aspect_ratio || '-' }}</p>
          <p><strong>质量：</strong>{{ currentTask.quality || '-' }}</p>
        </div>
        
        <div class="result-images" v-if="currentTask.result_image_url || (currentTask.images && currentTask.images.length > 0)">
          <h4>生成图像</h4>
          <div class="image-grid">
            <div 
              v-for="(url, index) in getImageUrls(currentTask)" 
              :key="index"
              class="image-item"
            >
              <el-image
                :src="url"
                :preview-src-list="getImageUrls(currentTask)"
                :initial-index="index"
                fit="cover"
                class="result-image"
                :loading="'lazy'"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <p>图片加载失败</p>
                  </div>
                </template>
              </el-image>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  EditPen,
  Plus,
  DocumentAdd,
  Document,
  Clock,
  Loading,
  CircleCheckFilled,
  CircleCloseFilled,
  Refresh,
  Delete,
  RefreshRight,
  View,
  InfoFilled,
  Picture,
  Download
} from '@element-plus/icons-vue'
import { text2imgAPI } from '../utils/api'

export default {
  name: 'JimengText2Img',
  components: {
    EditPen,
    Plus,
    DocumentAdd,
    Document,
    Clock,
    Loading,
    CircleCheckFilled,
    CircleCloseFilled,
    Refresh,
    Delete,
    RefreshRight,
    View,
    InfoFilled,
    Picture,
    Download
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const tasks = ref([])
    const selectedTasks = ref([])
    const statusFilter = ref(null)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const pagination = ref({
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 0
    })

    // 统计数据
    const stats = ref({
      total: 0,
      queued: 0,
      processing: 0,
      completed: 0,
      failed: 0
    })

    // 对话框状态
    const showAddTaskDialog = ref(false)
    const showBatchAddDialog = ref(false)
    const showResultDialog = ref(false)
    const addTaskLoading = ref(false)
    const batchAddLoading = ref(false)
    const batchDownloadLoading = ref(false)

    // 表单数据
    const taskForm = reactive({
      prompt: '',
      model: 'Image 3.1',
      aspect_ratio: '1:1',
      quality: '1K'
    })

    const batchForm = reactive({
      prompts: '',
      model: 'Image 3.1',
      aspect_ratio: '1:1',
      quality: '1K'
    })

    const currentTask = ref(null)

    // 表单验证规则
    const taskRules = {
      prompt: [
        { required: true, message: '请输入提示词', trigger: 'blur' },
        { min: 5, message: '提示词至少5个字符', trigger: 'blur' }
      ],
      model: [
        { required: true, message: '请选择模型', trigger: 'change' }
      ],
      aspect_ratio: [
        { required: true, message: '请选择分辨率比例', trigger: 'change' }
      ],
      quality: [
        { required: true, message: '请选择清晰度', trigger: 'change' }
      ]
    }

    const taskFormRef = ref()
    const batchFormRef = ref()

    // 获取任务列表
    const fetchTasks = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }
        if (statusFilter.value !== null) {
          params.status = statusFilter.value
        }

        const response = await text2imgAPI.getTasks(params)
        if (response.data.success) {
          tasks.value = response.data.data
          pagination.value = response.data.pagination
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('获取任务失败:', error)
        ElMessage.error('获取任务失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }

    // 获取统计信息
    const fetchStats = async () => {
      try {
        const response = await text2imgAPI.getStats()
        if (response.data.success) {
          stats.value = response.data.data
        }
      } catch (error) {
        console.error('获取统计信息失败:', error)
      }
    }

    // 刷新任务
    const refreshTasks = () => {
      fetchTasks()
      fetchStats()
    }

    // 添加单个任务
    const addTask = async () => {
      try {
        await taskFormRef.value.validate()
        addTaskLoading.value = true

        const response = await text2imgAPI.createTask(taskForm)
        if (response.data.success) {
          ElMessage.success('任务创建成功')
          showAddTaskDialog.value = false
          resetTaskForm()
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('创建任务失败:', error)
        ElMessage.error('创建任务失败')
      } finally {
        addTaskLoading.value = false
      }
    }

    // 批量添加任务
    const batchAddTasks = async () => {
      if (!batchForm.prompts.trim()) {
        ElMessage.warning('请输入提示词列表')
        return
      }

      batchAddLoading.value = true
      const prompts = batchForm.prompts.trim().split('\n').filter(line => line.trim())
      let successCount = 0
      let errorCount = 0

      try {
        for (const prompt of prompts) {
          const taskData = {
            prompt: prompt.trim(),
            model: batchForm.model,
            aspect_ratio: batchForm.aspect_ratio,
            quality: batchForm.quality,
            count: 1 // 批量添加时，count 固定为 1
          }

          try {
            const response = await text2imgAPI.createTask(taskData)
            if (response.data.success) {
              successCount++
            } else {
              errorCount++
            }
          } catch (error) {
            errorCount++
          }
        }

        ElMessage.success(`批量创建完成：成功 ${successCount} 个，失败 ${errorCount} 个`)
        if (successCount > 0) {
          showBatchAddDialog.value = false
          resetBatchForm()
          refreshTasks()
        }
      } catch (error) {
        console.error('批量创建失败:', error)
        ElMessage.error('批量创建失败')
      } finally {
        batchAddLoading.value = false
      }
    }

    // 删除任务
    const deleteTask = async (taskId) => {
      try {
        const response = await text2imgAPI.deleteTask(taskId)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('删除任务失败:', error)
        ElMessage.error('删除任务失败')
      }
    }

    // 批量删除任务
    const batchDeleteTasks = async () => {
      if (selectedTasks.value.length === 0) {
        ElMessage.warning('请选择要删除的任务')
        return
      }

      try {
        const taskIds = selectedTasks.value.map(task => task.id)
        const response = await text2imgAPI.batchDeleteTasks(taskIds)
        if (response.data.success) {
          ElMessage.success(response.data.message)
          selectedTasks.value = []
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('批量删除失败:', error)
        ElMessage.error('批量删除失败')
      }
    }

    // 重试任务
    const retryTask = async (task) => {
      try {
        const response = await text2imgAPI.retryTask(task.id)
        if (response.data.success) {
          ElMessage.success(response.data.message || '任务已重新加入队列')
          refreshTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('重试任务失败:', error)
        ElMessage.error(error.response?.data?.message || '重试任务失败')
      }
    }

    // 查看结果
    const viewResult = (task) => {
      currentTask.value = task
      showResultDialog.value = true
    }

    // 处理选择变化
    const handleSelectionChange = (selection) => {
      selectedTasks.value = selection
    }

    // 判断任务是否可选择（生成中的任务不可选择）
    const isTaskSelectable = (row) => {
      return row.status !== 1
    }

    // 计算已完成且有图片的选中任务
    const selectedCompletedTasks = computed(() => {
      if (!selectedTasks.value || !Array.isArray(selectedTasks.value)) {
        return []
      }
      return selectedTasks.value.filter(task => 
        task && task.status === 2 && (task.result_image_url || (task.images && task.images.length > 0))
      )
    })

    // 状态筛选
    const handleStatusFilter = () => {
      currentPage.value = 1
      fetchTasks()
    }

    // 分页处理
    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchTasks()
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchTasks()
    }

    // 重置添加表单
    const resetTaskForm = () => {
      Object.assign(taskForm, {
        prompt: '',
        model: 'Image 3.1',
        aspect_ratio: '1:1',
        quality: '1K'
      })
      if (taskFormRef.value) {
        taskFormRef.value.resetFields()
      }
    }

    // 重置批量添加表单
    const resetBatchForm = () => {
      Object.assign(batchForm, {
        prompts: '',
        model: 'Image 3.1',
        aspect_ratio: '1:1',
        quality: '1K'
      })
      if (batchFormRef.value) {
        batchFormRef.value.resetFields()
      }
    }

    // 工具函数
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getStatusType = (status) => {
      const statusTypes = {
        0: 'warning',  // 排队中
        1: 'primary',  // 生成中
        2: 'success',  // 已完成
        3: 'danger'    // 失败
      }
      return statusTypes[status] || 'info'
    }

    const getQualityType = (quality) => {
      if (!quality) return 'info'
      const qualityTypes = {
        'standard': 'info',
        'hd': 'success',
        'uhd': 'warning'
      }
      return qualityTypes[quality] || 'info'
    }

    const getImageUrls = (task) => {
      try {
        // 如果传入的是任务对象，处理新的数据格式
        if (task && typeof task === 'object') {
          if (task.images && Array.isArray(task.images)) {
            return task.images.filter(img => img && typeof img === 'string') // 过滤掉空值和非字符串
          }
          if (task.result_image_url) {
            if (typeof task.result_image_url === 'string' && task.result_image_url.includes(',')) {
              return task.result_image_url.split(',').map(u => u.trim()).filter(u => u)
            }
            return task.result_image_url ? [task.result_image_url] : []
          }
          return []
        }
        
        // 如果传入的是字符串URL（向后兼容）
        if (!task || typeof task !== 'string') return []
        if (task.includes(',')) {
          return task.split(',').map(u => u.trim()).filter(u => u)
        }
        return [task]
      } catch (error) {
        console.error('获取图片URL失败:', error, task)
        return []
      }
    }

    // 批量下载图片
    const batchDownloadImages = async () => {
      if (selectedCompletedTasks.value.length === 0) {
        ElMessage.warning('请选择已完成的任务')
        return
      }

      batchDownloadLoading.value = true
      try {
        const taskIds = selectedCompletedTasks.value.map(task => task.id)
        
        ElMessage.info(`准备下载 ${selectedCompletedTasks.value.length} 个任务的图片，请在弹出的对话框中选择文件夹...`)
        
        const response = await text2imgAPI.batchDownload(taskIds)
        
        if (response.data.success) {
          ElMessage.success(response.data.message)
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('批量下载失败:', error)
        ElMessage.error(error.response?.data?.message || '批量下载失败')
      } finally {
        batchDownloadLoading.value = false
      }
    }

    // 生命周期
    onMounted(() => {
      refreshTasks()
    })

    onActivated(() => {
      refreshTasks()
    })

    onUnmounted(() => {
      // 清理数据，避免内存泄漏
      tasks.value = []
      selectedTasks.value = []
      currentTask.value = null
    })

    return {
      loading,
      tasks,
      selectedTasks,
      statusFilter,
      currentPage,
      pageSize,
      pagination,
      stats,
      showAddTaskDialog,
      showBatchAddDialog,
      showResultDialog,
      addTaskLoading,
      batchAddLoading,
      taskForm,
      taskRules,
      taskFormRef,
      batchForm,
      batchFormRef,
      currentTask,
      fetchTasks,
      refreshTasks,
      addTask,
      batchAddTasks,
      deleteTask,
      batchDeleteTasks,
      retryTask,
      viewResult,
      handleSelectionChange,
      isTaskSelectable,
      handleStatusFilter,
      handleCurrentChange,
      handleSizeChange,
      resetTaskForm,
      resetBatchForm,
      truncateText,
      getStatusType,
      getQualityType,
      getImageUrls,
      selectedCompletedTasks,
      batchDownloadImages,
      batchDownloadLoading
    }
  }
}
</script>

<style scoped>
.jimeng-text2img-page {
  padding: 16px 24px;
  min-height: calc(100vh - 64px);
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

.add-task-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.batch-add-btn {
  background-color: #67C23A;
  border-color: #67C23A;
}

.batch-add-btn:hover {
  background-color: #85ce61;
  border-color: #85ce61;
}

.batch-download-btn {
  background-color: #409EFF;
  border-color: #409EFF;
}

.batch-download-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.batch-delete-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;
}

.batch-delete-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
}

.refresh-btn {
  background-color: #E6A23C;
  border-color: #E6A23C;
}

.refresh-btn:hover {
  background-color: #ebb563;
  border-color: #ebb563;
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

.prompt-cell {
  max-width: 250px;
}

.prompt-text {
  cursor: pointer;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-tag, .ratio-tag, .quality-tag {
  font-size: 12px;
  font-weight: 500;
}

.model-tag {
  background-color: #e1f3d8;
  color: #67c23a;
  border-color: #e1f3d8;
}

.ratio-tag {
  background-color: #fde2e2;
  color: #f56c6c;
  border-color: #fde2e2;
}

.quality-tag {
  background-color: #e1f3d8;
  color: #67c23a;
  border-color: #e1f3d8;
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

.status-tag.warning {
  background-color: #fde2e2;
  color: #f56c6c;
  border-color: #fde2e2;
}

.status-tag.success {
  background-color: #e1f3d8;
  color: #67c23a;
  border-color: #e1f3d8;
}

.status-tag.danger {
  background-color: #fde2e2;
  color: #f56c6c;
  border-color: #fde2e2;
}

.rotating-icon {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 空状态样式 */
.empty-state {
  padding: 40px 20px;
  text-align: center;
}

/* 对话框样式 */
.modern-dialog {
  border-radius: 12px;
}

.modern-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.modern-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.task-form, .batch-add-content {
  padding: 24px;
}

.task-form .el-form-item, .batch-add-content .el-form-item {
  margin-bottom: 20px;
}

.task-form .el-textarea, .batch-add-content .el-textarea {
  resize: vertical;
}

.task-form .el-select, .batch-add-content .el-select {
  width: 100%;
}

.task-form .full-width .el-input__inner, .batch-add-content .full-width .el-input__inner {
  width: 100%;
}

.form-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #909399;
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.cancel-btn {
  background-color: #f8f9fa;
  border-color: #e4e7ed;
  color: #606266;
}

.cancel-btn:hover {
  background-color: #f8f9fa;
  border-color: #e4e7ed;
  color: #409EFF;
}

.confirm-btn {
  background-color: #409EFF;
  border-color: #409EFF;
}

.confirm-btn:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.format-guide {
  line-height: 1.6;
}

.format-guide p {
  margin: 6px 0;
}

.example-list {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-top: 8px;
}

.example-list p {
  margin: 4px 0;
  font-family: monospace;
  color: #495057;
}

.batch-add-form {
  padding: 0;
}

.batch-stats {
  margin-top: 12px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.result-content {
  text-align: left;
}

.result-info h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.result-info p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

.result-info strong {
  color: #374151;
  font-weight: 500;
}

.result-images {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-images h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 15px;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.image-item {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 aspect ratio for images */
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}

.image-error .el-icon {
  font-size: 30px;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-text2img-page {
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
</style>