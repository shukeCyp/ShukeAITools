<template>
  <div id="app">
    <!-- 主应用 -->
    <el-container class="app-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon size="32"><Tools /></el-icon>
            <h1>舒克AI工具集</h1>
          </div>
          <div class="header-actions">
            <el-button 
              text 
              @click="checkHealth"
              :loading="healthChecking"
              style="color: white;"
            >
              <el-icon><Connection /></el-icon>
              {{ healthStatus }}
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="200px" class="app-sidebar">
          <el-menu
            :default-active="activeMenu"
            class="sidebar-menu"
            @select="handleMenuSelect"
            :default-openeds="['jimeng', 'accounts', 'settings']"
          >
            <el-menu-item index="home">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            
            <el-menu-item index="task-manager">
              <el-icon><Monitor /></el-icon>
              <span>任务管理器</span>
            </el-menu-item>
            
            <!-- 即梦国际版 -->
            <el-sub-menu index="jimeng">
              <template #title>
                <el-icon><Picture /></el-icon>
                <span>即梦国际版</span>
              </template>
              <el-menu-item index="jimeng-text2img">
                <el-icon><EditPen /></el-icon>
                <span>文生图</span>
              </el-menu-item>
              <el-menu-item index="jimeng-img2video">
                <el-icon><VideoPlay /></el-icon>
                <span>图生视频</span>
              </el-menu-item>
              <el-menu-item index="jimeng-digital-human">
                <el-icon><Avatar /></el-icon>
                <span>数字人</span>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 账号配置 -->
            <el-sub-menu index="accounts">
              <template #title>
                <el-icon><User /></el-icon>
                <span>账号配置</span>
              </template>
              <el-menu-item index="jimeng-accounts">
                <el-icon><UserFilled /></el-icon>
                <span>即梦账号</span>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 系统设置 -->
            <el-sub-menu index="settings">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统设置</span>
              </template>
              <el-menu-item index="base-config">
                <el-icon><Tools /></el-icon>
                <span>基础配置</span>
              </el-menu-item>
            </el-sub-menu>
            
            <el-menu-item index="about">
              <el-icon><InfoFilled /></el-icon>
              <span>关于我们</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主要内容区域 -->
        <el-main class="app-main">
          <div class="content-wrapper">
            <!-- 首页 -->
            <div v-if="activeMenu === 'home'" class="page-content">
                <div class="welcome-content">
                  <div class="welcome-header">
                    <h2>欢迎使用舒克AI工具集</h2>
                    <p>基于 Vue 3 + Flask 构建的现代化 AI 工具集成平台</p>
                  </div>
                
                <!-- 支持开源区域 -->
                <div class="support-section">
                  <div class="support-header">
                    <div class="support-icon">⭐</div>
                    <h3>开源不易，支持一下吧</h3>
                    <p>您的支持就是我持续开发的动力！如果这个项目对您有帮助，请考虑支持一杯咖啡 ☕</p>
                  </div>
                  
                  <div class="qrcode-container">
                    <div class="qrcode-item" @click="showQRCode('zfb')">
                      <div class="qrcode-wrapper">
                        <img src="/zfb_qrcode.jpg" alt="支付宝收款码" class="qrcode-img" />
                        <div class="qrcode-overlay">
                          <div class="zoom-icon">🔍</div>
                          <span>点击查看</span>
                        </div>
                      </div>
                      <div class="qrcode-label">
                        <div class="payment-icon">💰</div>
                        <span>支付宝</span>
                      </div>
                    </div>
                    
                    <div class="qrcode-item" @click="showQRCode('wx')">
                      <div class="qrcode-wrapper">
                        <img src="/wx_qrcode.jpg" alt="微信收款码" class="qrcode-img" />
                        <div class="qrcode-overlay">
                          <div class="zoom-icon">🔍</div>
                          <span>点击查看</span>
                        </div>
                      </div>
                      <div class="qrcode-label">
                        <div class="payment-icon">💬</div>
                        <span>微信</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="support-footer">
                    <p>💝 感谢每一位支持者，让开源项目走得更远！</p>
                    <div class="github-link">
                      <el-button 
                        type="primary" 
                        @click="openGithub"
                        style="margin-top: 10px;"
                      >
                        ⭐ 给项目点个 Star
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 二维码预览弹窗 -->
              <el-dialog
                v-model="qrcodeDialogVisible"
                :title="qrcodeDialogTitle"
                width="400px"
                center
                :show-close="true"
              >
                <div class="qrcode-dialog-content">
                  <img :src="currentQRCode" :alt="qrcodeDialogTitle" class="dialog-qrcode" />
                  <p class="dialog-tip">{{ qrcodeDialogTip }}</p>
                </div>
              </el-dialog>
            </div>

            <!-- 即梦国际版功能页面 -->
            <div v-if="activeMenu === 'jimeng-text2img'" class="page-content">
              <JimengText2Img />
            </div>
            
            <div v-if="activeMenu === 'jimeng-img2video'" class="page-content">
              <JimengImg2Video />
            </div>
            
            <div v-if="activeMenu === 'jimeng-digital-human'" class="page-content">
              <JimengDigitalHuman />
            </div>

            <!-- 账号配置页面 -->
            <div v-if="activeMenu === 'jimeng-accounts'" class="page-content">
              <JimengAccountManager />
            </div>

            <!-- 任务管理器 -->
            <div v-if="activeMenu === 'task-manager'" class="page-content">
              <TaskManager />
            </div>

            <!-- 基础配置 -->
            <div v-if="activeMenu === 'base-config'" class="page-content">
              <BaseConfig />
            </div>

            <!-- 关于我们 -->
            <div v-if="activeMenu === 'about'" class="page-content">
                <div class="about-content">
                  <h2>关于舒克AI工具集</h2>
                <p><strong>版本:</strong> 1.0.0</p>
                <p><strong>技术栈:</strong> Vue 3 + Element Plus + Flask + SQLite + Playwright</p>
                <p><strong>开发者:</strong> 舒克AI团队</p>
                <p><strong>特色功能:</strong> 多平台AI工具集成、智能任务管理、账号统一管理</p>
                <p><strong>更新时间:</strong> {{ new Date().toLocaleDateString() }}</p>
                </div>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Tools,
  Connection,
  House,
  User,
  Picture,
  InfoFilled,
  UserFilled,
  SuccessFilled,
  WarningFilled,
  EditPen,
  VideoPlay,
  Avatar,
  Setting,
  Monitor
} from '@element-plus/icons-vue'
import AccountConfiguration from './views/AccountConfiguration.vue'
import JimengPlatform from './views/JimengPlatform.vue'
import JimengAccountManager from './components/JimengAccountManager.vue'
import JimengText2Img from './views/JimengText2Img.vue'
import BaseConfig from './views/BaseConfig.vue'
import JimengImg2Video from './views/JimengImg2Video.vue'
import JimengDigitalHuman from './views/JimengDigitalHuman.vue'
import TaskManager from './views/TaskManager.vue'
import { accountAPI } from './utils/api'

