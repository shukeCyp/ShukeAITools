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
- **Python 3.9+** (启动脚本会自动使用UV安装)
- **Node.js 16+** (启动脚本会检测并引导安装)
- **现代浏览器** (Chrome、Firefox、Safari、Edge)

### 支持的操作系统
- macOS 10.14+
- Windows 10+
- Linux (Ubuntu 18.04+)

### 自动化环境管理
本项目使用现代化的包管理工具：
- **UV** - 快速的Python包管理器（自动安装Python和依赖）
- **智能检测** - 自动检测Node.js环境并提供安装引导
- **一键启动** - 无需手动配置环境，脚本自动处理所有依赖

## 🛠️ 安装与启动

### 方式一：分步启动（推荐）

#### macOS/Linux
```bash
# 克隆项目
git clone git@github.com:shukeCyp/ShukeAITools.git
cd ShukeAITools

# 给脚本执行权限
chmod +x scripts/*.sh

# 启动后端服务（自动安装Python和依赖）
./scripts/start_backend.sh

# 新开终端窗口，启动前端服务（自动检测Node.js并引导安装）
./scripts/start_frontend.sh
```

#### Windows
```cmd
# 克隆项目
git clone git@github.com:shukeCyp/ShukeAITools.git
cd ShukeAITools

# 启动后端服务（自动安装Python和依赖）
scripts\start_backend.bat

# 新开命令行窗口，启动前端服务（自动检测Node.js并引导安装）
scripts\start_frontend.bat
```

#### 🚀 智能环境检测
启动脚本具备以下智能功能：

**Python环境管理**：
- 自动检测并安装UV包管理器
- 自动安装Python 3.11
- 自动创建虚拟环境
- 自动安装所有Python依赖

**Node.js环境管理**：
- 自动检测Node.js是否已安装
- 如未安装，提供友好的安装引导：
  - **Windows**：可选择使用内置安装包或在线下载
  - **macOS/Linux**：引导到官网下载或使用包管理器安装

**依赖管理**：
- 智能选择包管理器（优先pnpm，其次npm）
- 自动安装前端依赖
- 自动安装Playwright浏览器

### 方式二：手动启动

如果需要手动控制启动过程，可以使用以下命令：

#### 1. 启动后端服务
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python app.py
```

#### 2. 启动前端服务
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install  # 或 pnpm install

# 启动前端开发服务器
npm run dev  # 或 pnpm run dev
```

### 3. 访问应用

启动成功后，在浏览器中访问：
- 🌐 **前端界面**: http://localhost:9999
- 🔧 **后端API**: http://localhost:8888

> 💡 **提示**：如果前端端口显示为5173，实际访问请使用9999端口

## 📱 功能模块
### 功能模块

- ✅ **即梦国际版文生图**
- 🚧 **即梦国际版图生视频**
- 🚧 **即梦国际版数字人**
- 🚧 **Runway文生图**
- 🚧 **Runway图生视频**
- 🚧 **Vidu图生视频**

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
│   ├── requirements.txt    # Python依赖
│   └── app.py              # 主应用入口
├── frontend/               # 前端代码
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── utils/          # 工具函数
│   └── package.json        # 依赖配置
├── scripts/                # 启动脚本和工具
│   ├── start_backend.sh    # 启动后端服务(Unix)
│   ├── start_backend.bat   # 启动后端服务(Windows)
│   ├── start_frontend.sh   # 启动前端服务(Unix)
│   ├── start_frontend.bat  # 启动前端服务(Windows)
│   ├── uv                  # UV包管理器(Unix)
│   ├── uv.exe              # UV包管理器(Windows)
│   └── node-v22.18.0-x86.msi # Node.js安装包(Windows)
├── INSTALL.md              # 详细安装指南
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
5. **环境要求**：
   - 首次运行需要网络连接以下载依赖
   - Windows用户需要管理员权限来安装Node.js
   - macOS用户可能需要允许运行未知开发者的应用（UV工具）

## 📞 联系方式

- **项目地址**：https://github.com/shukeCyp/ShukeAITools
- **问题反馈**：https://github.com/shukeCyp/ShukeAITools/issues

## 🙏 致谢

感谢所有为这个项目贡献代码和建议的开发者们！

---

**⭐ 如果这个项目对你有帮助，请给它一个Star！**