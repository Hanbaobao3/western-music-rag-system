"""
向量化生成器
使用预训练模型将文本转换为向量
"""
import os
import logging
import pickle
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from ..chunkers.text_chunker import TextChunk

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """嵌入结果数据结构"""
    embeddings: np.ndarray
    chunks: List[TextChunk]
    model_name: str
    embedding_dim: int


class EmbeddingGenerator:
    """嵌入生成器类"""

    def __init__(self,
                 model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 device: str = "cpu",
                 cache_dir: Optional[str] = None):
        """
        初始化嵌入生成器

        Args:
            model_name: 预训练模型名称
            device: 运行设备 ('cpu' 或 'cuda')
            cache_dir: 模型缓存目录
        """
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir
        self.model = None

        logger.info(f"嵌入生成器初始化完成 - 模型: {model_name}, 设备: {device}")

    def load_model(self):
        """加载嵌入模型"""
        if self.model is not None:
            return

        logger.info(f"正在加载模型: {self.model_name}")

        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir
            )
            logger.info(f"模型加载成功，嵌入维度: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise

    def generate_embeddings(self, chunks: List[TextChunk]) -> EmbeddingResult:
        """
        为文本块生成嵌入向量

        Args:
            chunks: 文本块列表

        Returns:
            包含嵌入向量和元数据的结果对象
        """
        if not chunks:
            logger.warning("文本块列表为空")
            return EmbeddingResult(
                embeddings=np.array([]),
                chunks=[],
                model_name=self.model_name,
                embedding_dim=0
            )

        self.load_model()

        logger.info(f"开始生成 {len(chunks)} 个文本块的嵌入向量")

        try:
            # 提取文本内容
            texts = [chunk.content for chunk in chunks]

            # 生成嵌入
            embeddings = self.model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True  # 归一化，便于相似度计算
            )

            # 处理可能的维度问题
            if len(embeddings.shape) == 3:
                embeddings = embeddings.squeeze(1)

            embedding_dim = embeddings.shape[1] if len(embeddings.shape) > 1 else embeddings.shape[0]
            logger.info(f"嵌入生成完成，维度: {embedding_dim}")

            return EmbeddingResult(
                embeddings=embeddings,
                chunks=chunks,
                model_name=self.model_name,
                embedding_dim=embedding_dim
            )

        except Exception as e:
            logger.error(f"嵌入生成失败: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        为单个文本生成嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        self.load_model()

        # 确保文本是字符串格式，修复新版sentence-transformers的API兼容性
        if not isinstance(text, str):
            text = str(text)

        # 新版sentence-transformers要求传入列表
        embedding = self.model.encode(
            [text],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # 如果是批量编码，返回第一个结果
        if len(embedding.shape) == 2:
            embedding = embedding[0]

        return embedding

    def compute_similarity(self, query_embedding: np.ndarray,
                          doc_embeddings: np.ndarray) -> np.ndarray:
        """
        计算查询向量与文档向量之间的相似度

        Args:
            query_embedding: 查询向量
            doc_embeddings: 文档向量矩阵

        Returns:
            相似度分数数组
        """
        # 使用余弦相似度（因为向量已归一化，直接点积即可）
        similarities = np.dot(doc_embeddings, query_embedding.T)
        return similarities

    def save_embeddings(self, embedding_result: EmbeddingResult, save_path: str):
        """
        保存嵌入结果到文件

        Args:
            embedding_result: 嵌入结果对象
            save_path: 保存路径
        """
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                pickle.dump({
                    'embeddings': embedding_result.embeddings,
                    'chunks': embedding_result.chunks,
                    'model_name': embedding_result.model_name,
                    'embedding_dim': embedding_result.embedding_dim
                }, f)

            logger.info(f"嵌入结果已保存到: {save_path}")

        except Exception as e:
            logger.error(f"保存嵌入结果失败: {str(e)}")
            raise

    def load_embeddings(self, load_path: str) -> EmbeddingResult:
        """
        从文件加载嵌入结果

        Args:
            load_path: 加载路径

        Returns:
            嵌入结果对象
        """
        try:
            with open(load_path, 'rb') as f:
                data = pickle.load(f)

            logger.info(f"嵌入结果已从 {load_path} 加载")
            logger.info(f"嵌入维度: {data['embedding_dim']}, 文本块数量: {len(data['chunks'])}")

            return EmbeddingResult(
                embeddings=data['embeddings'],
                chunks=data['chunks'],
                model_name=data['model_name'],
                embedding_dim=data['embedding_dim']
            )

        except Exception as e:
            logger.error(f"加载嵌入结果失败: {str(e)}")
            raise


def main():
    """测试嵌入生成器"""
    from ..chunkers.text_chunker import TextChunk

    # 创建测试文本块
    test_chunks = [
        TextChunk(
            content="人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的机器。",
            metadata={'test': True},
            chunk_index=0,
            chunk_id="test_0",
            token_count=20
        ),
        TextChunk(
            content="机器学习是人工智能的一个子领域，专注于让系统从数据中学习和改进。",
            metadata={'test': True},
            chunk_index=1,
            chunk_id="test_1",
            token_count=15
        ),
        TextChunk(
            content="自然语言处理是AI的一个重要应用领域，涉及计算机与人类语言的交互。",
            metadata={'test': True},
            chunk_index=2,
            chunk_id="test_2",
            token_count=18
        )
    ]

    # 创建嵌入生成器
    generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")

    # 生成嵌入
    result = generator.generate_embeddings(test_chunks)

    print(f"嵌入生成完成:")
    print(f"  模型: {result.model_name}")
    print(f"  嵌入维度: {result.embedding_dim}")
    print(f"  文本块数量: {len(result.chunks)}")

    # 测试相似度计算
    query = "什么是机器学习？"
    query_embedding = generator.generate_embedding(query)

    similarities = generator.compute_similarity(query_embedding, result.embeddings)

    print(f"\n查询: {query}")
    print("相似度排序:")
    sorted_indices = np.argsort(similarities)[::-1]
    for i, idx in enumerate(sorted_indices):
        chunk = result.chunks[idx]
        similarity = similarities[idx]
        print(f"  {i+1}. [{similarity:.4f}] {chunk.content[:50]}...")


if __name__ == "__main__":
    main()