export default {
  name: 'App',
  components: {
    AccountConfiguration,
    JimengPlatform,
    JimengAccountManager,
    JimengText2Img,
    JimengImg2Video,
    JimengDigitalHuman,
    TaskManager,
    BaseConfig,
    Tools,
    Connection,
    House,
    User,
    Picture,
    InfoFilled,
    UserFilled,
    SuccessFilled,
    WarningFilled,
    EditPen,
    VideoPlay,
    Avatar,
    Setting,
    Monitor
  },
  setup() {
    const activeMenu = ref('home')
    const healthStatus = ref('检查中...')
    const healthChecking = ref(false)
    
    // 二维码弹窗相关
    const qrcodeDialogVisible = ref(false)
    const qrcodeDialogTitle = ref('')
    const qrcodeDialogTip = ref('')
    const currentQRCode = ref('')

    // 切换菜单
    const handleMenuSelect = (index) => {
      activeMenu.value = index
    }

    // 健康检查
    const checkHealth = async () => {
      healthChecking.value = true
      try {
        const response = await accountAPI.healthCheck()
        if (response.data.success) {
          healthStatus.value = '服务正常'
          ElMessage.success('后端服务连接正常')
        } else {
          healthStatus.value = '服务异常'
        }
      } catch (error) {
        console.error('健康检查失败:', error)
        healthStatus.value = '连接失败'
        ElMessage.error('无法连接到后端服务，请确保服务已启动')
      } finally {
        healthChecking.value = false
      }
    }

    // 初始化
    // 显示二维码
    const showQRCode = (type) => {
      if (type === 'zfb') {
        qrcodeDialogTitle.value = '支付宝收款码'
        qrcodeDialogTip.value = '打开支付宝扫一扫，支持开源项目'
        currentQRCode.value = '/zfb_qrcode.jpg'
      } else if (type === 'wx') {
        qrcodeDialogTitle.value = '微信收款码'
        qrcodeDialogTip.value = '打开微信扫一扫，支持开源项目'
        currentQRCode.value = '/wx_qrcode.jpg'
      }
      qrcodeDialogVisible.value = true
    }
    
    // 打开GitHub
    const openGithub = () => {
      window.open('https://github.com/your-username/ShukeAITools', '_blank')
      ElMessage.info('感谢您的支持！⭐')
    }
    
    onMounted(() => {
      checkHealth()
    })

    return {
      activeMenu,
      healthStatus,
      healthChecking,
      qrcodeDialogVisible,
      qrcodeDialogTitle,
      qrcodeDialogTip,
      currentQRCode,
      handleMenuSelect,
      checkHealth,
      showQRCode,
      openGithub
    }
  }
}
</script>

