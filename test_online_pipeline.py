"""
在线流程集成测试
测试检索、Prompt组装、答案生成的完整流程
"""
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.online_pipeline import OnlinePipeline


def test_single_query():
    """测试单次查询"""
    print("=" * 60)
    print("测试 1: 单次查询")
    print("=" * 60)

    try:
        # 创建在线查询流程
        pipeline = OnlinePipeline(
            vector_store_path="processed/vector_store",
            config_path="config/config.yaml"
        )

        # 测试问题列表
        test_questions = [
            "巴洛克音乐有什么特点？",
            "古典主义时期的代表作曲家有哪些？",
            "浪漫主义音乐时期的特征是什么？"
        ]

        for i, question in enumerate(test_questions, 1):
            print(f"\n【问题 {i}】")
            print(f"问题: {question}")
            print("正在处理...")

            # 执行查询
            result = pipeline.query(question)

            # 显示结果
            print(f"\n答案: {result['answer']}")
            print(f"状态: {'成功' if result['success'] else '失败'}")

            if result['success']:
                print(f"检索文档数: {len(result['retrieved_docs'])}")

                # 显示最相关的文档片段
                if result['retrieved_docs']:
                    print(f"最相关文档 (相似度: {result['retrieved_docs'][0]['similarity']:.4f}):")
                    print(f"  {result['retrieved_docs'][0]['content'][:100]}...")

            print("-" * 40)

        print("\n测试 1 完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_pipeline_components():
    """测试各个组件的衔接"""
    print("\n" + "=" * 60)
    print("测试 2: 组件衔接测试")
    print("=" * 60)

    try:
        from src.embeddings.embedding_generator import EmbeddingGenerator
        from src.storage.vector_store import VectorStore
        from src.retriever.document_retriever import DocumentRetriever
        from src.generator.prompt_assembler import PromptAssembler
        from src.generator.answer_generator import AnswerGenerator

        print("步骤 1: 初始化嵌入生成器")
        embedding_generator = EmbeddingGenerator()
        print("  [OK] 嵌入生成器初始化完成")

        print("\n步骤 2: 加载向量存储")
        vector_store = VectorStore()
        vector_store.load("processed/vector_store")
        print(f"  [OK] 向量存储加载完成，包含 {len(vector_store.chunks)} 个向量")

        print("\n步骤 3: 创建文档检索器")
        retriever = DocumentRetriever(
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            top_k=3
        )
        print("  [OK] 文档检索器创建完成")

        print("\n步骤 4: 创建Prompt组装器")
        prompt_assembler = PromptAssembler()
        print("  [OK] Prompt组装器创建完成")

        print("\n步骤 5: 创建答案生成器")
        answer_generator = AnswerGenerator(llm_provider='mock')
        print("  [OK] 答案生成器创建完成")

        # 测试完整流程
        test_query = "西方音乐史的主要时期有哪些？"

        print(f"\n步骤 6: 测试完整查询流程")
        print(f"  查询: {test_query}")

        # 检索
        print("  6.1 执行检索...")
        retrieved_docs = retriever.retrieve(test_query)
        print(f"  [OK] 检索到 {len(retrieved_docs)} 个文档")

        # Prompt组装
        print("  6.2 组装Prompt...")
        prompt = prompt_assembler.assemble_prompt(test_query, retrieved_docs)
        print(f"  [OK] Prompt组装完成，长度: {len(prompt)}")

        # 答案生成
        print("  6.3 生成答案...")
        answer = answer_generator.generate_answer(prompt)
        print(f"  [OK] 答案生成完成，长度: {len(answer)}")

        print(f"\n最终答案:")
        print(f"  {answer}")

        print("\n测试 2 完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_batch_query():
    """测试批量查询"""
    print("\n" + "=" * 60)
    print("测试 3: 批量查询")
    print("=" * 60)

    try:
        # 创建在线查询流程
        pipeline = OnlinePipeline(
            vector_store_path="processed/vector_store",
            config_path="config/config.yaml"
        )

        # 测试问题
        test_questions = [
            "什么是巴洛克音乐？",
            "海顿属于哪个时期？",
            "贝多芬的音乐风格特点"
        ]

        print(f"批量查询 {len(test_questions)} 个问题\n")

        results = pipeline.batch_query(test_questions)

        # 显示结果
        for i, (question, result) in enumerate(zip(test_questions, results), 1):
            print(f"问题 {i}: {question}")
            print(f"答案: {result['answer'][:80]}...")
            print(f"状态: {'成功' if result['success'] else '失败'}")
            print()

        success_count = sum(1 for r in results if r['success'])
        print(f"批量查询完成: {success_count}/{len(results)} 成功")

        print("\n测试 3 完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 4: 错误处理")
    print("=" * 60)

    try:
        pipeline = OnlinePipeline(
            vector_store_path="processed/vector_store",
            config_path="config/config.yaml"
        )

        # 测试1: 空查询
        print("测试 4.1: 空查询")
        result = pipeline.query("")
        print(f"  结果: {result['success']}")
        print(f"  答案: {result['answer'][:50]}...")

        # 测试2: 不相关查询
        print("\n测试 4.2: 不相关查询")
        result = pipeline.query("如何制作披萨？")
        print(f"  结果: {result['success']}")
        print(f"  答案: {result['answer'][:80]}...")

        # 测试3: 模糊查询
        print("\n测试 4.3: 模糊查询")
        result = pipeline.query("音乐")
        print(f"  结果: {result['success']}")
        print(f"  检索文档数: {len(result['retrieved_docs'])}")

        print("\n测试 4 完成！")

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数"""
    print("RAG系统在线流程集成测试")
    print("=" * 60)

    try:
        # 检查向量存储是否存在
        if not os.path.exists("processed/vector_store.index"):
            print("错误: 向量存储文件不存在！")
            print("请先运行离线处理流程: python src/offline_pipeline.py")
            return

        # 运行各个测试
        test_single_query()
        test_pipeline_components()
        test_batch_query()
        test_error_handling()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()