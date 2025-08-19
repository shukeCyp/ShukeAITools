<template>
  <div class="jimeng-img2video-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="32"><VideoCamera /></el-icon>
          </div>
          <h1 class="page-title">图生视频</h1>
        </div>
        <div class="status-section">
          <el-tag 
            type="warning" 
            size="large"
            class="status-tag"
          >
            <el-icon class="status-icon"><Tools /></el-icon>
            开发中
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stats-content">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total }}</span>
              <span class="stat-label">总任务</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon warning">
              <el-icon size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.queued }}</span>
              <span class="stat-label">排队中</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon primary">
              <el-icon size="24"><Loading /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.processing }}</span>
              <span class="stat-label">生成中</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon success">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.completed }}</span>
              <span class="stat-label">已完成</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon danger">
              <el-icon size="24"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.failed }}</span>
              <span class="stat-label">失败</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 开发状态展示 -->
    <div class="development-status">
      <div class="status-content">
        <div class="status-header">
          <div class="status-icon-large">
            <el-icon size="64"><VideoCamera /></el-icon>
          </div>
          <h2 class="status-title">图生视频功能开发中</h2>
          <p class="status-desc">将静态图像转换为动态视频，支持多种动画效果和参数调节</p>
        </div>
        
        <div class="feature-preview">
          <div class="preview-grid">
            <div class="preview-card" v-for="feature in previewFeatures" :key="feature.id">
              <div class="preview-icon">
                <el-icon size="32">
                  <component :is="feature.icon" />
                </el-icon>
              </div>
              <div class="preview-content">
                <h4 class="preview-title">{{ feature.title }}</h4>
                <p class="preview-desc">{{ feature.description }}</p>
                <div class="preview-tags">
                  <el-tag 
                    v-for="tag in feature.tags" 
                    :key="tag" 
                    size="small" 
                    type="warning"
                    class="preview-tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="development-progress">
          <div class="progress-header">
            <h3 class="progress-title">开发进度</h3>
            <span class="progress-percent">35%</span>
          </div>
          <el-progress 
            :percentage="35" 
            color="#e6a23c" 
            :stroke-width="8"
            class="progress-bar"
          />
          <div class="progress-milestones">
            <div class="milestone completed">
              <el-icon><Check /></el-icon>
              <span>需求分析</span>
            </div>
            <div class="milestone completed">
              <el-icon><Check /></el-icon>
              <span>界面设计</span>
            </div>
            <div class="milestone active">
              <el-icon><Loading /></el-icon>
              <span>核心功能开发</span>
            </div>
            <div class="milestone pending">
              <el-icon><Clock /></el-icon>
              <span>测试优化</span>
            </div>
            <div class="milestone pending">
              <el-icon><Clock /></el-icon>
              <span>正式发布</span>
            </div>
          </div>
        </div>

        <div class="coming-soon">
          <el-alert
            title="即将上线"
            type="warning"
            :closable="false"
            show-icon
            class="coming-alert"
          >
            <template #default>
              <p>图生视频功能正在紧张开发中，预计将在下个版本中与大家见面。敬请期待！</p>
              <div class="alert-features">
                <span>✨ 多种动画效果</span>
                <span>⚡ 快速生成</span>
                <span>🎨 参数自定义</span>
                <span>📱 移动端支持</span>
              </div>
            </template>
          </el-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { 
  VideoCamera,
  Tools,
  Document,
  Clock,
  Loading,
  CircleCheck,
  CircleClose,
  Check,
  Magic,
  Setting,
  Timer,
  Picture
} from '@element-plus/icons-vue'