<style>
/* 全局样式变量 */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  --text-primary: #1a202c;
  --text-secondary: #718096;
  --text-muted: #a0aec0;
  --border-color: #e2e8f0;
  --border-light: #f1f5f9;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.12);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  height: 100vh;
  background: var(--bg-gradient);
  color: var(--text-primary);
}

.app-container {
  height: 100vh;
  background: var(--bg-gradient);
}

/* 顶部导航栏样式 */
.app-header {
  background: var(--bg-primary);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-light);
  color: var(--text-primary);
  padding: 0;
  box-shadow: var(--shadow-md);
  position: relative;
  z-index: 1000;
}

.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--primary-gradient);
  opacity: 0.1;
  z-index: -1;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 32px;
  backdrop-filter: blur(10px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
  font-weight: 700;
}

.logo .el-icon {
  background: var(--primary-gradient);
  color: white;
  padding: 8px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.logo h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
}

.header-actions .el-button {
  border-radius: var(--radius-md);
  font-weight: 500;
  padding: 12px 20px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  color: var(--text-primary) !important;
  transition: var(--transition);
}

.header-actions .el-button:hover {
  background: rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* 侧边栏样式 */
.app-sidebar {
  background: var(--bg-primary);
  border-right: 1px solid var(--border-light);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(20px);
  position: relative;
}

.app-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--secondary-gradient);
  opacity: 0.03;
  z-index: -1;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
  background: transparent;
  padding: 16px 0;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 16px;
  border-radius: var(--radius-md);
  font-weight: 500;
  color: var(--text-secondary);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.sidebar-menu .el-menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--primary-gradient);
  transition: var(--transition);
  opacity: 0.1;
  z-index: -1;
}

.sidebar-menu .el-menu-item:hover::before {
  left: 0;
}

.sidebar-menu .el-menu-item:hover {
  background-color: rgba(102, 126, 234, 0.08);
  color: var(--text-primary);
  transform: translateX(4px);
}

.sidebar-menu .el-sub-menu__title {
  height: 48px;
  line-height: 48px;
  font-weight: 600;
  margin: 4px 16px;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  transition: var(--transition);
}

.sidebar-menu .el-sub-menu__title:hover {
  background-color: rgba(102, 126, 234, 0.05);
  transform: translateX(2px);
}

.sidebar-menu .el-menu-item.is-active {
  background: var(--primary-gradient);
  color: white;
  border-right: none;
  box-shadow: var(--shadow-sm);
  transform: translateX(2px);
}

.sidebar-menu .el-menu-item.is-active::before {
  left: 0;
  opacity: 0.2;
}

.sidebar-menu .el-sub-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  padding-left: 60px !important;
  font-size: 14px;
  margin: 2px 16px;
  font-weight: 400;
}

.sidebar-menu .el-sub-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
  color: white;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
}

/* 主内容区域样式 */
.app-main {
  background: transparent;
  padding: 0;
  overflow-y: auto;
  position: relative;
  min-height: calc(100vh - 64px);
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
}

