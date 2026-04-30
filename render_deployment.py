"""
Render部署配置文件
用于在Render上部署西方音乐史RAG系统
"""
import os

# Render配置文件内容
render_config = """
# Render部署配置
services:
  - type: web
    name: western-music-rag-system
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python app/advanced_music_server.py
    envVars:
      - key: PORT
        value: "8000"

# 或者使用Docker配置
# docker:
#   web:
#     dockerfilePath: ./Dockerfile
#     context: .
"""

def create_render_required_files():
    """创建Render部署所需文件"""

    # 1. 创建render.yaml配置文件
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_config)

    # 2. 创建Procfile（Render需要）
    procfile = """web: python app/advanced_music_server.py
"""
    with open('Procfile', 'w', encoding='utf-8') as f:
        f.write(procfile)

    # 3. 创建requirements.txt（如果不存在或更新）
    requirements = """http.server>=0.1
flask>=2.0.0
"""
    # 检查并合并现有的requirements.txt
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            existing_content = f.read()
        # 合并requirements
        existing_lines = existing_content.strip().split('\n')
        new_lines = requirements.strip().split('\n')
        # 合并去重
        combined_requirements = list(set(existing_lines + new_lines))
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(combined_requirements))
    else:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)

    print("[OK] Render deployment files created successfully")
    print("📋 创建的文件：")
    print("   - render.yaml (Render配置)")
    print("   - Procfile (启动命令)")
    print("   - requirements.txt (依赖包)")

def create_github_deploy_guide():
    """创建GitHub部署指南"""
    guide = """# 🚀 Render部署指南

## 准备工作

### 1. 确保GitHub仓库包含以下文件：
- render.yaml (已自动创建)
- Procfile (已自动创建)
- requirements.txt (已更新)
- app/advanced_music_server.py (主要服务器)
- app/index.html (前端界面)

### 2. 在Render上部署步骤：

#### 方法A：通过Render界面（推荐）
1. 登录 [Render](https://dashboard.render.com/)
2. 点击 "New +"
3. 选择 "Web Service"
4. 连接您的GitHub仓库
5. 配置：
   - Name: `western-music-rag-system`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app/advanced_music_server.py`
   - Plan: `Free`
6. 点击 "Create Web Service"

#### 方法B：通过Render CLI（高级）
1. 安装Render CLI：
   ```bash
   npm install -g render
   ```
2. 连接GitHub仓库并部署：
   ```bash
   render connect
   ```

## 部署后

### API地址：
- 自动分配的HTTPS URL，如：`https://western-music-rag-system.onrender.com`
- API端点：`https://western-music-rag-system.onrender.com/api/query`
- 健康检查：`https://western-music-rag-system.onrender.com/api/health`

### 环境变量：
- PORT: 8000 (自动设置)
- 其他变量可在Render控制台配置

## 测试

### 部署成功后测试：
```bash
# 测试API健康
curl https://western-music-rag-system.onrender.com/api/health

# 测试问答功能
curl -X POST https://western-music-rag-system.onrender.com/api/query \\
  -H "Content-Type: application/json" \\
  -d '{"query": "贝多芬的主要作品有哪些？"}'
```

## 注意事项

1. Render免费计划限制：
   - 512MB内存
   - 无域名限制
   - 可能有冷启动时间

2. 如需更高配置：
   - 升级到付费计划
   - 配置自定义域名

3. 监控和日志：
   - 在Render Dashboard查看部署日志
   - 监控性能和错误率
"""

    with open('RENDER_DEPLOY_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)

    print("[OK] Render deployment guide created successfully")
    print("📋 文件：RENDER_DEPLOY_GUIDE.md")

if __name__ == "__main__":
    print("=" * 70)
    print("Render部署文件生成")
    print("=" * 70)
    print()

    create_render_required_files()
    print()
    create_github_deploy_guide()

    print("=" * 70)
    print("准备完成！")
    print("=" * 70)
    print()
    print("📝 下一步：")
    print("1. 提交这些新文件到Git")
    print("   git add render.yaml Procfile RENDER_DEPLOY_GUIDE.md")
    print("   git commit -m 'Add Render deployment files'")
    print("   git push origin main")
    print()
    print("2. 在Render上部署")
    print("   访问 https://dashboard.render.com/")
    print("   连接GitHub仓库")
    print("   配置并创建Web Service")
