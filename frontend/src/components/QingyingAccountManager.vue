<template>
  <div class="qingying-account-manager-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">清影账号管理</h2>
        <p class="page-subtitle">管理清影平台的登录账号，支持单个添加和统一管理</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="addAccount"
          :loading="addLoading"
          size="large"
          class="primary-btn"
        >
          <el-icon><Plus /></el-icon>
          添加账号
        </el-button>
        <el-button 
          @click="refreshAccounts"
          :loading="loading"
          size="large"
          class="refresh-btn"
        >
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
        <el-popconfirm
          title="确定要清空所有清影账号吗？此操作不可恢复！"
          @confirm="clearAllAccounts"
          confirm-button-text="确定清空"
          cancel-button-text="取消"
          confirm-button-type="danger"
        >
          <template #reference>
            <el-button 
              type="danger" 
              :disabled="accounts.length === 0"
              size="large"
              class="danger-btn"
            >
              <el-icon><Delete /></el-icon>
              清空所有
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="!loading">
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">
            <el-icon size="24"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ accounts.length }}</div>
            <div class="stat-label">总账号数</div>
          </div>
        </div>
      </div>
    </div>

   

    <!-- 状态提示 -->
    <div class="status-section" v-if="statusMessage">
      <el-alert
        :title="statusMessage"
        :type="statusType"
        center
        show-icon
        :closable="false"
        class="status-alert"
      />
    </div>

    <!-- 账号表格 -->
    <div class="account-table-container">
      <el-table 
        :data="accounts" 
        v-loading="loading" 
        style="width: 100%"
        class="accounts-table"
        empty-text="暂无账号数据"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="nickname" label="昵称" min-width="150" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column prop="created_at" label="添加时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="scope">
            <el-button 
              type="danger" 
              size="small"
              @click="deleteAccount(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="pagination.total > 0">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  Plus, 
  Refresh, 
  Delete
} from '@element-plus/icons-vue'
import { qingyingAccountAPI } from '@/utils/api'

// 响应式数据
const loading = ref(false)
const accounts = ref([])

// 统计数据
const stats = reactive({
  total_accounts: 0,
  accounts_with_cookies: 0,
  accounts_without_cookies: 0
})

// 分页数据
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 添加账号相关
const addLoading = ref(false)

// 状态消息
const statusMessage = ref('')
const statusType = ref('info')

// 方法
const loadAccounts = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await qingyingAccountAPI.getAccounts(params)
    
    if (response.data.success) {
      accounts.value = response.data.data.map(account => ({
        ...account,
        loading: false
      }))
      pagination.total = response.data.pagination.total
      
      // 更新状态消息
      if (accounts.value.length === 0) {
        statusMessage.value = '暂无清影账号，点击"添加账号"开始添加'
        statusType.value = 'info'
      } else {
        statusMessage.value = ''
      }
    } else {
      ElMessage.error(response.data.message || '获取账号列表失败')
    }
  } catch (error) {
    console.error('获取账号列表失败:', error)
    ElMessage.error('获取账号列表失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await qingyingAccountAPI.getUsageStats()
    
    if (response.data.success) {
      Object.assign(stats, response.data.data)
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const refreshAccounts = () => {
  loadAccounts()
  loadStats()
}

const addAccount = async () => {
  try {
    addLoading.value = true
    
    const response = await qingyingAccountAPI.addAccount()
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '正在打开浏览器，请完成登录')
      // 延迟刷新账号列表
      setTimeout(() => {
        refreshAccounts()
      }, 5000)
    } else {
      ElMessage.error(response.data.message || '添加账号失败')
    }
  } catch (error) {
    console.error('添加账号失败:', error)
    ElMessage.error('添加账号失败')
  } finally {
    addLoading.value = false
  }
}

const deleteAccount = async (account) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除账号 "${account.nickname}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await qingyingAccountAPI.deleteAccount(account.id)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '删除账号成功')
      await refreshAccounts()
    } else {
      ElMessage.error(response.data.message || '删除账号失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除账号失败:', error)
      ElMessage.error('删除账号失败')
    }
  }
}

const clearAllAccounts = async () => {
  try {
    const response = await qingyingAccountAPI.clearAllAccounts()
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '清空账号成功')
      await refreshAccounts()
    } else {
      ElMessage.error(response.data.message || '清空账号失败')
    }
  } catch (error) {
    console.error('清空账号失败:', error)
    ElMessage.error('清空账号失败')
  }
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadAccounts()
}

const handleSizeChange = (size) => {
  pagination.page = 1
  pagination.page_size = size
  loadAccounts()
}

// 生命周期
onMounted(() => {
  refreshAccounts()
})

onActivated(() => {
  refreshAccounts()
})
</script>

<style scoped>
.qingying-account-manager-page {
  padding: 24px;
  min-height: 100vh;
  background: transparent;
}

/* 页面头部 */
.page-header {
  max-width: 1200px;
  margin: 0 auto 24px auto;
  background: var(--bg-primary);
  padding: 24px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--success-gradient);
  opacity: 0.03;
  z-index: -1;
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  background: var(--success-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn {
  background: var(--primary-gradient);
  border: none;
  color: white;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.refresh-btn {
  background: var(--accent-gradient);
  border: none;
  color: white;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.danger-btn {
  background: var(--danger-gradient);
  border: none;
  color: white;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
}

.danger-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
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
  flex-shrink: 0;
  transition: var(--transition);
}

.stat-card.primary .stat-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  margin: 0;
}



/* 状态提示 */
.status-section {
  margin-bottom: 24px;
}

.status-alert {
  border-radius: var(--radius-md);
}

/* 表格容器样式 */
.account-table-container {
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: auto;
}

.accounts-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.accounts-table :deep(.el-table__header-wrapper th) {
  background-color: #f8fafc;
  color: #374151;
  font-weight: 600;
}

.accounts-table :deep(.el-table__header-wrapper th:first-child) {
  border-top-left-radius: 12px;
}

.accounts-table :deep(.el-table__header-wrapper th:last-child) {
  border-top-right-radius: 12px;
}

.accounts-table :deep(.el-table__body-wrapper tr:last-child td:first-child) {
  border-bottom-left-radius: 12px;
}

.accounts-table :deep(.el-table__body-wrapper tr:last-child td:last-child) {
  border-bottom-right-radius: 12px;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .qingying-account-manager-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    padding: 20px;
  }
}
</style> 