.page-content {
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 首页样式 */
.welcome-content {
  padding: 0;
}

.welcome-header {
  text-align: center;
  padding: 60px 40px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  margin-bottom: 0;
}

.welcome-header::before {
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

.welcome-header h2 {
  color: var(--text-primary);
  margin-bottom: 20px;
  font-size: 36px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-header p {
  color: var(--text-secondary);
  font-size: 18px;
  margin-bottom: 0;
  font-weight: 400;
  line-height: 1.6;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  margin-top: 40px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.feature-item::before {
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

.feature-item:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(102, 126, 234, 0.3);
}

.feature-item:hover::before {
  left: 0;
}

.feature-item .el-icon {
  font-size: 32px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: rgba(102, 126, 234, 0.1);
  transition: var(--transition);
}

.feature-item:hover .el-icon {
  background: var(--primary-gradient);
  color: white;
  transform: scale(1.1);
}

.feature-item span {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
  transition: var(--transition);
}

.feature-item small {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.4;
  margin-top: 4px;
}

/* 关于我们样式 */
.about-content {
  padding: 60px 40px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.about-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--secondary-gradient);
  opacity: 0.03;
  z-index: -1;
}

.about-content h2 {
  color: var(--text-primary);
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.about-content p {
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.8;
  font-size: 16px;
  font-weight: 400;
}

/* 支持开源区域样式 */
.support-section {
  max-width: 800px;
  margin: 60px auto 0;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 2px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.support-section::before {
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

.support-section:hover::before {
  left: 0;
}

.support-header {
  text-align: center;
  margin-bottom: 40px;
}

.support-icon {
  font-size: 48px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
  display: inline-block;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.support-header h3 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 15px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.support-header p {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 500px;
  margin: 0 auto;
}

.qrcode-container {
  display: flex;
  justify-content: center;
  gap: 60px;
  margin: 40px 0;
}

.qrcode-item {
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
}

.qrcode-item:hover {
  transform: translateY(-5px);
}

.qrcode-wrapper {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 15px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: var(--transition);
}

.qrcode-wrapper:hover {
  box-shadow: var(--shadow-lg);
}

.qrcode-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: var(--transition);
}

.qrcode-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: var(--transition);
  gap: 8px;
}

.qrcode-wrapper:hover .qrcode-overlay {
  opacity: 1;
}

.qrcode-overlay span {
  font-size: 14px;
  font-weight: 500;
}

.qrcode-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.payment-icon {
  font-size: 20px;
  display: inline-block;
}

.zoom-icon {
  font-size: 24px;
  display: inline-block;
}

.support-footer {
  text-align: center;
  padding-top: 30px;
  border-top: 2px dashed var(--border-color);
}

.support-footer p {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.github-link .el-button {
  background: var(--primary-gradient);
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 25px;
  transition: var(--transition);
}

.github-link .el-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 弹窗样式 */
.qrcode-dialog-content {
  text-align: center;
  padding: 20px;
}

.dialog-qrcode {
  width: 280px;
  height: 280px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  margin-bottom: 20px;
}

.dialog-tip {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
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

/* 滚动条样式 */
.app-main::-webkit-scrollbar {
  width: 8px;
}

.app-main::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.app-main::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 4px;
  transition: var(--transition);
}

.app-main::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-wrapper {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .app-sidebar {
    width: 180px !important;
  }
  
  .header-content {
    padding: 0 20px;
  }
  
  .logo h1 {
    font-size: 24px;
  }
  
  .app-main {
    padding: 16px;
  }
  
  .welcome-header {
    padding: 40px 24px;
  }
  
  .welcome-header h2 {
    font-size: 28px;
  }
  
  .about-content {
    padding: 40px 24px;
  }
  
  .feature-list {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .support-section {
    margin: 40px 20px 0;
    padding: 30px 20px;
  }
  
  .qrcode-container {
    flex-direction: column;
    gap: 30px;
    align-items: center;
  }
  
  .support-header h3 {
    font-size: 24px;
  }
  
  .qrcode-wrapper {
    width: 140px;
    height: 140px;
  }
}

@media (max-width: 480px) {
  .app-sidebar {
    width: 160px !important;
  }
  
  .header-content {
    padding: 0 16px;
  }
  
  .logo h1 {
    font-size: 20px;
  }
  
  .welcome-header h2 {
    font-size: 24px;
  }
  
  .feature-item {
    padding: 24px 16px;
  }
}
</style>