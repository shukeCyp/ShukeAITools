<template>
  <div class="jimeng-page account-configuration-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="title-content">
            <h1 class="page-title">账号配置</h1>
            <p class="page-subtitle">管理各平台账号信息，配置自动化任务所需的登录凭证</p>
          </div>
        </div>
        <div class="status-section">
          <el-button 
            type="success" 
            size="large"
            @click="showAccountManager = true"
            class="account-btn"
          >
            <el-icon><User /></el-icon>
            账号管理
            <el-badge 
              :value="jimengCount" 
              :hidden="jimengCount === 0"
              class="inline-badge"
            />
          </el-button>
        </div>
      </div>
    </div>

    <!-- 平台选择 -->
    <div class="platform-section">
      <div class="platform-tabs">
        <div class="tab-header">
          <h3>选择平台</h3>
          <p>选择要配置的AI平台账号</p>
        </div>
        
        <el-tabs 
          v-model="activeTab" 
          class="modern-tabs"
          @tab-change="handleTabChange"
        >
          <!-- 即梦国际版 -->
          <el-tab-pane name="jimeng">
            <template #label>
              <div class="tab-label">
                <el-icon><Picture /></el-icon>
                <span>即梦国际版</span>
                <el-badge 
                  :value="jimengCount" 
                  :hidden="jimengCount === 0"
                  type="danger"
                  class="tab-badge"
                />
              </div>
            </template>
            
            <!-- 功能导航 -->
            <div class="function-navigation">
              <div class="nav-buttons">
                <el-button
                  v-for="drawer in drawers"
                  :key="drawer.key"
                  :type="activeDrawer === drawer.key ? 'primary' : ''"
                  @click="openDrawer(drawer.key)"
                  class="nav-btn"
                  size="large"
                >
                  <el-icon><component :is="drawer.icon" /></el-icon>
                  {{ drawer.title }}
                </el-button>
              </div>
            </div>
            
            <!-- 功能模块预览 -->
            <div class="feature-showcase" v-if="!currentDrawerOpen">
              <div class="showcase-grid">
                <div 
                  v-for="drawer in drawers"
                  :key="drawer.key"
                  class="feature-card"
                  @click="openDrawer(drawer.key)"
                >
                  <div class="card-icon">
                    <el-icon size="32"><component :is="drawer.icon" /></el-icon>
                  </div>
                  <div class="card-content">
                    <h4>{{ drawer.title }}</h4>
                    <p>{{ drawer.description }}</p>
                    <div class="card-status">
                      <el-tag 
                        :type="drawer.status === 'active' ? 'success' : 'warning'" 
                        class="status-tag"
                      >
                        {{ drawer.status === 'active' ? '可用' : '开发中' }}
                      </el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 账号管理抽屉 -->
    <el-drawer
      v-model="showAccountManager"
      title="即梦账号管理"
      size="80%"
      direction="rtl"
      class="account-drawer"
    >
      <JimengAccountManager @account-changed="updateJimengCount" />
    </el-drawer>

    <!-- 文生图抽屉 -->
    <el-drawer
      v-model="drawers[0].visible"
      :title="drawers[0].title"
      size="80%"
      direction="rtl"
      class="feature-drawer"
      @close="currentDrawerOpen = false"
    >
      <div class="drawer-placeholder">
        <el-empty description="文生图功能界面">
          <div class="placeholder-content">
            <el-icon size="64" color="#409EFF"><PictureFilled /></el-icon>
            <h3>文生图功能</h3>
            <p>基于AI的文字转图片生成功能，支持多种风格和参数调节</p>
            <div class="placeholder-features">
              <el-tag>风格选择</el-tag>
              <el-tag>尺寸调节</el-tag>
              <el-tag>批量生成</el-tag>
              <el-tag>历史记录</el-tag>
            </div>
          </div>
        </el-empty>
      </div>
    </el-drawer>

    <!-- 图生视频抽屉 -->
    <el-drawer
      v-model="drawers[1].visible"
      :title="drawers[1].title"
      size="80%"
      direction="rtl"
      class="feature-drawer"
      @close="currentDrawerOpen = false"
    >
      <div class="drawer-placeholder">
        <el-empty description="图生视频功能界面">
          <div class="placeholder-content">
            <el-icon size="64" color="#67C23A"><VideoPlay /></el-icon>
            <h3>图生视频功能</h3>
            <p>将静态图片转换为动态视频，支持多种动画效果和时长设置</p>
            <div class="placeholder-features">
              <el-tag type="success">动画效果</el-tag>
              <el-tag type="success">时长控制</el-tag>
              <el-tag type="success">质量调节</el-tag>
              <el-tag type="success">预览播放</el-tag>
            </div>
          </div>
        </el-empty>
      </div>
    </el-drawer>

    <!-- 数字人抽屉 -->
    <el-drawer
      v-model="drawers[2].visible"
      :title="drawers[2].title"
      size="80%"
      direction="rtl"
      class="feature-drawer"
      @close="currentDrawerOpen = false"
    >
      <div class="drawer-placeholder">
        <el-empty description="数字人功能界面">
          <div class="placeholder-content">
            <el-icon size="64" color="#E6A23C"><Avatar /></el-icon>
            <h3>数字人功能</h3>
            <p>AI驱动的虚拟数字人生成，支持表情、动作和语音合成</p>
            <div class="placeholder-features">
              <el-tag type="warning">形象定制</el-tag>
              <el-tag type="warning">表情控制</el-tag>
              <el-tag type="warning">语音合成</el-tag>
              <el-tag type="warning">动作驱动</el-tag>
            </div>
          </div>
        </el-empty>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import { ref, onMounted, onActivated, reactive } from 'vue'
