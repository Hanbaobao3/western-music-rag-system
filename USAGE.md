# RAG系统使用说明

## 快速开始

### 1. 环境准备

#### 安装Python依赖
```bash
cd E:/ai-apps/rag-system
pip install -r requirements.txt
```

#### 下载模型（首次运行会自动下载）
系统会自动下载 `paraphrase-multilingual-MiniLM-L12-v2` 模型到 `./models` 目录。

### 2. 准备数据

将您的文档放到 `data/` 目录下，支持以下格式：
- PDF文件 (.pdf)
- 文本文件 (.txt)
- Word文档 (.docx)
- Excel文件 (.xlsx)

### 3. 运行离线处理

#### 处理单个文档
```bash
python src/offline_pipeline.py --input data/your_document.pdf --output processed/vector_store --stats
```

#### 处理整个目录
```bash
python src/offline_pipeline.py --input data/ --output processed/vector_store --stats
```

### 4. 测试系统

运行测试脚本验证各模块功能：
```bash
python test_system.py
```

## 配置说明

配置文件位于 `config/config.yaml`，主要配置项：

### 文档处理配置
```yaml
document_processing:
  supported_formats: [pdf, txt, docx, xlsx]
  pdf:
    extract_images: false
    preserve_layout: true
```

### 文本切块配置
```yaml
chunking:
  chunk_size: 512           # 每块最大token数
  chunk_overlap: 50         # 块间重叠token数
  use_semantic: true        # 是否使用语义分块
```

### 嵌入模型配置
```yaml
embeddings:
  model_name: "paraphrase-multilingual-MiniLM-L12-v2"
  device: "cpu"             # 使用CPU或GPU
  cache_dir: "./models"
```

### 向量存储配置
```yaml
vector_store:
  index_type: "flat"        # FAISS索引类型
  metric: "cosine"          # 相似度度量
  storage_path: "./processed/vector_store"
```

## 文件结构

```
rag-system/
├── config/
│   └── config.yaml        # 配置文件
├── data/                   # 原始文档目录
├── processed/              # 处理后的数据目录
│   └── vector_store/       # 向量存储文件
├── models/                 # 模型缓存目录
├── src/                    # 源代码目录
│   ├── parsers/            # 文档解析器
│   ├── chunkers/           # 文本切块器
│   ├── embeddings/         # 向量化模块
│   ├── storage/            # 向量存储模块
│   └── utils/              # 工具函数
├── test_system.py          # 测试脚本
├── requirements.txt        # Python依赖
└── USAGE.md               # 本文件
```

## 常见问题

### Q1: 模型下载失败怎么办？
A: 系统会自动从HuggingFace下载模型，如果网络不通，可以：
- 使用代理
- 手动下载模型到 `./models` 目录

### Q2: 如何使用GPU加速？
A: 修改配置文件中的 `embeddings.device: "cuda"`，并确保已安装CUDA版本的PyTorch。

### Q3: 处理大型文档很慢怎么办？
A: 可以：
- 使用更大的块大小减少块数量
- 使用IVF或HNSW索引类型
- 启用GPU加速

### Q4: 如何处理其他格式的文档？
A: 在 `src/parsers/` 目录下添加对应的解析器。

## 下一步

离线阶段完成后，您可以：

1. **实现在线阶段**
   - 开发Web界面
   - 实现查询API
   - 添加答案生成功能

2. **优化系统**
   - 尝试不同的嵌入模型
   - 调整切块参数
   - 优化检索策略

3. **扩展功能**
   - 支持更多文档格式
   - 添加多模态支持
   - 实现实时更新

## 技术支持

如有问题，请查看日志文件 `./logs/rag_system.log` 获取详细信息。