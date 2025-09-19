<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
    :title="tooltip"
  >
    <span v-if="loading" class="macaron-button-icon">
      <el-icon><Loading /></el-icon>
    </span>
    <span v-else-if="$slots.icon" class="macaron-button-icon">
      <slot name="icon"></slot>
    </span>
    <i v-else-if="icon" :class="['macaron-button-icon', icon]"></i>
    <span v-if="$slots.default" class="macaron-button-text">
      <slot></slot>
    </span>
  </button>
</template>

<script>
import { Loading } from '@element-plus/icons-vue'

export default {
  name: 'ActionButton',
  components: {
    Loading
  },
  props: {
    // 按钮类型
    type: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'success', 'warning', 'danger', 'info', 'secondary'].includes(value)
    },
    // 按钮尺寸
    size: {
      type: String,
      default: 'default',
      validator: (value) => ['small', 'default', 'large'].includes(value)
    },
    // 图标
    icon: {
      type: String,
      default: ''
    },
    // 禁用状态
    disabled: {
      type: Boolean,
      default: false
    },
    // 加载状态
    loading: {
      type: Boolean,
      default: false
    },
    // 提示文本
    tooltip: {
      type: String,
      default: ''
    },
    // 是否为圆形按钮（只显示图标）
    circle: {
      type: Boolean,
      default: false
    },
    // 是否为文本按钮（透明背景）
    text: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    buttonClasses() {
      const classes = ['macaron-button-base', `macaron-button-${this.type}`];
      
      // 尺寸类
      if (this.size !== 'default') {
        classes.push(`macaron-button-${this.size}`);
      }
      
      // 圆形按钮
      if (this.circle) {
        classes.push('macaron-button-circle');
      }
      
      // 文本按钮
      if (this.text) {
        classes.push('macaron-button-text-style');
      }
      
      return classes;
    }
  },
  methods: {
    handleClick(event) {
      if (!this.disabled && !this.loading) {
        this.$emit('click', event);
      }
    }
  }
}
</script>

<style scoped>
@import '../../styles/macaron-colors.css';

/* 按钮类型样式 - 渐变彩色版本 */
.macaron-button-primary {
  background: var(--macaron-primary);
  color: var(--macaron-text-white);
  border: none;
}

.macaron-button-primary:hover:not(:disabled) {
  background: var(--macaron-primary-hover);
}

.macaron-button-primary:active:not(:disabled) {
  background: var(--macaron-primary-active);
}

.macaron-button-success {
  background: var(--macaron-success);
  color: var(--macaron-text-white);
  border: none;
}

.macaron-button-success:hover:not(:disabled) {
  background: var(--macaron-success-hover);
}

.macaron-button-success:active:not(:disabled) {
  background: var(--macaron-success-active);
}

.macaron-button-warning {
  background: var(--macaron-warning);
  color: var(--macaron-text-primary);
  border: none;
}

.macaron-button-warning:hover:not(:disabled) {
  background: var(--macaron-warning-hover);
}

.macaron-button-warning:active:not(:disabled) {
  background: var(--macaron-warning-active);
}

.macaron-button-danger {
  background: var(--macaron-danger);
  color: var(--macaron-text-white);
  border: none;
}

.macaron-button-danger:hover:not(:disabled) {
  background: var(--macaron-danger-hover);
}

.macaron-button-danger:active:not(:disabled) {
  background: var(--macaron-danger-active);
}

.macaron-button-info {
  background: var(--macaron-info);
  color: var(--macaron-text-white);
  border: none;
}

.macaron-button-info:hover:not(:disabled) {
  background: var(--macaron-info-hover);
}

.macaron-button-info:active:not(:disabled) {
  background: var(--macaron-info-active);
}

.macaron-button-secondary {
  background: var(--macaron-secondary);
  color: var(--macaron-text-white);
  border: none;
}

.macaron-button-secondary:hover:not(:disabled) {
  background: var(--macaron-secondary-hover);
}

.macaron-button-secondary:active:not(:disabled) {
  background: var(--macaron-secondary-active);
}

/* 圆形按钮样式 */
.macaron-button-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  padding: 0;
  justify-content: center;
}

.macaron-button-circle.macaron-button-small {
  width: 32px;
  height: 32px;
}

.macaron-button-circle.macaron-button-large {
  width: 44px;
  height: 44px;
}

/* 文本按钮样式 */
.macaron-button-text-style {
  background: transparent;
  box-shadow: none;
  color: var(--macaron-text-primary);
}

.macaron-button-text-style:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.04);
  transform: none;
  box-shadow: none;
}

.macaron-button-text-style:active:not(:disabled) {
  background: rgba(0, 0, 0, 0.08);
}

/* 文本内容样式 */
.macaron-button-text {
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 只有图标的按钮隐藏文本 */
.macaron-button-circle .macaron-button-text {
  display: none;
}
</style> 