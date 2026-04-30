"""
文档检索器
基于向量存储进行相似度检索
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from ..embeddings.embedding_generator import EmbeddingGenerator
from ..storage.vector_store import VectorStore
from ..chunkers.text_chunker import TextChunk

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentRetriever:
    """文档检索器类"""

    def __init__(self,
                 vector_store: VectorStore,
                 embedding_generator: EmbeddingGenerator,
                 top_k: int = 5,
                 min_similarity: float = 0.7):
        """
        初始化文档检索器

        Args:
            vector_store: 向量存储对象
            embedding_generator: 嵌入生成器
            top_k: 返回的最相关文档数量
            min_similarity: 最小相似度阈值
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k
        self.min_similarity = min_similarity

        logger.info(f"文档检索器初始化完成 - TopK: {top_k}, 最小相似度: {min_similarity}")

    def retrieve(self,
               query: str,
               top_k: Optional[int] = None,
               min_similarity: Optional[float] = None,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 用户查询问题
            top_k: 返回的文档数量
            min_similarity: 最小相似度阈值
            filter_metadata: 元数据过滤条件

        Returns:
            包含相关文档及其元数据的列表
        """
        if top_k is None:
            top_k = self.top_k
        if min_similarity is None:
            min_similarity = self.min_similarity

        logger.info(f"开始检索: {query}")

        try:
            # 生成查询向量
            query_embedding = self.embedding_generator.generate_embedding(query)

            # 检索相关文档
            results = self.vector_store.search(
                query_embedding,
                k=top_k * 2,  # 获取更多结果以便过滤
                filter_metadata=filter_metadata
            )

            # 过滤低相似度结果并返回指定数量
            filtered_results = []
            for chunk, similarity in results:
                if similarity >= min_similarity:
                    filtered_results.append({
                        'content': chunk.content,
                        'metadata': chunk.metadata,
                        'similarity': similarity,
                        'chunk_id': chunk.chunk_id,
                        'chunk_index': chunk.chunk_index,
                        'token_count': chunk.token_count
                    })

                if len(filtered_results) >= top_k:
                    break

            logger.info(f"检索完成，返回 {len(filtered_results)}/{len(results)} 个相关文档")
            return filtered_results

        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            raise

    def retrieve_with_rerank(self,
                           query: str,
                           top_k: int = 5,
                           rerank_top_k: int = 10) -> List[Dict[str, Any]]:
        """
        检索并重新排序（简单的重排序策略）

        Args:
            query: 用户查询
            top_k: 最终返回的结果数量
            rerank_top_k: 初步检索的结果数量

        Returns:
            重排序后的文档列表
        """
        logger.info(f"开始检索并重排序: {query}")

        # 初步检索获取更多结果
        initial_results = self.retrieve(query, top_k=rerank_top_k, min_similarity=0.0)

        # 简单的重排序：基于与查询的关键词重叠度
        query_keywords = set(query.lower().split())

        reranked_results = []
        for result in initial_results:
            content = result['content'].lower()
            keyword_matches = len(query_keywords & set(content.split()))
            result['rerank_score'] = result['similarity'] * 0.7 + (keyword_matches / len(query_keywords)) * 0.3
            reranked_results.append(result)

        # 按重排序分数排序
        reranked_results.sort(key=lambda x: x['rerank_score'], reverse=True)

        logger.info(f"重排序完成，返回前 {min(top_k, len(reranked_results))} 个结果")
        return reranked_results[:top_k]

    def format_retrieved_docs(self, docs: List[Dict[str, Any]]) -> str:
        """
        格式化检索到的文档，便于Prompt组装

        Args:
            docs: 检索到的文档列表

        Returns:
            格式化后的文档字符串
        """
        if not docs:
            return "未找到相关文档。"

        formatted_docs = []
        for i, doc in enumerate(docs, 1):
            formatted_doc = f"""[文档 {i}] (相似度: {doc['similarity']:.4f})
{doc['content']}
来源: {doc['metadata'].get('source', '未知')} | 页码: {doc['metadata'].get('page', '未知')}
"""
            formatted_docs.append(formatted_doc)

        return "\n".join(formatted_docs)


def main():
    """测试检索器"""
    from ..storage.vector_store import VectorStore
    from ..chunkers.text_chunker import TextChunk

    # 创建测试数据
    test_chunks = [
        TextChunk(
            content="巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。",
            metadata={'category': 'baroque', 'period': '1600-1750'},
            chunk_index=0,
            chunk_id="baroque_0",
            token_count=15
        ),
        TextChunk(
            content="古典主义音乐时期从1750年到1820年，以海顿、莫扎特、贝多芬为代表。",
            metadata={'category': 'classical', 'period': '1750-1820'},
            chunk_index=1,
            chunk_id="classical_0",
            token_count=18
        ),
        TextChunk(
            content="浪漫主义音乐时期从1820年到1900年，强调个人情感的表达。",
            metadata={'category': 'romantic', 'period': '1820-1900'},
            chunk_index=2,
            chunk_id="romantic_0",
            token_count=12
        )
    ]

    # 初始化组件
    generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    embedding_result = generator.generate_embeddings(test_chunks)

    store = VectorStore(index_type="flat", metric="cosine")
    store.add_embeddings(embedding_result)

    # 创建检索器
    retriever = DocumentRetriever(
        vector_store=store,
        embedding_generator=generator,
        top_k=2,
        min_similarity=0.5
    )

    # 测试检索
    query = "巴洛克音乐有什么特点？"
    results = retriever.retrieve(query)

    print(f"查询: {query}")
    print("检索结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. [相似度: {result['similarity']:.4f}]")
        print(f"     {result['content']}")

    # 测试格式化
    print("\n格式化的检索结果:")
    print(retriever.format_retrieved_docs(results))


if __name__ == "__main__":
    main()