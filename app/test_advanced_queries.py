"""
测试高级RAG系统的问答功能
"""
import urllib.request
import urllib.parse
import json

# 测试不同的查询 - 涵盖不同问题类型
test_queries = [
    ("名词解释", "什么是通奏低音？"),
    ("简答题", "巴洛克音乐的主要特征有哪些？"),
    ("论述题", "古典主义音乐的发展历程如何？"),
    ("综合", "格里高利圣咏的特点是什么"),
    ("具体知识点", "巴赫的主要作品有哪些？"),
    ("比较分析", "文艺复兴与巴洛克音乐的区别是什么？")
]

print("=" * 70)
print("高级RAG系统测试")
print("=" * 70)
print()

for query_type, query in test_queries:
    print(f"查询类型: {query_type}")
    print(f"查询问题: {query}")
    print("-" * 70)

    try:
        data = json.dumps({'query': query}).encode('utf-8')
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/query',
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

            print(f"[OK] 状态: {'成功' if result.get('success') else '失败'}")
            print(f"[OK] 检索时期: {result.get('period', '未知')}")
            print(f"[OK] 题目类型: {result.get('question_type', '未知')}")
            print(f"[OK] 检索块数: {result.get('retrieved_chunks_count', 0)}")
            print(f"[OK] 相似度得分: {result.get('best_chunk_score', 0):.2f}")

            answer = result.get('answer', '')
            print(f"[OK] 答案长度: {len(answer)} 字符")
            print(f"[OK] 答案预览:")
            print(answer[:200] + "..." if len(answer) > 200 else answer)
            print()

    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        print()

    print("=" * 70)
    print()

print("测试完成")
print("=" * 70)
