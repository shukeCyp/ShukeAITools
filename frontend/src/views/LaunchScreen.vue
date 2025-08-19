<template>
  <div class="launch-screen" @click="enterApp">
    <!-- 星空背景 -->
    <div class="starfield">
      <!-- 流星雨 -->
      <div v-for="i in 12" :key="`meteor-${i}`" class="meteor" :style="getMeteorStyle(i)"></div>
      
      <!-- 星星 -->
      <div v-for="i in 200" :key="`star-${i}`" class="star" :style="getStarStyle(i)"></div>
      
      <!-- 闪烁星星 -->
      <div v-for="i in 50" :key="`twinkle-${i}`" class="star twinkle" :style="getTwinkleStarStyle(i)"></div>
    </div>

    <!-- 中间标题动画 -->
    <div class="title-container">
      <div class="app-title" :class="{ 'animate-in': showTitle }">
        <span v-for="(char, index) in titleChars" :key="index" 
              class="title-char" 
              :style="{ animationDelay: `${index * 0.1 + 1}s` }">
          {{ char }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'LaunchScreen',
  emits: ['enter-app'],
  setup(props, { emit }) {
    const launching = ref(false)
    const showTitle = ref(false)
    const titleChars = ref(['舒', '克', 'A', 'I', '工', '具', '集'])

    const getStarStyle = (index) => {
      const size = Math.random() * 3 + 1
      const x = Math.random() * 100
      const y = Math.random() * 100
      const opacity = Math.random() * 0.8 + 0.2
      
      return {
        width: `${size}px`,
        height: `${size}px`,
        left: `${x}%`,
        top: `${y}%`,
        opacity: opacity
      }
    }

    const getTwinkleStarStyle = (index) => {
      const size = Math.random() * 2 + 2
      const x = Math.random() * 100
      const y = Math.random() * 100
      const duration = Math.random() * 3 + 2
      const delay = Math.random() * 5
      
      return {
        width: `${size}px`,
        height: `${size}px`,
        left: `${x}%`,
        top: `${y}%`,
        animationDuration: `${duration}s`,
        animationDelay: `${delay}s`
      }
    }

    const getMeteorStyle = (index) => {
      const x = Math.random() * 120 - 10 // 从屏幕左上角开始
      const y = Math.random() * 50 - 10
      const duration = Math.random() * 4 + 3
      const delay = Math.random() * 8
      
      return {
        left: `${x}%`,
        top: `${y}%`,
        animationDuration: `${duration}s`,
        animationDelay: `${delay}s`
      }
    }

    const enterApp = async () => {
      if (launching.value) return
      launching.value = true
      
      emit('enter-app', 'home')
    }

    onMounted(() => {
      // 1秒后显示标题动画
      setTimeout(() => {
        showTitle.value = true
      }, 1000)
    })

    return {
      launching,
      showTitle,
      titleChars,
      getStarStyle,
      getTwinkleStarStyle,
      getMeteorStyle,
      enterApp
    }
  }
}
</script>

<style scoped>
.launch-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(ellipse at center, #1e3c72 0%, #2a5298 50%, #0f1419 100%);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

/* 星空背景 */
.starfield {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 普通星星 */
.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8);
}

/* 闪烁星星 */
.star.twinkle {
  animation: twinkle linear infinite;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.9);
}

@keyframes twinkle {
  0%, 100% { 
    opacity: 0.3;
    transform: scale(1);
  }
  50% { 
    opacity: 1;
    transform: scale(1.2);
  }
}

/* 流星 */
.meteor {
  position: absolute;
  width: 2px;
  height: 100px;
  background: linear-gradient(to bottom, 
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.8) 40%,
    rgba(135, 206, 235, 1) 100%);
  animation: meteorDiagonal linear infinite;
  opacity: 0;
  transform: rotate(45deg); /* 固定45度角，斜向右下 */
}

.meteor::before {
  content: '';
  position: absolute;
  top: 0;
  left: -1px;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 1);
  border-radius: 50%;
  box-shadow: 0 0 12px rgba(135, 206, 235, 1), 0 0 20px rgba(255, 255, 255, 0.8);
}

@keyframes meteorDiagonal {
  0% {
    opacity: 0;
    transform: rotate(45deg) translateY(-200px);
  }
  5% {
    opacity: 1;
  }
  95% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: rotate(45deg) translateY(calc(100vh + 200px));
  }
}

/* 标题容器 */
.title-container {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

/* 应用标题 */
.app-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.title-char {
  font-size: 4rem;
  font-weight: 700;
  color: white;
  text-shadow: 
    0 0 20px rgba(255, 255, 255, 0.8),
    0 0 40px rgba(135, 206, 235, 0.6),
    0 0 60px rgba(135, 206, 235, 0.4);
  opacity: 0;
  transform: translateY(50px) scale(0.5);
  animation: charFadeIn 0.8s ease-out forwards;
}

@keyframes charFadeIn {
  0% {
    opacity: 0;
    transform: translateY(50px) scale(0.5) rotateY(90deg);
  }
  50% {
    transform: translateY(-10px) scale(1.1) rotateY(0deg);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1) rotateY(0deg);
  }
}

/* 每个字符的特殊效果 */
.title-char:nth-child(1) { color: #ff6b6b; }
.title-char:nth-child(2) { color: #4ecdc4; }
.title-char:nth-child(3) { color: #45b7d1; }
.title-char:nth-child(4) { color: #96ceb4; }
.title-char:nth-child(5) { color: #ffeaa7; }
.title-char:nth-child(6) { color: #dda0dd; }
.title-char:nth-child(7) { color: #98d8c8; }

/* 整体标题动画 */
.app-title.animate-in .title-char {
  animation-play-state: running;
}

/* 标题呼吸效果 */
.app-title.animate-in {
  animation: titleBreathe 4s ease-in-out infinite 2s;
}

@keyframes titleBreathe {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
  }
  50% {
    transform: scale(1.05);
    filter: drop-shadow(0 0 30px rgba(135, 206, 235, 0.6));
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .title-char {
    font-size: 3rem;
    gap: 6px;
  }
}

@media (max-width: 480px) {
  .title-char {
    font-size: 2.5rem;
    gap: 4px;
  }
}
</style>