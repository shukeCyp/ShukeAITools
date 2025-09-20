<template>
  <div class="jimeng-page base-config-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><Setting /></el-icon>
          </div>
          <div class="title-content">
            <h1 class="page-title">基础配置</h1>
            <p class="page-subtitle">配置系统基础参数和全局设置</p>
          </div>
        </div>
        <div class="status-section">
          <el-tag 
            :type="loading ? 'warning' : 'success'" 
            size="large"
            class="status-tag"
          >
            <el-icon class="status-icon">
              <component :is="loading ? 'Loading' : 'SuccessFilled'" />
            </el-icon>
            {{ loading ? '加载中...' : '配置就绪' }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 配置内容 -->
    <div class="config-content">
      <div class="config-card">
        <div class="card-header">
          <div class="card-icon">
            <el-icon size="32"><Setting /></el-icon>
          </div>
          <div class="card-info">
            <h3 class="card-title">系统设置</h3>
          </div>
        </div>

        <div class="config-list">
          <div class="config-item">
            <div class="item-header">
              <div class="item-icon">
                <el-icon size="20"><Cpu /></el-icon>
              </div>
              <div class="item-info">
                <h4 class="item-title">自动化最大线程数</h4>
                <p class="item-desc">控制同时处理的任务数量，建议设置为1-5</p>
              </div>
            </div>
            <div class="item-control">
              <el-input-number
                v-model="configForm.automation_max_threads"
                :min="1"
                :max="10"
                :step="1"
                size="large"
                controls-position="right"
                @change="handleConfigChange"
                :disabled="loading"
              />
            </div>
          </div>

          <div class="config-item">
            <div class="item-header">
              <div class="item-icon">
                <el-icon size="20"><Monitor /></el-icon>
              </div>
              <div class="item-info">
                <h4 class="item-title">隐藏浏览器窗口</h4>
                <p class="item-desc">启用后任务处理时将在后台运行，提高系统效率</p>
              </div>
            </div>
            <div class="item-control">
              <el-switch
                v-model="configForm.hide_window"
                active-text="启用"
                inactive-text="禁用"
                @change="handleConfigChange"
                size="large"
                :disabled="loading"
                inline-prompt
              />
            </div>
          </div>

          <div class="config-item">
            <div class="item-header">
              <div class="item-icon">
                <el-icon size="20"><Refresh /></el-icon>
              </div>
              <div class="item-info">
                <h4 class="item-title">自动重试失败任务</h4>
                <p class="item-desc">启用后系统将自动重试因网络问题导致的失败任务（最多重试2次）</p>
              </div>
            </div>
            <div class="item-control">
              <el-switch
                v-model="configForm.auto_retry_enabled"
                active-text="启用"
                inactive-text="禁用"
                @change="handleConfigChange"
                size="large"
                :disabled="loading"
                inline-prompt
              />
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="config-actions">
          <el-button 
            class="btn-save action-btn primary-btn"
            :loading="saveLoading" 
            @click="saveConfigs"
            size="large"
          >
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
          <el-button 
            :loading="loading" 
            @click="resetConfigs"
            size="large"
            class="action-btn secondary-btn"
          >
            <el-icon><RefreshLeft /></el-icon>
            重置配置
          </el-button>
          <el-button 
            :loading="loading" 
            @click="loadConfigs"
            size="large"
            class="action-btn refresh-btn"
          >
            <el-icon><Refresh /></el-icon>
            刷新配置
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Setting, 
  Check, 
  RefreshLeft, 
  Refresh,
  Loading,
  SuccessFilled,
  InfoFilled,
  Cpu,
  Monitor
} from '@element-plus/icons-vue'
import { configAPI } from '../utils/api'

