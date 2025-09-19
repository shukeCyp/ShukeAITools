// 公共组件库入口文件
import ActionButton from './ActionButton.vue'
import ActionButtonGroup from './ActionButtonGroup.vue'

// 导出组件
export {
  ActionButton,
  ActionButtonGroup
}

// 组件安装函数
export const installCommonComponents = (app) => {
  app.component('ActionButton', ActionButton)
  app.component('ActionButtonGroup', ActionButtonGroup)
}

// 默认导出
export default {
  ActionButton,
  ActionButtonGroup,
  install: installCommonComponents
} 