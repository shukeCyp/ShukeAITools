<template>
  <div class="jimeng-digital-human-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">数字人工作台</h1>
          <p class="page-subtitle">AI驱动的虚拟数字人生成，支持表情、动作和语音合成</p>
        </div>
        <div class="status-section">
          <el-tag size="large" type="warning" class="status-tag">
            <el-icon class="status-icon"><Tools /></el-icon>
            开发中
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 功能展示 -->
    <div class="content-section">
      <div class="feature-showcase">
        <div class="showcase-header">
          <div class="feature-icon">
            <el-icon size="48"><Avatar /></el-icon>
          </div>
          <div class="feature-info">
            <h2>AI数字人创建工作台</h2>
            <p>打造专属的AI虚拟数字人，支持智能表情、动作捕捉和语音合成</p>
          </div>
        </div>

        <!-- 功能特性网格 -->
        <div class="features-grid">
          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><User /></el-icon>
            </div>
            <div class="card-content">
              <h3>智能形象定制</h3>
              <p>基于AI算法生成个性化数字人形象，支持多种风格和特征调整</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><VideoPlay /></el-icon>
            </div>
            <div class="card-content">
              <h3>表情实时控制</h3>
              <p>实时面部表情捕捉和控制，让数字人拥有丰富的情感表达</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><Connection /></el-icon>
            </div>
            <div class="card-content">
              <h3>动作捕捉驱动</h3>
              <p>支持全身动作捕捉，让数字人拥有自然流畅的肢体动作</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><Microphone /></el-icon>
            </div>
            <div class="card-content">
              <h3>语音智能合成</h3>
              <p>AI语音合成技术，支持多种音色和语言，让数字人开口说话</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><Picture /></el-icon>
            </div>
            <div class="card-content">
              <h3>场景自由搭建</h3>
              <p>丰富的3D场景库，支持自定义环境和背景，打造专属舞台</p>
            </div>
          </div>

          <div class="feature-card">
            <div class="card-icon">
              <el-icon size="32"><ChatDotRound /></el-icon>
            </div>
            <div class="card-content">
              <h3>交互式对话</h3>
              <p>集成智能对话系统，支持自然语言交互和情感理解</p>
            </div>
          </div>
        </div>

        <!-- 开发状态 -->
        <div class="development-status">
          <div class="status-content">
            <el-icon size="64" class="status-icon-large"><Tools /></el-icon>
            <h3>功能开发中</h3>
            <p>我们正在全力开发这些强大的数字人功能，敬请期待！</p>
            <div class="progress-info">
              <el-progress :percentage="35" :stroke-width="8" class="dev-progress" />
              <p class="progress-text">预计完成度：35%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  Avatar, 
  User, 
  Tools,
  VideoPlay,
  Connection,
  Microphone,
  Picture,
  ChatDotRound
} from '@element-plus/icons-vue'

export default {
  name: 'JimengDigitalHuman',
  components: {
    Avatar,
    User,
    Tools,
    VideoPlay,
    Connection,
    Microphone,
    Picture,
    ChatDotRound
  }
}
</script>

<style scoped>
.jimeng-digital-human-page {
  padding: 16px 24px;
  min-height: calc(100vh - 64px);
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px;
}

.header-content {
  background: var(--bg-primary);
  padding: 32px;
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

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  background: var(--warning-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
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

/* 内容区域 */
.content-section {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-showcase {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 40px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-showcase::before {
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

/* 展示头部 */
.showcase-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 40px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light);
}

.feature-icon {
  background: var(--warning-gradient);
  color: white;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
}

.feature-info h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.feature-info p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* 功能网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  padding: 24px;
  border: 1px solid var(--border-light);
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
  background: var(--warning-gradient);
  transition: var(--transition);
  opacity: 0.05;
  z-index: -1;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(240, 147, 251, 0.3);
}

.feature-card:hover::before {
  left: 0;
}

.card-icon {
  background: rgba(240, 147, 251, 0.1);
  color: #f093fb;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: var(--transition);
}

.feature-card:hover .card-icon {
  background: var(--warning-gradient);
  color: white;
  transform: scale(1.1);
}

.card-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.card-content p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* 开发状态 */
.development-status {
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  padding: 32px;
  text-align: center;
  border: 2px dashed var(--border-color);
}

.status-content {
  max-width: 400px;
  margin: 0 auto;
}

.status-icon-large {
  color: #e6a23c;
  margin-bottom: 16px;
}

.development-status h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.development-status p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.progress-info {
  margin-top: 20px;
}

.dev-progress {
  margin-bottom: 12px;
}

.progress-text {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
  font-weight: 500;
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
  .jimeng-digital-human-page {
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
  
  .feature-showcase {
    padding: 24px;
  }
  
  .showcase-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .feature-card {
    padding: 20px;
  }
  
  .development-status {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .feature-showcase {
    padding: 20px;
  }
  
  .feature-card {
    padding: 16px;
  }
  
  .card-icon {
    width: 56px;
    height: 56px;
  }
}
</style>