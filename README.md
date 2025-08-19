# 舒克AI工具集 (ShukeAITools)

> 🎨 一个基于Web的AI工具集合平台，主要用于技术交流和学习

## 📖 项目简介

舒克AI工具集是一个开源项目，旨在为开发者和AI爱好者提供便捷的AI工具使用体验。本项目采用前后端分离架构，支持多种AI平台的集成和管理。

**⚠️ 免责声明：本项目仅供技术交流和学习使用，请勿用于商业用途。**

## ✨ 主要特性

- 🖥️ **现代化界面**：基于Vue 3 + Element Plus的响应式Web界面
- 🔧 **模块化设计**：支持多平台AI工具的集成和扩展
- 📊 **任务管理**：智能任务队列管理和状态监控
- 👥 **账号管理**：统一的账号管理和使用统计
- 💾 **数据持久化**：基于SQLite的轻量级数据存储
- 🔄 **实时更新**：任务状态实时监控和更新

## 🚀 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3组件库
- **Vite** - 现代化构建工具

### 后端
- **Python 3.9+** - 核心开发语言
- **Flask** - 轻量级Web框架
- **Peewee** - 简洁的ORM框架
- **Playwright** - 浏览器自动化工具
- **SQLite** - 嵌入式数据库

## 📋 环境要求

### 系统要求
- **Python 3.9+** (需要自行安装)
- **Node.js 16+** (用于前端开发)
- **现代浏览器** (Chrome、Firefox、Safari、Edge)

### 支持的操作系统
- macOS 10.14+
- Windows 10+
- Linux (Ubuntu 18.04+)

## 🛠️ 安装与启动

### 方式一：使用启动脚本（推荐）

#### macOS/Linux
```bash
# 克隆项目
git@github.com:shukeCyp/ShukeAITools.git
cd ShukeAITools

# 给脚本执行权限
chmod +x scripts/start_all.sh

# 启动所有服务
./scripts/start_all.sh
```

#### Windows
```cmd
# 克隆项目
git clone https://github.com/your-username/ShukeAITools.git
cd ShukeAITools

# 启动所有服务
scripts\start_all.bat
```

### 方式二：手动启动

#### 1. 启动后端服务
```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python app.py
```

#### 2. 启动前端服务
```bash
# 新开终端窗口，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端开发服务器
npm run dev
```

### 3. 访问应用

启动成功后，在浏览器中访问：
- 🌐 **前端界面**: http://localhost:5173
- 🔧 **后端API**: http://localhost:8888

## 📱 功能模块

### ✅ 已实现功能

#### 🎨 即梦文生图
- **智能任务管理**：支持单个和批量任务创建
- **多账号支持**：自动轮换账号，避免频率限制
- **实时监控**：任务状态实时更新和进度跟踪
- **批量下载**：支持批量下载生成的图片到本地
- **灵活配置**：支持多种模型、分辨率和质量设置

**支持的参数**：
- 模型：Image 1.4, Image 2.0 Pro, Image 2.1, Image 3.0, Image 3.1
- 分辨率：21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16
- 质量：1K

### 🚧 开发计划 (TODO)

#### 📹 即梦图生视频
- [ ] 图片上传和管理
- [ ] 视频生成参数配置
- [ ] 视频任务队列管理
- [ ] 生成进度监控
- [ ] 视频下载和预览

#### 🤖 即梦数字人
- [ ] 数字人模型选择
- [ ] 语音输入和文本转换
- [ ] 数字人视频生成
- [ ] 表情和动作控制
- [ ] 批量数字人视频制作

## 🔧 配置说明

### 基础配置
在 `基础配置` 页面可以设置：
- **自动化线程数**：控制并发任务数量
- **隐藏窗口**：是否在无头模式下运行浏览器

### 账号管理
在 `账号配置` 页面可以：
- 添加和管理即梦平台账号
- 查看账号使用统计
- 批量导入账号信息

## 📁 项目结构

```
ShukeAITools/
├── backend/                 # 后端代码
│   ├── api/                # API路由
│   ├── core/               # 核心模块
│   ├── managers/           # 任务管理器
│   ├── models/             # 数据模型
│   ├── utils/              # 工具函数
│   └── app.py              # 主应用入口
├── frontend/               # 前端代码
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── utils/          # 工具函数
│   └── package.json        # 依赖配置
├── scripts/                # 启动脚本
│   ├── start_all.sh        # 启动所有服务(Unix)
│   ├── start_all.bat       # 启动所有服务(Windows)
│   └── ...
└── README.md               # 项目说明
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 开源协议

本项目采用 MIT 协议，详情请参见 [LICENSE](LICENSE) 文件。

## ⚠️ 注意事项

1. **仅供学习使用**：本项目仅用于技术交流和学习，请勿用于商业用途
2. **账号安全**：请妥善保管你的平台账号信息，本项目不对账号安全负责
3. **合规使用**：请遵守相关平台的使用条款和法律法规
4. **数据备份**：建议定期备份重要的任务数据和配置信息

## 📞 联系方式

- **项目地址**：https://github.com/your-username/ShukeAITools
- **问题反馈**：https://github.com/your-username/ShukeAITools/issues

## 🙏 致谢

感谢所有为这个项目贡献代码和建议的开发者们！

---

**⭐ 如果这个项目对你有帮助，请给它一个Star！**