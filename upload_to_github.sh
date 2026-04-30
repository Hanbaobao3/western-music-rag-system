#!/bin/bash
# Western Music History RAG System - 上传到GitHub脚本

echo "======================================"
echo "西方音乐史RAG系统 - 上传到GitHub"
echo "======================================"
echo ""

# 检查是否已设置GitHub仓库
if git remote | grep -q "origin"; then
    echo "✅ 已配置GitHub远程仓库"
    git remote -v
else
    echo "❌ 未配置GitHub远程仓库"
    echo ""
    echo "请按以下步骤手动设置："
    echo ""
    echo "1. 访问 https://github.com/new"
    echo "2. 创建新仓库：western-music-rag-system"
    echo "3. 运行以下命令连接仓库："
    echo ""
    echo "   git remote add origin https://github.com/你的用户名/western-music-rag-system.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    exit 1
fi

echo ""
echo "准备推送到GitHub..."
echo ""

# 重命名主分支为main（GitHub推荐）
git branch -M main

# 推送到GitHub
git push -u origin main

echo ""
echo "======================================"
echo "🎉 上传完成！"
echo "======================================"
echo ""
echo "仓库地址：https://github.com/你的用户名/western-music-rag-system"
echo ""
echo "下一步："
echo "1. 在GitHub上查看您的代码"
echo "2. 按照 DEPLOYMENT_GUIDE.md 进行线上部署"
echo "3. 选择合适的部署方案（GitHub Pages/Render/Vercel等）"
