<template>
  <div class="action-button-group" :class="groupClasses">
    <!-- 刷新按钮 -->
    <ActionButton
      v-if="showRefresh"
      type="info"
      :size="size"
      :loading="refreshLoading"
      :disabled="disabled"
      tooltip="刷新"
      @click="$emit('refresh')"
    >
      <template #icon><el-icon><Refresh /></el-icon></template>
      <span v-if="!compact">刷新</span>
    </ActionButton>

    <!-- 批量删除按钮 -->
    <ActionButton
      v-if="showBatchDelete"
      type="danger"
      :size="size"
      :disabled="disabled || !hasSelection"
      tooltip="批量删除"
      @click="$emit('batch-delete')"
    >
      <template #icon><el-icon><Delete /></el-icon></template>
      <span v-if="!compact">批量删除</span>
    </ActionButton>

    <!-- 批量下载按钮 -->
    <ActionButton
      v-if="showBatchDownload"
      type="success"
      :size="size"
      :disabled="disabled || !hasSelection"
      tooltip="批量下载"
      @click="$emit('batch-download')"
    >
      <template #icon><el-icon><Download /></el-icon></template>
      <span v-if="!compact">批量下载</span>
    </ActionButton>

    <!-- 自定义操作按钮 -->
    <ActionButton
      v-for="action in customActions"
      :key="action.key"
      :type="action.type || 'secondary'"
      :size="size"
      :icon="action.icon"
      :loading="action.loading"
      :disabled="disabled || action.disabled"
      :tooltip="action.tooltip"
      @click="$emit('custom-action', action.key)"
    >
      <span v-if="!compact && action.text">{{ action.text }}</span>
    </ActionButton>

    <!-- 单项操作按钮组 -->
    <div v-if="showItemActions" class="item-actions-group">
      <!-- 预览按钮 -->
      <ActionButton
        v-if="showView"
        type="info"
        :size="size"
        :circle="compact"
        :text="itemActionsStyle === 'text'"
        :disabled="disabled"
        tooltip="预览"
        @click="$emit('view')"
      >
        <template #icon><el-icon><View /></el-icon></template>
        <span v-if="!compact">预览</span>
      </ActionButton>

      <!-- 重试按钮 -->
      <ActionButton
        v-if="showRetry"
        type="warning"
        :size="size"
        :circle="compact"
        :text="itemActionsStyle === 'text'"
        :disabled="disabled"
        tooltip="重试"
        @click="$emit('retry')"
      >
        <template #icon><el-icon><RefreshRight /></el-icon></template>
        <span v-if="!compact">重试</span>
      </ActionButton>

      <!-- 删除按钮 -->
      <ActionButton
        v-if="showDelete"
        type="danger"
        :size="size"
        :circle="compact"
        :text="itemActionsStyle === 'text'"
        :disabled="disabled"
        tooltip="删除"
        @click="$emit('delete')"
      >
        <template #icon><el-icon><Delete /></el-icon></template>
        <span v-if="!compact">删除</span>
      </ActionButton>
    </div>
  </div>
</template>

<script>
import ActionButton from './ActionButton.vue'
import { Refresh, Delete, Download, View, RefreshRight } from '@element-plus/icons-vue'

export default {
  name: 'ActionButtonGroup',
  components: {
    ActionButton,
    Refresh,
    Delete,
    Download,
    View,
    RefreshRight
  },
  props: {
    // 按钮尺寸
    size: {
      type: String,
      default: 'default',
      validator: (value) => ['small', 'default', 'large'].includes(value)
    },
    // 是否紧凑模式（只显示图标）
    compact: {
      type: Boolean,
      default: false
    },
    // 是否禁用所有按钮
    disabled: {
      type: Boolean,
      default: false
    },
    // 布局方向
    direction: {
      type: String,
      default: 'horizontal',
      validator: (value) => ['horizontal', 'vertical'].includes(value)
    },
    // 按钮间距
    gap: {
      type: String,
      default: 'default',
      validator: (value) => ['small', 'default', 'large'].includes(value)
    },
    
    // 显示控制
    showRefresh: {
      type: Boolean,
      default: false
    },
    showBatchDelete: {
      type: Boolean,
      default: false
    },
    showBatchDownload: {
      type: Boolean,
      default: false
    },
    showItemActions: {
      type: Boolean,
      default: false
    },
    showView: {
      type: Boolean,
      default: true
    },
    showRetry: {
      type: Boolean,
      default: true
    },
    showDelete: {
      type: Boolean,
      default: true
    },
    
    // 状态控制
    refreshLoading: {
      type: Boolean,
      default: false
    },
    hasSelection: {
      type: Boolean,
      default: false
    },
    
    // 单项操作样式
    itemActionsStyle: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'text'].includes(value)
    },
    
    // 自定义操作按钮
    customActions: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    groupClasses() {
      return [
        `action-button-group--${this.direction}`,
        `action-button-group--gap-${this.gap}`,
        {
          'action-button-group--compact': this.compact
        }
      ];
    }
  }
}
</script>

<style scoped>
.action-button-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.action-button-group--horizontal {
  flex-direction: row;
}

.action-button-group--vertical {
  flex-direction: column;
  align-items: stretch;
}

/* 间距控制 */
.action-button-group--horizontal.action-button-group--gap-small > * {
  margin-right: 6px;
}

.action-button-group--horizontal.action-button-group--gap-default > * {
  margin-right: 8px;
}

.action-button-group--horizontal.action-button-group--gap-large > * {
  margin-right: 12px;
}

.action-button-group--vertical.action-button-group--gap-small > * {
  margin-bottom: 6px;
}

.action-button-group--vertical.action-button-group--gap-default > * {
  margin-bottom: 8px;
}

.action-button-group--vertical.action-button-group--gap-large > * {
  margin-bottom: 12px;
}

/* 移除最后一个元素的边距 */
.action-button-group--horizontal > *:last-child {
  margin-right: 0;
}

.action-button-group--vertical > *:last-child {
  margin-bottom: 0;
}

/* 单项操作按钮组 */
.item-actions-group {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--macaron-border-light);
}

.action-button-group--vertical .item-actions-group {
  margin-left: 0;
  margin-top: 12px;
  padding-left: 0;
  padding-top: 12px;
  border-left: none;
  border-top: 1px solid var(--macaron-border-light);
}

/* 紧凑模式 */
.action-button-group--compact .item-actions-group {
  margin-left: 8px;
  padding-left: 8px;
}

.action-button-group--compact.action-button-group--vertical .item-actions-group {
  margin-left: 0;
  margin-top: 8px;
  padding-left: 0;
  padding-top: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-button-group {
    gap: 6px;
  }
  
  .action-button-group--horizontal > * {
    margin-right: 6px;
  }
  
  .item-actions-group {
    margin-left: 8px;
    padding-left: 8px;
  }
}
</style> 