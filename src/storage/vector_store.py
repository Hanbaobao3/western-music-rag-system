"""
向量存储模块
使用FAISS进行向量存储和相似度检索
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import pickle

import numpy as np
import faiss

from ..embeddings.embedding_generator import EmbeddingResult
from ..chunkers.text_chunker import TextChunk

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """向量存储类"""

    def __init__(self,
                 embedding_dim: int = 384,
                 index_type: str = "flat",
                 metric: str = "cosine"):
        """
        初始化向量存储

        Args:
            embedding_dim: 嵌入向量维度
            index_type: FAISS索引类型 ('flat', 'ivf', 'hnsw')
            metric: 相似度度量 ('cosine', 'l2')
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        self.index = None
        self.chunks = []
        self.id_to_index = {}

        logger.info(f"向量存储初始化完成 - 维度: {embedding_dim}, 类型: {index_type}")

    def add_embeddings(self, embedding_result: EmbeddingResult):
        """
        添加嵌入向量到存储

        Args:
            embedding_result: 嵌入结果对象
        """
        embeddings = embedding_result.embeddings
        chunks = embedding_result.chunks

        if len(embeddings) != len(chunks):
            raise ValueError("嵌入向量数量与文本块数量不匹配")

        if self.index is None:
            self._create_index(embeddings.shape[1])

        # 添加向量到索引
        base_index = len(self.chunks)
        self.index.add(embeddings.astype(np.float32))

        # 存储文本块和映射
        for i, chunk in enumerate(chunks):
            chunk_id = f"{len(self.chunks)}_{chunk.chunk_id}"
            self.chunks.append(chunk)
            self.id_to_index[chunk_id] = base_index + i

        logger.info(f"已添加 {len(chunks)} 个向量到存储，当前总数: {len(self.chunks)}")

    def _create_index(self, dim: int):
        """创建FAISS索引"""
        if self.index_type == "flat":
            # 精确搜索
            if self.metric == "cosine":
                # 余弦相似度需要归一化
                self.index = faiss.IndexFlatIP(dim)
            else:
                self.index = faiss.IndexFlatL2(dim)

        elif self.index_type == "ivf":
            # IVF索引（用于大数据集）
            nlist = 100  # 聚类中心数量
            quantizer = faiss.IndexFlatL2(dim)
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist)

        elif self.index_type == "hnsw":
            # HNSW索引（高性能）
            M = 16  # 每个节点的连接数
            ef_construction = 64  # 构建时的搜索参数
            self.index = faiss.IndexHNSWFlat(dim, M)
            self.index.hnsw.efConstruction = ef_construction

        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}")

        logger.info(f"创建FAISS索引: {self.index_type}")

    def search(self,
               query_embedding: np.ndarray,
               k: int = 5,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[TextChunk, float]]:
        """
        搜索最相似的向量

        Args:
            query_embedding: 查询向量
            k: 返回的最相似结果数量
            filter_metadata: 元数据过滤条件

        Returns:
            包含文本块和相似度分数的列表
        """
        if self.index is None:
            raise ValueError("向量存储为空，请先添加向量")

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # 执行搜索
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)

        # 转换结果
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks) and idx >= 0:
                chunk = self.chunks[idx]

                # 元数据过滤
                if filter_metadata:
                    match = True
                    for key, value in filter_metadata.items():
                        if chunk.metadata.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue

                # 如果使用余弦相似度，距离已经是相似度分数
                # 如果使用L2距离，需要转换
                if self.metric == "l2":
                    similarity = 1 / (1 + distance)
                else:
                    similarity = float(distance)

                results.append((chunk, similarity))

        logger.info(f"搜索完成，返回 {len(results)} 个结果")
        return results

    def save(self, save_path: str):
        """
        保存向量存储到文件

        Args:
            save_path: 保存路径
        """
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 保存FAISS索引
            index_path = save_path + ".index"
            faiss.write_index(self.index, index_path)

            # 保存元数据
            metadata_path = save_path + ".meta"
            with open(metadata_path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'id_to_index': self.id_to_index,
                    'embedding_dim': self.embedding_dim,
                    'index_type': self.index_type,
                    'metric': self.metric
                }, f)

            logger.info(f"向量存储已保存到: {save_path}")

        except Exception as e:
            logger.error(f"保存向量存储失败: {str(e)}")
            raise

    def load(self, load_path: str):
        """
        从文件加载向量存储

        Args:
            load_path: 加载路径
        """
        try:
            # 加载FAISS索引
            index_path = load_path + ".index"
            self.index = faiss.read_index(index_path)

            # 加载元数据
            metadata_path = load_path + ".meta"
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.id_to_index = data['id_to_index']
                self.embedding_dim = data['embedding_dim']
                self.index_type = data['index_type']
                self.metric = data['metric']

            logger.info(f"向量存储已从 {load_path} 加载")
            logger.info(f"向量数量: {len(self.chunks)}, 维度: {self.embedding_dim}")

        except Exception as e:
            logger.error(f"加载向量存储失败: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取向量存储统计信息

        Returns:
            统计信息字典
        """
        return {
            'total_vectors': len(self.chunks),
            'embedding_dim': self.embedding_dim,
            'index_type': self.index_type,
            'metric': self.metric,
            'index_size': self.index.ntotal if self.index else 0
        }

    def delete_by_metadata(self, key: str, value: Any):
        """
        根据元数据删除向量（注意：FAISS不支持真正的删除，需要重建索引）

        Args:
            key: 元数据键
            value: 元数据值
        """
        # 收集需要保留的向量
        new_chunks = []
        new_embeddings = []

        # 由于FAISS的限制，这里只是标记逻辑
        # 实际应用中需要重建索引
        logger.warning("FAISS索引不支持真正的删除操作，需要重建索引")


def main():
    """测试向量存储"""
    from ..embeddings.embedding_generator import EmbeddingGenerator
    from ..chunkers.text_chunker import TextChunk

    # 创建测试数据
    test_chunks = [
        TextChunk(
            content="人工智能技术正在快速发展，应用领域越来越广泛。",
            metadata={'category': 'tech'},
            chunk_index=0,
            chunk_id="test_0",
            token_count=15
        ),
        TextChunk(
            content="深度学习是机器学习的一种重要方法，基于神经网络。",
            metadata={'category': 'tech'},
            chunk_index=1,
            chunk_id="test_1",
            token_count=12
        ),
        TextChunk(
            content="今天天气很好，适合出去散步。",
            metadata={'category': 'life'},
            chunk_index=2,
            chunk_id="test_2",
            token_count=10
        )
    ]

    # 创建嵌入生成器
    generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    embedding_result = generator.generate_embeddings(test_chunks)

    # 创建向量存储
    store = VectorStore(embedding_dim=embedding_result.embedding_dim)
    store.add_embeddings(embedding_result)

    # 测试搜索
    query = "什么是深度学习？"
    query_embedding = generator.generate_embedding(query)

    results = store.search(query_embedding, k=2)

    print(f"查询: {query}")
    print("搜索结果:")
    for i, (chunk, similarity) in enumerate(results):
        print(f"  {i+1}. [{similarity:.4f}] {chunk.content}")
        print(f"      分类: {chunk.metadata.get('category', 'N/A')}")

    # 显示统计信息
    stats = store.get_statistics()
    print(f"\n统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()