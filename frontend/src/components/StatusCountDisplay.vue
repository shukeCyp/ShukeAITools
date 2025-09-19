<template>
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
</template>

<script>
import { 
  Document, 
  Clock, 
  Loading, 
  CircleCheckFilled, 
  CircleCloseFilled
} from '@element-plus/icons-vue'

export default {
  name: 'StatusCountDisplay',
  components: {
    Document,
    Clock,
    Loading,
    CircleCheckFilled,
    CircleCloseFilled
  },
  props: {
    stats: {
      type: Object,
      default: () => ({
        total: 0,
        queued: 0,
        processing: 0,
        completed: 0,
        failed: 0
      })
    }
  }
}
</script>

<style scoped>
.stats-overview {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
}

.stat-card.processing .stat-icon {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
}

.stat-card.completed .stat-icon {
  background: linear-gradient(135deg, #55efc4, #00b894);
}

.stat-card.failed .stat-icon {
  background: linear-gradient(135deg, #fd79a8, #e84393);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #718096;
}
</style> 