import {
  Picture,
  User,
  PictureFilled,
  VideoPlay,
  Avatar,
  EditPen,
  Film,
  UserFilled
} from '@element-plus/icons-vue'
import JimengAccountManager from '../components/JimengAccountManager.vue'
import { accountAPI } from '../utils/api'

export default {
  name: 'AccountConfiguration',
  components: {
    JimengAccountManager,
    Picture,
    User,
    PictureFilled,
    VideoPlay,
    Avatar,
    EditPen,
    Film,
    UserFilled
  },
  setup() {
    // 响应式数据
    const activeTab = ref('jimeng')
    const jimengCount = ref(0)
    const activeDrawer = ref('')
    const showAccountManager = ref(false)
    const currentDrawerOpen = ref(false)

    // 抽屉配置
    const drawers = reactive([
      {
        key: 'text2img',
        title: '文生图',
        icon: EditPen,
        color: '#409EFF',
        description: '基于AI的文字转图片生成功能，支持多种风格和参数调节',
        status: 'developing',
        visible: false
      },
      {
        key: 'img2video',
        title: '图生视频',
        icon: Film,
        color: '#67C23A',
        description: '将静态图片转换为动态视频，支持多种动画效果和时长设置',
        status: 'developing',
        visible: false
      },
      {
        key: 'digital_human',
        title: '数字人',
        icon: UserFilled,
        color: '#E6A23C',
        description: 'AI驱动的虚拟数字人生成，支持表情、动作和语音合成',
        status: 'developing',
        visible: false
      }
    ])

    // 更新即梦账号数量
    const updateJimengCount = async () => {
      try {
        const response = await accountAPI.getAccounts()
        if (response.data.success) {
          jimengCount.value = response.data.data.length
        }
      } catch (error) {
        console.error('获取账号数量失败:', error)
      }
    }

    // 打开抽屉
    const openDrawer = (drawerKey) => {
      // 关闭所有抽屉
      drawers.forEach(drawer => {
        drawer.visible = false
      })
      
      // 打开指定抽屉
      const targetDrawer = drawers.find(d => d.key === drawerKey)
      if (targetDrawer) {
        targetDrawer.visible = true
        activeDrawer.value = drawerKey
        currentDrawerOpen.value = true
      }
    }

    // 标签页切换处理
    const handleTabChange = (tabName) => {
      console.log('切换到标签页:', tabName)
      // 关闭所有抽屉
      drawers.forEach(drawer => {
        drawer.visible = false
      })
      activeDrawer.value = ''
      currentDrawerOpen.value = false
    }

    // 生命周期
    onMounted(() => {
      updateJimengCount()
    })

    onActivated(() => {
      updateJimengCount()
    })

    return {
      activeTab,
      jimengCount,
      activeDrawer,
      showAccountManager,
      currentDrawerOpen,
      drawers,
      updateJimengCount,
      openDrawer,
      handleTabChange
    }
  }
}
</script>

