"""
RAG系统测试脚本
快速测试各个模块的功能
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.parsers.pdf_parser import PDFParser
from src.chunkers.text_chunker import TextChunker
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.storage.vector_store import VectorStore


def create_test_document():
    """创建测试文档"""
    test_doc_path = "data/test_document.txt"
    os.makedirs("data", exist_ok=True)

    test_content = """
人工智能（Artificial Intelligence，AI）是计算机科学的一个重要分支，
它致力于创建能够模拟、延伸和扩展人类智能的理论、方法、技术和应用系统。

机器学习（Machine Learning）是人工智能的一个核心子领域。
它通过算法让计算机从数据中学习，从而在没有显式编程的情况下做出决策或预测。

深度学习（Deep Learning）是机器学习的一种特殊形式，基于人工神经网络。
它在图像识别、自然语言处理、语音识别等领域取得了突破性进展。

自然语言处理（Natural Language Processing，NLP）是AI的重要应用领域，
涉及计算机与人类语言的交互，包括文本分析、机器翻译、情感分析等。

计算机视觉（Computer Vision）使机器能够从图像或视频中获取信息，
在人脸识别、自动驾驶、医疗影像等方面有广泛应用。
"""

    with open(test_doc_path, 'w', encoding='utf-8') as f:
        f.write(test_content)

    print(f"测试文档已创建: {test_doc_path}")
    return test_doc_path


def test_text_processing():
    """测试文本处理流程"""
    print("\n" + "=" * 60)
    print("测试 1: 文本切块")
    print("=" * 60)

    from src.parsers.pdf_parser import DocumentChunk

    # 创建测试文档
    test_doc = DocumentChunk(
        content="人工智能是计算机科学的重要分支。机器学习是AI的核心技术。深度学习基于神经网络。自然语言处理涉及文本和语言。",
        metadata={'test': True},
        page_num=1,
        chunk_id="test_doc"
    )

    # 切块
    chunker = TextChunker(chunk_size=20, chunk_overlap=5)
    chunks = chunker.chunk_documents([test_doc])

    print(f"[OK] 切块完成，生成 {len(chunks)} 个块")
    for i, chunk in enumerate(chunks):
        print(f"  块 {i+1} ({chunk.token_count} tokens): {chunk.content[:30]}...")


def test_embedding_generation():
    """测试向量化"""
    print("\n" + "=" * 60)
    print("测试 2: 向量化")
    print("=" * 60)

    from src.chunkers.text_chunker import TextChunk

    # 创建测试文本块
    test_chunks = [
        TextChunk(
            content="人工智能技术正在改变世界。",
            metadata={'test': True},
            chunk_index=0,
            chunk_id="test_0",
            token_count=10
        ),
        TextChunk(
            content="机器学习让计算机能够学习。",
            metadata={'test': True},
            chunk_index=1,
            chunk_id="test_1",
            token_count=8
        )
    ]

    # 生成嵌入
    generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    embedding_result = generator.generate_embeddings(test_chunks)

    print(f"[OK] 嵌入生成完成")
    print(f"  模型: {embedding_result.model_name}")
    print(f"  嵌入维度: {embedding_result.embedding_dim}")
    print(f"  文本块数量: {len(embedding_result.chunks)}")


def test_vector_storage():
    """测试向量存储和检索"""
    print("\n" + "=" * 60)
    print("测试 3: 向量存储和检索")
    print("=" * 60)

    from src.chunkers.text_chunker import TextChunk

    # 创建测试数据
    test_chunks = [
        TextChunk(
            content="Python是一种流行的编程语言。",
            metadata={'category': 'programming'},
            chunk_index=0,
            chunk_id="test_0",
            token_count=8
        ),
        TextChunk(
            content="深度学习基于神经网络技术。",
            metadata={'category': 'ai'},
            chunk_index=1,
            chunk_id="test_1",
            token_count=8
        ),
        TextChunk(
            content="今天天气不错，适合出门。",
            metadata={'category': 'life'},
            chunk_index=2,
            chunk_id="test_2",
            token_count=8
        )
    ]

    # 生成嵌入
    generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    embedding_result = generator.generate_embeddings(test_chunks)

    # 创建向量存储
    store = VectorStore(index_type="flat", metric="cosine")
    store.add_embeddings(embedding_result)

    # 测试检索
    query = "深度学习的原理是什么？"
    query_embedding = generator.generate_embedding(query)
    results = store.search(query_embedding, k=2)

    print(f"[OK] 向量存储完成")
    print(f"  存储向量数量: {len(test_chunks)}")

    print(f"\n查询: {query}")
    print("检索结果:")
    for i, (chunk, similarity) in enumerate(results):
        print(f"  {i+1}. [{similarity:.4f}] {chunk.content}")

    # 显示统计信息
    stats = store.get_statistics()
    print(f"\n统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def test_complete_pipeline():
    """测试完整的离线流程"""
    print("\n" + "=" * 60)
    print("测试 4: 完整离线流程")
    print("=" * 60)

    # 创建测试文档
    test_doc_path = create_test_document()

    # 这里需要实现简单的文本读取器，因为我们用TXT文档而不是PDF
    class SimpleTXTParser:
        def parse_txt(self, txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()

            from src.parsers.pdf_parser import DocumentChunk
            return [DocumentChunk(
                content=content,
                metadata={'source': txt_path},
                page_num=1,
                chunk_id=f"{os.path.basename(txt_path)}_1"
            )]

    try:
        # 解析文档
        txt_parser = SimpleTXTParser()
        doc_chunks = txt_parser.parse_txt(test_doc_path)
        print(f"[OK] 文档解析完成")

        # 切块
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text_chunks = chunker.chunk_documents(doc_chunks)
        print(f"[OK] 文本切块完成，生成 {len(text_chunks)} 个块")

        # 向量化
        generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        embedding_result = generator.generate_embeddings(text_chunks)
        print(f"[OK] 向量化完成，维度: {embedding_result.embedding_dim}")

        # 存储
        store = VectorStore(index_type="flat", metric="cosine")
        store.add_embeddings(embedding_result)
        print(f"[OK] 向量存储完成")

        # 测试检索
        query = "什么是深度学习？"
        query_embedding = generator.generate_embedding(query)
        results = store.search(query_embedding, k=2)

        print(f"\n查询: {query}")
        print("检索结果:")
        for i, (chunk, similarity) in enumerate(results):
            print(f"  {i+1}. [{similarity:.4f}] {chunk.content[:60]}...")

        print(f"\n[OK] 完整流程测试成功！")

    except Exception as e:
        print(f"[ERROR] 流程测试失败: {str(e)}")


def main():
    """主函数"""
    print("RAG系统功能测试")
    print("=" * 60)

    try:
        # 运行各个测试
        test_text_processing()
        test_embedding_generation()
        test_vector_storage()
        test_complete_pipeline()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()