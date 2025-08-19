<template>
  <div class="jimeng-account-manager-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">即梦账号管理</h2>
        <p class="page-subtitle">管理即梦平台的登录账号，支持批量导入和统一管理</p>
      </div>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="showAddDialog = true"
          size="large"
          class="primary-btn"
        >
          <el-icon><Plus /></el-icon>
          批量添加
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
          title="确定要清空所有即梦账号吗？此操作不可恢复！"
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
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon size="24"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ lastUpdateTime }}</div>
            <div class="stat-label">最近更新</div>
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-icon">
            <el-icon size="24"><DataBoard /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ usageStats.summary.available_accounts }}</div>
            <div class="stat-label">可用账号</div>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon">
            <el-icon size="24"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ usageStats.summary.total_today_usage }}</div>
            <div class="stat-label">今日已用</div>
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon size="24"><DataBoard /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ usageStats.summary.total_remaining }}</div>
            <div class="stat-label">今日剩余</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 状态提示 -->
    <div class="status-section" v-if="statusMessage">
      <el-alert
        :title="statusMessage"
        :type="statusType"
        :closable="true"
        @close="clearStatus"
        show-icon
        class="status-alert"
      />
    </div>

    <!-- 账号列表 -->
    <div class="account-table-container">
      <!-- 空状态 -->
      <el-empty 
        v-if="accounts.length === 0 && !loading" 
        description="暂无即梦账号数据"
        class="empty-state"
      >
        <el-button 
          type="primary" 
          @click="showAddDialog = true"
          :icon="Plus"
        >
          添加第一个账号
        </el-button>
      </el-empty>

      <!-- 账号表格 -->
      <el-table 
        v-else
        :data="paginatedAccounts" 
        stripe 
        v-loading="loading"
        class="account-table"
        :default-sort="{ prop: 'updated_at', order: 'descending' }"
      >
        <el-table-column 
          prop="id" 
          label="ID" 
          width="70" 
          align="center"
          sortable
        />
        <el-table-column 
          prop="account" 
          label="账号"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <div class="account-cell">
              <el-icon color="#409EFF"><Message /></el-icon>
              <span>{{ row.account }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          prop="password" 
          label="密码" 
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <div class="password-cell">
              <span v-if="!showPassword[row.id]" class="masked-password">
                {{ maskPassword(row.password) }}
              </span>
              <span v-else class="real-password">{{ row.password }}</span>
              <el-button
                :icon="showPassword[row.id] ? Hide : View"
                size="small"
                text
                @click="togglePassword(row.id)"
                class="password-toggle"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column 
          prop="cookies" 
          label="Cookies状态" 
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag 
              :type="row.cookies ? 'success' : 'info'" 
              size="small"
              effect="plain"
            >
              {{ row.cookies ? '已设置' : '未设置' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column 
          prop="created_at" 
          label="创建时间" 
          width="160"
          sortable
        />
        
        <el-table-column 
          prop="updated_at" 
          label="更新时间" 
          width="160"
          sortable
        />
        
        <el-table-column 
          label="今日使用" 
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <div class="usage-info">
              <span class="usage-text">
                {{ getAccountUsage(row.id).today_text2img }}/10
              </span>
              <el-progress 
                :percentage="getAccountUsage(row.id).today_text2img * 10" 
                :stroke-width="4"
                :show-text="false"
                :color="getUsageColor(getAccountUsage(row.id).today_text2img)"
              />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          label="状态" 
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag 
              :type="getAccountUsage(row.id).status === 'available' ? 'success' : 'danger'"
              size="small"
            >
              {{ getAccountUsage(row.id).status === 'available' ? '可用' : '已满' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column 
          label="操作" 
          width="120" 
          fixed="right"
          align="center"
        >
          <template #default="{ row }">
            <el-popconfirm
              :title="`确定删除账号 ${row.account} 吗？`"
              @confirm="deleteAccount(row.id)"
              confirm-button-text="删除"
              cancel-button-text="取消"
              confirm-button-type="danger"
            >
              <template #reference>
                <el-button 
                  type="danger" 
                  size="small" 
                  text
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="accounts.length > pageSize">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="accounts.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 添加账号对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="批量添加即梦国际版账号"
      width="700px"
      @close="resetAddForm"
      class="add-dialog"
    >
      <div class="add-form">
        <!-- 格式说明卡片 -->
        <el-card shadow="never" class="format-card">
          <template #header>
            <div class="card-header">
              <el-icon><DocumentAdd /></el-icon>
              <span>输入格式说明</span>
            </div>
          </template>
          
          <div class="format-examples">
            <div class="format-item">
              <el-tag type="primary" size="small">格式1</el-tag>
              <code>账号----密码</code>
            </div>
            <div class="format-item">
              <el-tag type="success" size="small">格式2</el-tag>
              <code>账号----密码----cookies</code>
            </div>
          </div>
          
          <div class="format-note">
            <el-icon color="#E6A23C"><Warning /></el-icon>
            <span>每行一个账号，使用 ---- 分隔各字段</span>
          </div>
        </el-card>

        <!-- 输入区域 -->
        <div class="input-section">
          <el-input
            v-model="newAccountsText"
            type="textarea"
            :rows="8"
            placeholder="请按上述格式输入账号信息，例如：&#10;user1@email.com----password123&#10;user2@email.com----password456----cookie_data_here"
            class="account-input"
            show-word-limit
            :maxlength="10000"
          />
          
          <div class="input-stats">
            <span class="line-count">
              行数: {{ newAccountsText.split('\n').filter(line => line.trim()).length }}
            </span>
          </div>
        </div>

        <!-- 对话框按钮 -->
        <div class="dialog-actions">
          <el-button @click="showAddDialog = false" size="default">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="addAccounts"
            :loading="addLoading"
            :disabled="!newAccountsText.trim()"
            size="default"
          >
            <el-icon><Plus /></el-icon>
            确认添加
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onActivated } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, 
  Refresh, 
  Delete, 
  User,
  Clock,
  Message,
  View,
  Hide,
  DocumentAdd,
  Warning,
  DataBoard
} from '@element-plus/icons-vue'
import { accountAPI } from '../utils/api'

export default {
  name: 'JimengAccountManager',
  components: {
    Plus,
    Refresh,
    Delete,
    User,
    Clock,
    Message,
    View,
    Hide,
    DocumentAdd,
    Warning,
    DataBoard
  },
  setup() {
    // 响应式数据
    const accounts = ref([])
    const loading = ref(false)
    const addLoading = ref(false)
    const showAddDialog = ref(false)
    const newAccountsText = ref('')
    const statusMessage = ref('')
    const statusType = ref('success')
    const showPassword = ref({})
    const currentPage = ref(1)
    const pageSize = ref(10)
    const usageStats = ref({
      accounts: [],
      summary: {
        total_accounts: 0,
        available_accounts: 0,
        total_today_usage: 0,
        total_remaining: 0
      }
    })

    // 计算属性
    const lastUpdateTime = computed(() => {
      if (accounts.value.length === 0) return '无'
      const latest = accounts.value.reduce((latest, account) => {
        return new Date(account.updated_at) > new Date(latest.updated_at) ? account : latest
      })
      return latest.updated_at
    })

    const paginatedAccounts = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return accounts.value.slice(start, end)
    })

    // 获取账号列表
    const fetchAccounts = async () => {
      loading.value = true
      try {
        const response = await accountAPI.getAccounts()
        if (response.data.success) {
          accounts.value = response.data.data
          setStatus(response.data.message, 'success')
        } else {
          setStatus(response.data.message, 'error')
        }
      } catch (error) {
        console.error('获取账号失败:', error)
        setStatus('获取账号失败，请检查后端服务是否正常运行', 'error')
      } finally {
        loading.value = false
      }
    }

    // 刷新账号
    const refreshAccounts = () => {
      fetchAccounts()
    }

    // 添加账号
    const addAccounts = async () => {
      if (!newAccountsText.value.trim()) {
        ElMessage.warning('请输入账号信息')
        return
      }

      addLoading.value = true
      try {
        const response = await accountAPI.addAccounts(newAccountsText.value)
        if (response.data.success) {
          setStatus(response.data.message, 'success')
          showAddDialog.value = false
          resetAddForm()
          await fetchAccounts()
        } else {
          setStatus(response.data.message, 'error')
        }
      } catch (error) {
        console.error('添加账号失败:', error)
        setStatus('添加账号失败', 'error')
      } finally {
        addLoading.value = false
      }
    }

    // 删除账号
    const deleteAccount = async (accountId) => {
      try {
        const response = await accountAPI.deleteAccount(accountId)
        if (response.data.success) {
          setStatus(response.data.message, 'success')
          await fetchAccounts()
        } else {
          setStatus(response.data.message, 'error')
        }
      } catch (error) {
        console.error('删除账号失败:', error)
        setStatus('删除账号失败', 'error')
      }
    }

    // 清空所有账号
    const clearAllAccounts = async () => {
      try {
        const response = await accountAPI.clearAllAccounts()
        if (response.data.success) {
          setStatus(response.data.message, 'warning')
          await fetchAccounts()
          currentPage.value = 1
        } else {
          setStatus(response.data.message, 'error')
        }
      } catch (error) {
        console.error('清空账号失败:', error)
        setStatus('清空账号失败', 'error')
      }
    }

    // 切换密码显示
    const togglePassword = (accountId) => {
      showPassword.value[accountId] = !showPassword.value[accountId]
    }

    // 密码遮盖显示
    const maskPassword = (password) => {
      if (!password) return ''
      if (password.length <= 4) return '*'.repeat(password.length)
      return password.substring(0, 2) + '*'.repeat(password.length - 4) + password.substring(password.length - 2)
    }

    // 设置状态消息
    const setStatus = (message, type) => {
      statusMessage.value = message
      statusType.value = type
      setTimeout(clearStatus, 5000)
    }

    // 清除状态消息
    const clearStatus = () => {
      statusMessage.value = ''
    }

    // 重置添加表单
    const resetAddForm = () => {
      newAccountsText.value = ''
    }

    // 分页处理
    const handlePageChange = (page) => {
      currentPage.value = page
    }

    // 获取使用统计
    const fetchUsageStats = async () => {
      try {
        const response = await accountAPI.getUsageStats()
        if (response.data.success) {
          usageStats.value = response.data.data
        } else {
          console.error('获取使用统计失败:', response.data.message)
        }
      } catch (error) {
        console.error('获取使用统计异常:', error)
      }
    }

    // 刷新所有数据
    const refreshAll = async () => {
      await Promise.all([
        fetchAccounts(),
        fetchUsageStats()
      ])
    }

    // 获取账号使用情况
    const getAccountUsage = (accountId) => {
      const usage = usageStats.value.accounts.find(acc => acc.id === accountId)
      return usage || {
        today_text2img: 0,
        today_remaining: 10,
        status: 'available'
      }
    }

    // 获取使用情况颜色
    const getUsageColor = (usage) => {
      if (usage >= 10) return '#f56c6c'  // 红色 - 已满
      if (usage >= 7) return '#e6a23c'   // 橙色 - 接近上限
      if (usage >= 4) return '#409eff'   // 蓝色 - 中等使用
      return '#67c23a'                   // 绿色 - 使用较少
    }

    // 生命周期
    onMounted(refreshAll)
    onActivated(refreshAll)

    return {
      accounts,
      loading,
      addLoading,
      showAddDialog,
      newAccountsText,
      statusMessage,
      statusType,
      showPassword,
      currentPage,
      pageSize,
      usageStats,
      lastUpdateTime,
      paginatedAccounts,
      fetchAccounts,
      refreshAccounts,
      addAccounts,
      deleteAccount,
      clearAllAccounts,
      togglePassword,
      maskPassword,
      setStatus,
      clearStatus,
      resetAddForm,
      handlePageChange,
      fetchUsageStats,
      refreshAll,
      getAccountUsage,
      getUsageColor
    }
  }
}
</script>

<style scoped>
.jimeng-account-manager-page {
  padding: 24px;
  min-height: 100vh;
  background: transparent;
}

/* 页面头部 */
.page-header {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  margin-bottom: 24px;
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
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-md);
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
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  left: 0;
}