export default {
  name: 'JimengImg2Video',
  components: {
    VideoCamera,
    Tools,
    Document,
    Clock,
    Loading,
    CircleCheck,
    CircleClose,
    Check,
    Magic,
    Setting,
    Timer,
    Picture
  },
  setup() {
    // 统计数据
    const stats = reactive({
      total: 0,
      queued: 0,
      processing: 0,
      completed: 0,
      failed: 0
    })

    // 预览功能
    const previewFeatures = ref([
      {
        id: 1,
        title: '智能动画',
        description: '基于AI的智能动画生成，让静态图像栩栩如生',
        icon: 'Magic',
        tags: ['AI驱动', '智能', '自动']
      },
      {
        id: 2,
        title: '参数调节',
        description: '丰富的参数设置，精确控制动画效果和质量',
        icon: 'Setting',
        tags: ['自定义', '精确', '专业']
      },
      {
        id: 3,
        title: '快速处理',
        description: '优化的处理算法，快速生成高质量动态视频',
        icon: 'Timer',
        tags: ['高效', '快速', '稳定']
      },
      {
        id: 4,
        title: '多格式支持',
        description: '支持多种图片输入格式和视频输出格式',
        icon: 'Picture',
        tags: ['兼容', '多格式', '灵活']
      }
    ])

    // 加载数据
    const loadStats = () => {
      // 模拟数据
      stats.total = 0
      stats.queued = 0
      stats.processing = 0
      stats.completed = 0
      stats.failed = 0
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats,
      previewFeatures
    }
  }
}
</script>

<style scoped>
.jimeng-img2video-page {
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
  background: var(--warning-gradient);
  opacity: 0.03;
  z-index: -1;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  background: var(--warning-gradient);
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
  background: var(--warning-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-section {
  display: flex;
  align-items: center;
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

/* 统计概览 */
.stats-overview {
  max-width: 1200px;
  margin: 0 auto 32px auto;
}

.stats-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.stats-content::before {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
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

.stat-icon.warning {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.stat-icon.primary {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stat-icon.success {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stat-icon.danger {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.stat-info {
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

/* 开发状态 */
.development-status {
  max-width: 1200px;
  margin: 0 auto;
}

.status-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: 40px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.status-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--warning-gradient);
  opacity: 0.02;
  z-index: -1;
}

.status-header {
  text-align: center;
  margin-bottom: 40px;
}

.status-icon-large {
  background: var(--warning-gradient);
  color: white;
  width: 120px;
  height: 120px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px auto;
  box-shadow: var(--shadow-lg);
}

.status-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  background: var(--warning-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.status-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* 功能预览 */
.feature-preview {
  margin-bottom: 40px;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.preview-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.preview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: var(--warning-gradient);
  transition: var(--transition);
  opacity: 0.05;
  z-index: -1;
}

.preview-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(230, 162, 60, 0.3);
}

.preview-card:hover::before {
  left: 0;
}

.preview-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: var(--transition);
}

.preview-card:hover .preview-icon {
  background: var(--warning-gradient);
  color: white;
  transform: scale(1.1);
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.preview-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

/* 开发进度 */
.development-progress {
  margin-bottom: 32px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.progress-percent {
  font-size: 18px;
  font-weight: 700;
  color: #e6a23c;
}

.progress-bar {
  margin-bottom: 24px;
}

.progress-milestones {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.milestone {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 100px;
}

.milestone .el-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.milestone.completed .el-icon {
  background: #67c23a;
  color: white;
}

.milestone.active .el-icon {
  background: #e6a23c;
  color: white;
}

.milestone.pending .el-icon {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.milestone span {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
  font-weight: 500;
}

/* 即将上线 */
.coming-soon {
  text-align: center;
}

.coming-alert {
  border-radius: var(--radius-lg);
  padding: 24px;
}

.coming-alert .el-alert__content {
  text-align: left;
}

.alert-features {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  justify-content: center;
}

.alert-features span {
  font-size: 14px;
  color: #e6a23c;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .jimeng-img2video-page {
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
  
  .preview-grid {
    grid-template-columns: 1fr;
  }
  
  .status-content {
    padding: 24px;
  }
  
  .status-title {
    font-size: 28px;
  }
  
  .progress-milestones {
    justify-content: center;
  }
  
  .milestone {
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .status-title {
    font-size: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .alert-features {
    flex-direction: column;
    gap: 8px;
  }
}
</style>