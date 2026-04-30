"""
测试贝多芬查询的简化版本
"""
import sys
sys.path.append('/e/ai-apps/rag-system/app')

try:
    from advanced_music_server import (
        load_and_chunk_knowledge,
        intelligent_retrieve,
        analyze_query_intent,
        select_best_chunk,
        generate_targeted_answer,
        classify_question_type
    )

    print("模块导入成功")

    # 加载知识库
    print("正在加载知识库...")
    knowledge_chunks = load_and_chunk_knowledge()
    print(f"加载了 {len(knowledge_chunks)} 个知识块")

    # 测试贝多芬查询
    query = "贝多芬"
    print(f"\n测试查询: {query}")

    # 分析查询意图
    intent = analyze_query_intent(query)
    print(f"查询意图: {intent}")

    # 智能检索
    relevant_chunks = intelligent_retrieve(query, knowledge_chunks)
    print(f"找到 {len(relevant_chunks)} 个相关块")

    # 选择最佳块
    best_chunk = select_best_chunk(query, relevant_chunks, intent)
    if best_chunk:
        print(f"最佳块预览: {best_chunk.content[:100]}...")

    # 分类问题类型
    question_type = classify_question_type(query)
    print(f"问题类型: {question_type}")

    # 生成答案
    answer = generate_targeted_answer(query, relevant_chunks, question_type)
    print(f"\n生成的答案:\n{answer}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
