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
            
            <el-menu-item index="prompt-manager">
              <el-icon><Collection /></el-icon>
              <span>提示词</span>
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
            
            <!-- 清影平台 -->
            <el-sub-menu index="qingying">
              <template #title>
                <el-icon><VideoCamera /></el-icon>
                <span>智谱清影</span>
              </template>
              <el-menu-item index="qingying-img2video">
                <el-icon><VideoPlay /></el-icon>
                <span>图生视频</span>
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
              <el-menu-item index="qingying-accounts">
                <el-icon><UserFilled /></el-icon>
                <span>清影账号</span>
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
                
                <!-- 定制化服务区域 -->
                <div class="services-section">
                  <div class="services-header">
                    <div class="services-icon">🚀</div>
                    <h3>舒克专业定制服务</h3>
                    <p>专业的AI工具定制开发，为您量身打造专属解决方案 🎯</p>
                  </div>
                  
                  <div class="services-container">
                    <div class="service-item">
                      <div class="service-icon">⚙️</div>
                      <h4>定制化脚本</h4>
                      <p>根据您的需求开发专属自动化脚本</p>
                      <ul>
                        <li>数据处理自动化</li>
                        <li>业务流程脚本</li>
                        <li>爬虫与数据采集</li>
                        <li>系统集成方案</li>
                      </ul>
                    </div>
                    
                    <div class="service-item">
                      <div class="service-icon">🎨</div>
                      <h4>ComfyUI工作流</h4>
                      <p>专业的ComfyUI节点开发与工作流定制</p>
                      <ul>
                        <li>自定义节点开发</li>
                        <li>复杂工作流设计</li>
                        <li>模型整合优化</li>
                        <li>批量处理方案</li>
                      </ul>
                    </div>
                    
                    <div class="service-item">
                      <div class="service-icon">🔗</div>
                      <h4>扣子工作流</h4>
                      <p>扣子平台工作流开发与部署服务</p>
                      <ul>
                        <li>智能对话流程</li>
                        <li>知识库集成</li>
                        <li>API接口开发</li>
                        <li>多平台部署</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div class="services-footer">
                    <div class="brand-highlight">
                      <div class="brand-logo">🏆</div>
                      <h4>认准舒克</h4>
                      <p>专业 · 高效 · 可靠</p>
                    </div>
                    <div class="contact-info">
                      <p>💬 需要定制服务？联系我们获取专业方案</p>
                      <el-button 
                        type="primary" 
                        size="large"
                        @click="contactUs"
                        style="margin-top: 15px;"
                      >
                        📞 立即咨询
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
              

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

            <!-- 清影平台功能页面 -->
            <div v-if="activeMenu === 'qingying-img2video'" class="page-content">
              <QingyingImg2Video />
            </div>

            <!-- 账号配置页面 -->
            <div v-if="activeMenu === 'jimeng-accounts'" class="page-content">
              <JimengAccountManager />
            </div>

            <div v-if="activeMenu === 'qingying-accounts'" class="page-content">
              <QingyingAccountManager />
            </div>

            <!-- 任务管理器 -->
            <div v-if="activeMenu === 'task-manager'" class="page-content">
              <TaskManager />
            </div>

            <!-- 提示词管理 -->
            <div v-if="activeMenu === 'prompt-manager'" class="page-content">
              <PromptManager />
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

    <!-- 联系我们对话框 -->
    <el-dialog 
      v-model="contactDialogVisible" 
      title="联系我们" 
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="contact-content">
        <div class="contact-simple">
          <div class="wechat-info">
            <div class="contact-item">
              <el-icon class="contact-icon" color="#67C23A">
                <ChatDotRound />
              </el-icon>
              <div class="contact-text">
                <div class="contact-label">微信号</div>
                <div class="contact-value">zhaxinyu--</div>
              </div>
            </div>
          </div>
          
          <div class="qrcode-section">
            <div class="qrcode-container">
              <img src="./assets/vx.png" alt="微信二维码" class="qrcode-image" />
              <p class="qrcode-text">扫码添加微信好友</p>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="contact-footer">
          <el-button @click="contactDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="copyContactInfo">复制微信号</el-button>
        </div>
      </template>
    </el-dialog>
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
  Monitor,
  Collection,
  VideoCamera,
  Message,
  Star
} from '@element-plus/icons-vue'
import AccountConfiguration from './views/AccountConfiguration.vue'
import JimengPlatform from './views/JimengPlatform.vue'
import JimengAccountManager from './components/JimengAccountManager.vue'
import QingyingAccountManager from './components/QingyingAccountManager.vue'
import JimengText2Img from './views/JimengText2Img.vue'
import BaseConfig from './views/BaseConfig.vue'
import JimengImg2Video from './views/JimengImg2Video.vue'
import JimengDigitalHuman from './views/JimengDigitalHuman.vue'
import QingyingImg2Video from './views/QingyingImg2Video.vue'
import TaskManager from './views/TaskManager.vue'
import PromptManager from './views/PromptManager.vue'
import { accountAPI } from './utils/api'