.stat-card.primary .stat-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.stat-card.success .stat-icon {
  background: rgba(78, 205, 196, 0.1);
  color: #4ecdc4;
}

.stat-card.info .stat-icon {
  background: rgba(79, 172, 254, 0.1);
  color: #4facfe;
}

.stat-card.warning .stat-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
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

.stat-card:hover .stat-icon {
  background: var(--primary-gradient);
  color: white;
  transform: scale(1.1);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 状态提示 */
.status-section {
  margin-bottom: 24px;
}

.status-alert {
  border-radius: var(--radius-md);
}

/* 操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.left-actions, .right-actions {
  display: flex;
  gap: 12px;
}

/* 统计信息样式 */
.stats-bar {
  margin-bottom: 20px;
}

.stats-card {
  border: none;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  color: #2c3e50;
  font-weight: 600;
  font-size: 16px;
}

.stat-divider {
  width: 1px;
  height: 20px;
  background: #e4e7ed;
}

/* 状态提示样式 */
.status-alert {
  margin-bottom: 20px;
  border-radius: 8px;
}

/* 表格容器样式 */
.account-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
}

.empty-state {
  padding: 60px 20px;
}

.account-table {
  width: 100%;
}

.account-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.password-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.masked-password, .real-password {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.masked-password {
  color: #999;
}

.password-toggle {
  padding: 2px !important;
  min-height: auto !important;
}

/* 分页样式 */
.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #f0f0f0;
}

/* 对话框样式 */
.add-dialog .el-dialog__body {
  padding: 20px 24px;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.format-card {
  border: 1px solid #e1f3ff;
  background: #f6fbff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409EFF;
}

.format-examples {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.format-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.format-item code {
  background: #f0f2f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #2c3e50;
}

.format-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fdf6ec;
  border-left: 4px solid #E6A23C;
  border-radius: 4px;
  font-size: 13px;
  color: #E6A23C;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.account-input {
  font-family: 'Courier New', monospace;
}

.input-stats {
  display: flex;
  justify-content: flex-end;
  font-size: 12px;
  color: #999;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

/* 使用情况样式 */
.usage-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.usage-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-account-manager {
    padding: 16px;
  }

  .action-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .left-actions, .right-actions {
    justify-content: center;
  }

  .stats-content {
    justify-content: center;
  }

  .add-dialog {
    width: 95% !important;
  }
}
</style>