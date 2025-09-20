<template>
  <div class="jimeng-page jimeng-platform-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><Picture /></el-icon>
          </div>
          <div class="title-content">
            <h1 class="page-title">即梦国际版</h1>
            <p class="page-subtitle">AI图像生成和视频制作平台</p>
          </div>
        </div>
        <div class="status-section">
          <el-button 
            :icon="User"
            @click="showAccountManager = true"
            class="btn-account action-btn"
            size="large"
          >
            <el-icon><User /></el-icon>
            账号管理 ({{ accountCount }})
          </el-button>
        </div>
      </div>
    </div>

    <!-- 功能导航 -->
    <div class="function-navigation">
      <div class="nav-content">
        <div class="nav-grid">
          <div
            v-for="func in functions"
            :key="func.key"
            :class="['nav-card', { 'active': activeFunction === func.key }]"
            @click="openFunction(func.key)"
          >
            <div class="card-icon">
              <el-icon size="28">
                <component :is="func.icon" />
              </el-icon>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ func.title }}</h3>
              <p class="card-desc">{{ func.description }}</p>
            </div>
            <div class="card-status">
              <el-tag 
                v-if="func.status === 'developing'"
                type="warning" 
                size="small"
                class="status-tag"
              >
                开发中
              </el-tag>
              <el-tag 
                v-else-if="func.status === 'available'"
                type="success" 
                size="small"
                class="status-tag"
              >
                可用
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能预览 -->
    <div class="feature-showcase">
      <div class="showcase-content">
        <div class="showcase-header">
          <h2 class="showcase-title">平台功能</h2>
        </div>
        <div class="showcase-grid">
          <div class="feature-card" v-for="feature in platformFeatures" :key="feature.id">
            <div class="feature-icon">
              <el-icon size="32">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <div class="feature-content">
              <h4 class="feature-title">{{ feature.title }}</h4>
              <p class="feature-desc">{{ feature.description }}</p>
              <div class="feature-tags">
                <el-tag 
                  v-for="tag in feature.tags" 
                  :key="tag" 
                  size="small" 
                  class="feature-tag"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 账号管理抽屉 -->
    <el-drawer
      v-model="showAccountManager"
      title="即梦账号管理"
      size="80%"
      direction="rtl"
    >
      <JimengAccountManager />
    </el-drawer>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Picture, 
  User, 
  Edit, 
  VideoCamera, 
  Avatar,
  Cpu,
  DataBoard,
  Star,
  TrendCharts,
  Connection
} from '@element-plus/icons-vue'
import JimengAccountManager from '../components/JimengAccountManager.vue'
import { accountAPI } from '../utils/api'

export default {
  name: 'JimengPlatform',
  components: {
    JimengAccountManager,
    Picture,
    User,
    Edit,
    VideoCamera,
    Avatar,
    Cpu,
    DataBoard,
    Star,
    TrendCharts,
    Connection
  },
  setup() {
    const showAccountManager = ref(false)
    const activeFunction = ref('text2img')
    const accountCount = ref(0)

    // 功能列表
    const functions = ref([
      {
        key: 'text2img',
        title: '文生图',
        description: 'AI文本生成图像，创意无限',
        icon: 'Edit',
        status: 'available'
      },
      {
        key: 'img2video',
        title: '图生视频',
        description: '静态图像转动态视频',
        icon: 'VideoCamera',
        status: 'developing'
      },
      {
        key: 'digital-human',
        title: '数字人',
        description: 'AI虚拟人物生成',
        icon: 'Avatar',
        status: 'developing'
      }
    ])

    // 平台功能特色
    const platformFeatures = ref([
      {
        id: 1,
        title: 'AI智能创作',
        description: '基于先进的AI模型，提供高质量的内容创作服务',
        icon: 'Cpu',
        tags: ['智能', 'AI', '创作']
      },
      {
        id: 2,
        title: '多样化输出',
        description: '支持多种风格和尺寸的内容生成，满足不同需求',
        icon: 'DataBoard',
        tags: ['多样化', '灵活', '定制']
      },
      {
        id: 3,
        title: '高效处理',
        description: '优化的处理流程，快速生成高质量内容',
        icon: 'TrendCharts',
        tags: ['高效', '快速', '质量']
      },
      {
        id: 4,
        title: '无缝集成',
        description: '完整的API接口，轻松集成到现有工作流程',
        icon: 'Connection',
        tags: ['集成', 'API', '便捷']
      }
    ])

    // 加载账号数量
    const loadAccountCount = async () => {
      try {
        const response = await accountAPI.getJimengAccounts({ page: 1, pageSize: 1 })
        if (response.data.success) {
          accountCount.value = response.data.data.total || 0
        }
      } catch (error) {
        console.error('加载账号数量失败:', error)
      }
    }

    // 打开功能
    const openFunction = (functionKey) => {
      activeFunction.value = functionKey
      
      switch (functionKey) {
        case 'text2img':
          // 跳转到文生图页面
          window.location.hash = '#/jimeng-text2img'
          break
        case 'img2video':
          ElMessage.info('图生视频功能开发中，敬请期待')
          break
        case 'digital-human':
          ElMessage.info('数字人功能开发中，敬请期待')
          break
        default:
          ElMessage.warning('未知功能')
      }
    }

    onMounted(() => {
      loadAccountCount()
    })

    return {
      showAccountManager,
      activeFunction,
      accountCount,
      functions,
      platformFeatures,
      openFunction
    }
  }
}
</script>

<style scoped>
@import '../styles/jimeng-common.css';

/* 即梦平台页面特定样式 */
.title-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 按钮样式已移至全局样式 */

/* 功能导航 */
.function-navigation {
  max-width: 1200px;
  margin: 0 auto 32px auto;
}

.nav-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.nav-content::before {
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

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.nav-card {
  background: var(--bg-secondary);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nav-card::before {
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

.nav-card:hover {
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.nav-card:hover::before {
  left: 0;
}

.nav-card.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  box-shadow: var(--shadow-md);
}

.nav-card.active::before {
  left: 0;
  opacity: 0.1;
}

.card-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.nav-card:hover .card-icon,
.nav-card.active .card-icon {
  background: var(--primary-gradient);
  color: white;
  transform: scale(1.1);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.card-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.card-status {
  display: flex;
  justify-content: flex-end;
}

.status-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

/* 功能预览 */
.feature-showcase {
  max-width: 1200px;
  margin: 0 auto;
}

.showcase-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 40px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.showcase-content::before {
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

.showcase-header {
  text-align: center;
  margin-bottom: 32px;
}

.showcase-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  text-align: center;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
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
  border-color: rgba(76, 175, 80, 0.3);
}

.feature-card:hover::before {
  left: 0;
}

.feature-icon {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px auto;
  transition: var(--transition);
}

.feature-card:hover .feature-icon {
  background: var(--success-gradient);
  color: white;
  transform: scale(1.1);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.feature-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.feature-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-platform-page {
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
  
  .nav-grid {
    grid-template-columns: 1fr;
  }
  
  .showcase-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .nav-content,
  .showcase-content {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .showcase-title {
    font-size: 24px;
  }
  
  .showcase-grid {
    grid-template-columns: 1fr;
  }
}
</style>