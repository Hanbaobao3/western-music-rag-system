"""
简化的API测试客户端
"""
import requests
import json
import sys

# API配置
API_BASE_URL = "http://127.0.0.1:5001"

def test_health_check():
    """测试健康检查"""
    print("=" * 50)
    print("测试1：健康检查")
    print("=" * 50)

    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_query_without_ai():
    """测试查询（不使用AI）"""
    print("=" * 50)
    print("测试2：基础查询（不使用AI）")
    print("=" * 50)

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={
                "query": "什么是巴洛克音乐",
                "period": "baroque",
                "use_ai": False
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"解析结果:")
            print(f"  成功: {data.get('success', False)}")
            print(f"  答案: {data.get('answer', '')[:50]}...")
            print(f"  检索文档数: {len(data.get('retrieved_docs', []))}")
            print(f"   AI生成: {data.get('ai_generated', False)}")
            return True
        else:
            print(f"HTTP错误: {response.status_code}")
            return False

    except Exception as e:
        print(f"查询失败: {e}")
        return False

def test_query_with_ai():
    """测试查询（使用AI）"""
    print("=" * 50)
    print("测试3：AI增强查询")
    print("=" * 50)

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query",
            json={
                "query": "什么是古典主义音乐",
                "period": "classical",
                "use_ai": True
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"解析结果:")
            print(f"  成功: {data.get('success', False)}")
            print(f"  答案: {data.get('answer', '')[:50]}...")
            print(f"  检索文档数: {len(data.get('retrieved_docs', []))}")
            print(f"  AI生成: {data.get('ai_generated', False)}")
            print(f"  模型: {data.get('model', '')}")
            return True
        else:
            print(f"HTTP错误: {response.status_code}")
            return False

    except Exception as e:
        print(f"查询失败: {e}")
        return False

def main():
    print("西方音乐史RAG系统 - API测试客户端")
    print("=" * 60)
    print()

    # 运行测试
    health_ok = test_health_check()
    print()

    if health_ok:
        basic_ok = test_query_without_ai()
        print()

        if basic_ok:
            ai_ok = test_query_with_ai()
            print()

            if ai_ok:
                print("=" * 50)
                print("所有测试通过！API工作正常")
                print("=" * 50)
                print()
                print("现在可以在浏览器中正常使用对话功能了")
            else:
                print("AI查询失败，但基础查询正常")
    else:
        print("健康检查失败，请检查服务器")

if __name__ == "__main__":
    input("按回车键退出...")
    input()