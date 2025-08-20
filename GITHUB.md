# Windows 系统 GitHub 安装与配置教程

> 📖 本教程将指导您在 Windows 系统上安装 Git 并配置 GitHub，以便能够克隆和管理代码仓库。

## 📋 前置要求

- Windows 10 或更高版本
- 管理员权限（用于安装软件）
- 稳定的网络连接

## 🛠️ 安装步骤

### 第一步：注册 GitHub 账号

1. **访问 GitHub 官网**
   - 打开浏览器，访问：https://github.com
   - 点击右上角的 "Sign up" 按钮

2. **填写注册信息**
   - **用户名**：输入您想要的用户名（全局唯一）
   - **邮箱地址**：输入您的邮箱地址
   - **密码**：设置一个强密码（至少8位，包含字母和数字）

3. **验证账号**
   - 完成人机验证（如果需要）
   - 选择账号类型（个人用户选择 "Personal"）
   - 验证邮箱地址（查看邮箱中的验证邮件并点击确认链接）

4. **完善个人资料**
   - 上传头像（可选）
   - 填写个人简介（可选）
   - 设置个人资料的可见性

### 第二步：下载并安装 Git

1. **访问 Git 官网**
   - 打开浏览器，访问：https://git-scm.com/
   - 点击 "Download for Windows" 按钮

2. **下载安装包**
   - 系统会自动检测您的系统架构（32位或64位）
   - 下载完成后，双击运行安装程序

3. **安装配置**
   - 选择安装路径（建议使用默认路径）
   - 选择组件时，建议勾选以下选项：
     - ✅ Git Bash Here
     - ✅ Git GUI Here
     - ✅ Associate .git* configuration files with the default text editor
     - ✅ Associate .sh files to be run with Bash
   
4. **重要配置选项**
   - **选择默认编辑器**：推荐选择 "Use Visual Studio Code as Git's default editor"（如果已安装VS Code）
   - **调整PATH环境**：选择 "Git from the command line and also from 3rd-party software"
   - **选择HTTPS传输后端**：选择 "Use the OpenSSL library"
   - **配置行尾转换**：选择 "Checkout Windows-style, commit Unix-style line endings"
   - **配置终端模拟器**：选择 "Use Windows' default console window"

### 第三步：验证安装

1. **打开命令提示符**
   - 按 `Win + R`，输入 `cmd`，按回车
   - 或者右键桌面空白处，选择 "Git Bash Here"

2. **检查版本**
   ```bash
   git --version
   ```
   如果显示版本号，说明安装成功

## ⚙️ 配置 Git

### 基础配置

1. **设置用户名和邮箱**
   ```bash
   git config --global user.name "您的用户名"
   git config --global user.email "您的邮箱@example.com"
   ```

2. **验证配置**
   ```bash
   git config --global --list
   ```

### 配置 SSH 密钥（推荐）

1. **生成 SSH 密钥**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "您的邮箱@example.com"
   ```
   - 按回车使用默认文件位置
   - 可以设置密码（推荐）或直接回车跳过

2. **启动 SSH 代理**
   ```bash
   eval "$(ssh-agent -s)"
   ```

3. **添加 SSH 密钥到代理**
   ```bash
   ssh-add ~/.ssh/id_rsa
   ```

4. **复制公钥到剪贴板**
   ```bash
   clip < ~/.ssh/id_rsa.pub
   ```

### 在 GitHub 上添加 SSH 密钥

1. **登录 GitHub**
   - 访问：https://github.com
   - 使用刚才注册的账号登录

2. **添加 SSH 密钥**
   - 点击右上角头像 → Settings
   - 左侧菜单选择 "SSH and GPG keys"
   - 点击 "New SSH key"
   - Title：输入描述（如："我的Windows电脑"）
   - Key：粘贴刚才复制的公钥内容
   - 点击 "Add SSH key"

3. **测试连接**
   ```bash
   ssh -T git@github.com
   ```
   如果看到欢迎信息，说明配置成功

## 📂 克隆仓库

### 使用 SSH 克隆（推荐）