export default {
  name: 'App',
  components: {
    AccountConfiguration,
    JimengPlatform,
    JimengAccountManager,
    QingyingAccountManager,
    JimengText2Img,
    JimengImg2Video,
    JimengDigitalHuman,
    QingyingImg2Video,
    TaskManager,
    PromptManager,
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
    Monitor,
    Collection,
    VideoCamera
  },
  setup() {
    const activeMenu = ref('home')
    const healthStatus = ref('检查中...')
    const healthChecking = ref(false)
    const contactDialogVisible = ref(false)

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

    // 联系我们
    const contactUs = () => {
      contactDialogVisible.value = true
    }

    // 复制联系信息
    const copyContactInfo = () => {
      const contactInfo = `微信号：zhaxinyu--`
      
      navigator.clipboard.writeText(contactInfo).then(() => {
        ElMessage.success('微信号已复制到剪贴板')
        contactDialogVisible.value = false
      }).catch(() => {
        ElMessage.error('复制失败，请手动复制')
      })
    }
    
    onMounted(() => {
      checkHealth()
    })

    return {
      activeMenu,
      healthStatus,
      healthChecking,
      contactDialogVisible,
      handleMenuSelect,
      checkHealth,
      contactUs,
      copyContactInfo
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
  min-height: 100vh;
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
  height: calc(100vh - 64px);
  max-height: calc(100vh - 64px);
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

/* 定制化服务区域样式 */
.services-section {
  max-width: 1200px;
  margin: 60px auto 0;
  padding: 40px;
  background: var(--bg-secondary);
  border-radius: 20px;
  border: 2px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.services-section::before {
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

.services-section:hover::before {
  left: 0;
}

.services-header {
  text-align: center;
  margin-bottom: 40px;
}

.services-icon {
  font-size: 48px;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
  display: inline-block;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.services-header h3 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 15px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.services-header p {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 500px;
  margin: 0 auto;
}

.services-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  margin: 40px 0;
}

.service-item {
  background: var(--bg-primary);
  padding: 30px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.service-item::before {
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

.service-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(102, 126, 234, 0.3);
}

.service-item:hover::before {
  left: 0;
}

.service-icon {
  font-size: 36px;
  margin-bottom: 16px;
  display: inline-block;
}

.service-item h4 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.service-item p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}

.service-item ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.service-item li {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
}

.service-item li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #4ecdc4;
  font-weight: 600;
}

.services-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 30px;
  border-top: 2px dashed var(--border-color);
  gap: 40px;
}

.brand-highlight {
  text-align: center;
  flex: 1;
}

.brand-logo {
  font-size: 36px;
  margin-bottom: 12px;
  display: inline-block;
}

.brand-highlight h4 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-highlight p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.contact-info {
  text-align: center;
  flex: 1;
}

.contact-info p {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 0;
}

.contact-info .el-button {
  background: var(--primary-gradient);
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 25px;
  transition: var(--transition);
}

.contact-info .el-button:hover {
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
  
  .services-section {
    margin: 40px 20px 0;
    padding: 30px 20px;
  }
  
  .services-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .services-header h3 {
    font-size: 24px;
  }
  
  .services-footer {
    flex-direction: column;
    gap: 30px;
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

/* 联系我们对话框样式 */
.contact-content {
  padding: 20px 0;
}

.contact-simple {
  display: flex;
  gap: 40px;
  align-items: center;
  justify-content: center;
}

.wechat-info {
  flex: 1;
  max-width: 300px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.contact-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.contact-text {
  flex: 1;
}

.contact-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
  font-weight: 500;
}

.contact-value {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.qrcode-section {
  flex-shrink: 0;
  text-align: center;
}

.qrcode-section h3 {
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.qrcode-container {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.qrcode-image {
  width: 160px;
  height: 160px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
}

.qrcode-text {
  color: #606266;
  font-size: 14px;
  margin: 0;
  font-weight: 500;
}

/* 联系弹窗响应式设计 */
@media (max-width: 768px) {
  .contact-simple {
    flex-direction: column;
    gap: 30px;
    text-align: center;
  }
  
  .wechat-info {
    max-width: 100%;
  }
  
  .qrcode-image {
    width: 140px;
    height: 140px;
  }
}

@media (max-width: 480px) {
  .contact-item {
    padding: 16px;
  }
  
  .contact-icon {
    font-size: 24px;
  }
  
  .contact-value {
    font-size: 16px;
  }
  
  .qrcode-image {
    width: 120px;
    height: 120px;
  }
}

.contact-item:last-child {
  margin-bottom: 0;
}

.contact-item strong {
  color: #303133;
  min-width: 60px;
  display: inline-block;
}

.contact-footer {
  text-align: right;
}

.contact-footer .el-button {
  margin-left: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .contact-layout {
    flex-direction: column;
    gap: 20px;
  }
  
  .qrcode-section {
    width: 100%;
  }
  
  .qrcode-image {
    width: 140px;
    height: 140px;
  }
}
</style>