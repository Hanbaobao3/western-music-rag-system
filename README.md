# RAG检索增强生成系统

## 项目概述
这是一个基于RAG（Retrieval-Augmented Generation）技术的智能检索系统，支持在线访问和文档问答。

## 系统架构

### 离线阶段（当前实现）
1. **数据导入** - 支持PDF、TXT等格式文档
2. **文档解析** - 提取文本内容，保留结构信息
3. **文本切块** - 智能分块，保持语义完整性
4. **向量化** - 使用嵌入模型将文本转换为向量
5. **存储** - 向量数据库存储和索引

### 在线阶段（待实现）
1. **查询处理** - 用户问题向量化
2. **相似度检索** - 检索相关文档块
3. **答案生成** - 基于检索内容生成答案
4. **Web界面** - 提供在线访问接口

## 技术栈
- **语言**: Python 3.8+
- **文档处理**: PyPDF2, pdfplumber
- **文本处理**: langchain, nltk
- **向量化**: sentence-transformers
- **向量数据库**: FAISS, ChromaDB
- **Web框架**: Flask/FastAPI
- **前端**: React/Vue

## 目录结构
```
rag-system/
├── data/              # 原始文档数据
├── processed/         # 处理后的数据
├── models/            # 模型文件
├── config/            # 配置文件
├── src/               # 源代码
│   ├── parsers/       # 文档解析器
│   ├── chunkers/      # 文本切块器
│   ├── embeddings/    # 向量化模块
│   ├── storage/       # 存储模块
│   └── utils/         # 工具函数
├── app/               # Web应用
├── requirements.txt   # 依赖列表
└── README.md         # 项目说明
```

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 离线处理
```bash
python src/offline_pipeline.py --input data/your_document.pdf
```

### 在线服务
```bash
python app/server.py
```

## 配置说明
详细配置请参考 `config/config.yaml`

## 许可证
MIT License