<style scoped>
@import '../styles/jimeng-common.css';

.account-configuration-page {
  padding: 16px 24px;
  min-height: calc(100vh - 64px);
}

/* 账户配置页面特定样式 */
.title-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.account-btn {
  background: var(--success-gradient);
  border: none;
  color: white;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
  position: relative;
}

.account-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.inline-badge {
  margin-left: 8px;
}

/* 平台选择区域 */
.platform-section {
  max-width: 1200px;
  margin: 0 auto;
}

.platform-tabs {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.platform-tabs::before {
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

.tab-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.tab-header h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.tab-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 现代化标签页 */
.modern-tabs :deep(.el-tabs__header) {
  margin: 0 0 24px 0;
  border-bottom: 2px solid var(--border-light);
}

.modern-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.modern-tabs :deep(.el-tabs__item) {
  padding: 16px 24px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  transition: var(--transition);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  margin-right: 8px;
}

.modern-tabs :deep(.el-tabs__item.is-active) {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom: 3px solid #4ecdc4;
  font-weight: 600;
}

.modern-tabs :deep(.el-tabs__item:hover) {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.modern-tabs :deep(.el-tabs__content) {
  padding: 0;
}

/* 标签页标签 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tab-badge {
  margin-left: 4px;
}

/* 功能导航 */
.function-navigation {
  margin-bottom: 32px;
}

.nav-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.nav-btn {
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: var(--transition);
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: #4ecdc4;
}

.nav-btn.el-button--primary {
  background: var(--success-gradient);
  border: none;
  color: white;
  box-shadow: var(--shadow-sm);
}

.nav-btn.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 功能展示 */
.feature-showcase {
  margin-top: 24px;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 24px;
  border: 1px solid var(--border-light);
  transition: var(--transition);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--success-gradient);
  transition: var(--transition);
  opacity: 0.05;
  z-index: -1;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(78, 205, 196, 0.3);
}

.feature-card:hover::before {
  left: 0;
}

.card-icon {
  background: rgba(78, 205, 196, 0.1);
  color: #4ecdc4;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: var(--transition);
}

.feature-card:hover .card-icon {
  background: var(--success-gradient);
  color: white;
  transform: scale(1.1);
}

.card-content {
  flex: 1;
}

.card-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.card-content p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.card-status {
  display: flex;
  justify-content: flex-start;
}

.status-tag {
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  padding: 4px 8px;
}

/* 抽屉样式 */
.account-drawer :deep(.el-drawer__header) {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 0;
  padding: 20px 24px;
}

.account-drawer :deep(.el-drawer__title) {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 18px;
}

.feature-drawer :deep(.el-drawer__header) {
  background: var(--primary-gradient);
  color: white;
  margin-bottom: 0;
  padding: 20px 24px;
}

.feature-drawer :deep(.el-drawer__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

/* 抽屉占位内容 */
.drawer-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 40px 20px;
}

.placeholder-content {
  text-align: center;
  max-width: 500px;
  background: var(--bg-secondary);
  padding: 40px;
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-color);
}

.placeholder-content h3 {
  margin: 16px 0 12px 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
}

.placeholder-content p {
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.6;
  font-size: 16px;
}

.placeholder-features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.placeholder-features .el-tag {
  margin: 2px;
  font-size: 12px;
  border-radius: var(--radius-sm);
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
  .account-configuration-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 16px;
    padding: 24px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .platform-tabs {
    padding: 20px;
  }
  
  .modern-tabs :deep(.el-tabs__item) {
    padding: 12px 16px;
    font-size: 14px;
    margin-right: 4px;
  }
  
  .tab-label span {
    display: none;
  }
  
  .nav-buttons {
    justify-content: center;
  }
  
  .showcase-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .feature-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .card-icon {
    align-self: center;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .platform-tabs {
    padding: 16px;
  }
  
  .nav-buttons {
    flex-direction: column;
  }
  
  .nav-btn {
    width: 100%;
  }
  
  .feature-card {
    padding: 20px;
  }
}
</style>