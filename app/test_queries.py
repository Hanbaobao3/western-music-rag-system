"""
测试RAG系统的问答功能
"""
import urllib.request
import urllib.parse
import json

# 测试不同的查询
test_queries = [
    "中世纪音乐的特点",
    "巴洛克音乐的主要特征",
    "古典主义音乐的发展",
    "格里高利圣咏是什么",
    "什么是通奏低音"
]

print("=" * 60)
print("西方音乐史RAG系统测试")
print("=" * 60)
print()

for query in test_queries:
    print(f"查询: {query}")
    print("-" * 60)

    try:
        data = json.dumps({'query': query}).encode('utf-8')
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/query',
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))

            print(f"状态: {'成功' if result.get('success') else '失败'}")
            print(f"识别时期: {result.get('period', '未知')}")
            print(f"题目类型: {result.get('question_type', '未知')}")
            print(f"答案预览: {result.get('answer', '')[:100]}...")
            print()

    except Exception as e:
        print(f"请求失败: {e}")
        print()

print("=" * 60)
print("测试完成")
print("=" * 60)
