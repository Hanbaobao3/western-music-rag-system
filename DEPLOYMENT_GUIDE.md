# Western Music History RAG System - 部署指南

## 🚀 项目状态
✅ Git仓库已初始化
✅ 初始提交已完成（53个文件）
✅ 项目准备就绪上传GitHub

## 📋 部署步骤

### 步骤1：创建GitHub仓库
1. 登录到 [GitHub](https://github.com)
2. 点击右上角 "+" 按钮 → "New repository"
3. 填写仓库信息：
   - **Repository name**: `western-music-rag-system`
   - **Description**: `Intelligent RAG-based Western Music History Q&A System with professional knowledge base`
   - **Visibility**: ✅ Public (推荐)
4. 点击 "Create repository" 按钮

### 步骤2：连接本地仓库到GitHub
创建仓库后，在项目目录运行以下命令：

```bash
git remote add origin https://github.com/YOUR_USERNAME/western-music-rag-system.git
git branch -M main
git push -u origin main
```

**替换** `YOUR_USERNAME` 为您的GitHub用户名

### 步骤3：GitHub部署选项

#### 选项A：使用GitHub Pages（免费静态网站）

1. 创建 `docs` 文件夹
2. 将 `app/index.html` 复制到 `docs/index.html`
3. 创建 `docs/.nojekyll` 文件（内容为空）
4. 提交并推送：
   ```bash
   mkdir docs
   cp app/index.html docs/index.html
   echo "" > docs/.nojekyll
   git add docs/
   git commit -m "Add GitHub Pages deployment"
   git push origin main
   ```
5. 在GitHub仓库中：
   - Settings → Pages → Source → 选择 `main` 分支
   - 访问：`https://YOUR_USERNAME.github.io/western-music-rag-system/`

#### 选项B：使用Render/Vercel（推荐，支持后端）

1. 注册 [Render](https://render.com/)
2. 点击 "New +" → "Web Service"
3. 连接GitHub仓库并设置：
   - Name: `western-music-rag-api`
   - Environment: Python
   - Start Command: `python app/advanced_music_server.py`
   - Plan: Free
4. 添加环境变量：
   - `PORT`: 8000
5. 部署后获得API地址

#### 选项C：本地开发 + GitHub存储

1. 推送到GitHub作为代码备份
2. 本地运行：`python app/advanced_music_server.py`
3. 网页访问：`file:///E:/ai-apps/rag-system/app/index.html`

## 📊 项目文件结构
```
rag-system/
├── app/                    # 前端和主要后端
│   ├── index.html         # 网页界面
│   ├── advanced_music_server.py  # 最新高级RAG服务器
│   └── ...其他服务器文件
├── data/                   # 知识库文件
│   ├── music history.txt
│   └── music history 2.txt
├── src/                    # 模块化代码（可选）
├── README.md               # 项目说明
└── requirements.txt         # Python依赖
```

## 🔧 配置说明

### 启动服务器
```bash
# 方式1：启动高级RAG服务器
python app/advanced_music_server.py

# 方式2：启动简单版本
python app/working_final_server.py
```

### 访问系统
- **本地访问**：`file:///E:/ai-apps/rag-system/app/index.html`
- **API地址**：`http://127.0.0.1:8000/api/query`
- **健康检查**：`http://127.0.0.1:8000/api/health`

## 📝 重要说明

1. **确保已安装Python 3.8+**
2. **确保服务器端口8000未被占用**
3. **知识库文件**：`data/music history.txt` 和 `data/music history 2.txt` 必须存在
4. **建议部署方案**：GitHub Pages适合纯前端，Render支持全栈部署

## 🎯 推荐的部署方案

### 方案1：前端GitHub Pages + 后端Render
- **优点**：免费、自动HTTPS、专业域名
- **设置**：相对复杂，需要两个平台

### 方案2：纯本地开发
- **优点**：完全控制、无网络延迟
- **缺点**：需要手动启动服务器

### 方案3：纯GitHub代码存储
- **优点**：免费、版本控制、协作方便
- **缺点**：需要本地运行后端

## 🚀 快速开始

上传到GitHub后，您可以：

1. **立即测试本地系统**：
   ```bash
   python app/advanced_music_server.py
   # 然后访问 file:///E:/ai-apps/rag-system/app/index.html
   ```

2. **分享给他人使用**：
   - 分享GitHub仓库链接
   - 提供部署说明
   - 说明需要本地运行后端

3. **持续改进**：
   - 通过GitHub Issues收集反馈
   - Pull Requests进行功能改进
   - 定期更新知识库