export default {
  name: 'BaseConfig',
  components: {
    Setting,
    Check,
    RefreshLeft,
    Refresh,
    Loading,
    SuccessFilled,
    InfoFilled,
    Cpu,
    Monitor
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const saveLoading = ref(false)
    const configFormRef = ref()

    // 配置表单数据
    const configForm = reactive({
      automation_max_threads: 3,
      hide_window: false,
      auto_retry_enabled: false
    })

    // 原始配置数据（用于重置）
    const originalConfig = reactive({
      automation_max_threads: 3,
      hide_window: false,
      auto_retry_enabled: false
    })

    // 页面挂载后加载配置
    onMounted(() => {
      loadConfigs()
    })

    // 加载配置
    const loadConfigs = async () => {
      try {
        loading.value = true
        console.log('开始加载系统配置...')
        
        const response = await configAPI.getAllConfigs()
        if (response.data.success) {
          const configs = response.data.data
          
          // 更新表单数据
          if (configs.automation_max_threads) {
            configForm.automation_max_threads = parseInt(configs.automation_max_threads.value) || 3
            originalConfig.automation_max_threads = configForm.automation_max_threads
          }
          
          if (configs.hide_window) {
            configForm.hide_window = configs.hide_window.value === 'true'
            originalConfig.hide_window = configForm.hide_window
          }
          
          if (configs.auto_retry_enabled) {
            configForm.auto_retry_enabled = configs.auto_retry_enabled.value === 'true'
            originalConfig.auto_retry_enabled = configForm.auto_retry_enabled
          }
          
          console.log('配置加载成功:', configForm)
        } else {
          ElMessage.error('加载配置失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('加载配置异常:', error)
        ElMessage.error('加载配置失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }

    // 配置变更处理（实时保存）
    const handleConfigChange = async () => {
      console.log('配置发生变更:', configForm)
      // 可以在这里实现实时保存，或者只是标记为已修改
    }

    // 保存配置
    const saveConfigs = async () => {
      try {
        saveLoading.value = true
        console.log('开始保存配置:', configForm)
        
        // 批量更新配置
        const configs = {
          automation_max_threads: configForm.automation_max_threads.toString(),
          hide_window: configForm.hide_window.toString(),
          auto_retry_enabled: configForm.auto_retry_enabled.toString()
        }
        
        const response = await configAPI.updateBatchConfigs(configs)
        if (response.data.success) {
          ElMessage.success('配置保存成功')
          // 更新原始配置数据
          Object.assign(originalConfig, configForm)
        } else {
          ElMessage.error('配置保存失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('保存配置异常:', error)
        ElMessage.error('保存配置失败，请检查网络连接')
      } finally {
        saveLoading.value = false
      }
    }

    // 重置配置
    const resetConfigs = () => {
      console.log('重置配置到原始值:', originalConfig)
      Object.assign(configForm, originalConfig)
      ElMessage.info('配置已重置')
    }

    return {
      loading,
      saveLoading,
      configFormRef,
      configForm,
      loadConfigs,
      handleConfigChange,
      saveConfigs,
      resetConfigs
    }
  }
}
</script>

<style scoped>
@import '../styles/jimeng-common.css';

/* 基础配置页面特定样式 */
.title-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.status-tag {
  font-size: 16px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  font-weight: 600;
}

.status-icon {
  margin-right: 8px;
}

/* 配置卡片 */
.config-content {
  max-width: 1200px;
  margin: 0 auto;
}

.config-card {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.config-card::before {
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

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.card-icon {
  background: var(--primary-gradient);
  color: white;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

/* 配置列表 */
.config-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.config-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--primary-gradient);
  transition: var(--transition);
  opacity: 0.03;
  z-index: -1;
}

.config-item:hover {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: var(--shadow-sm);
}

.config-item:hover::before {
  left: 0;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.item-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.item-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

.item-control {
  flex-shrink: 0;
}

/* 操作按钮 */
.config-actions {
  display: flex;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
}

/* 按钮样式已移至全局样式 */

.primary-btn {
  background: var(--primary-gradient);
  border: none;
  color: white;
  box-shadow: var(--shadow-sm);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.secondary-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.secondary-btn:hover {
  background: var(--bg-primary);
  border-color: var(--border-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.refresh-btn {
  background: var(--accent-gradient);
  border: none;
  color: white;
  box-shadow: var(--shadow-sm);
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .base-config-page {
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
  
  .config-card {
    padding: 24px;
  }
  
  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .config-item {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 20px;
  }
  
  .item-header {
    justify-content: center;
    text-align: center;
  }
  
  .config-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .config-card {
    padding: 20px;
  }
  
  .section-title {
    padding: 12px 16px;
  }
  
  .section-title span {
    font-size: 16px;
  }
}
</style>