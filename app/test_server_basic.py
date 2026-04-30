"""
使用内置模块测试服务器功能
"""
import urllib.request
import urllib.parse
import json

def test_server():
    """测试服务器功能"""
    base_url = "http://127.0.0.1:5001"

    print("=" * 50)
    print("开始测试Flask-free服务器（基础版）")
    print("=" * 50)
    print()

    # 测试1: 健康检查
    print("[测试1] 健康检查...")
    try:
        req = urllib.request.Request(f"{base_url}/api/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✓ 健康检查成功: {data}")
            else:
                print(f"✗ 健康检查失败: 状态码 {response.status}")
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        print("  提示：请先启动服务器: python no_flask_solution.py")
    print()

    # 测试2: 基本查询
    print("[测试2] 基本查询（巴洛克音乐）...")
    try:
        query_data = {
            "query": "介绍一下巴洛克音乐的特点",
            "period": "baroque",
            "use_ai": False
        }

        req = urllib.request.Request(
            f"{base_url}/api/query",
            data=json.dumps(query_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✓ 查询成功")
                print(f"  答案: {data.get('answer', '')[:100]}...")
                print(f"  时期: {data.get('period')}")
                print(f"  AI生成: {data.get('ai_generated')}")
            else:
                print(f"✗ 查询失败: 状态码 {response.status}")
    except Exception as e:
        print(f"✗ 查询异常: {e}")
    print()

    # 测试3: 古典主义查询
    print("[测试3] 古典主义查询...")
    try:
        query_data = {
            "query": "海顿、莫扎特、贝多芬的音乐特点",
            "period": "classical",
            "use_ai": False
        }

        req = urllib.request.Request(
            f"{base_url}/api/query",
            data=json.dumps(query_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✓ 古典主义查询成功")
                print(f"  答案: {data.get('answer', '')[:100]}...")
            else:
                print(f"✗ 查询失败: 状态码 {response.status}")
    except Exception as e:
        print(f"✗ 查询异常: {e}")
    print()

    # 测试4: 错误处理
    print("[测试4] 错误处理（空查询）...")
    try:
        query_data = {
            "query": "",
            "period": "all"
        }

        req = urllib.request.Request(
            f"{base_url}/api/query",
            data=json.dumps(query_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 400:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✓ 错误处理正确")
                print(f"  错误信息: {data.get('error')}")
            else:
                print(f"✗ 错误处理异常: 状态码 {response.status}")
    except Exception as e:
        print(f"✗ 错误处理测试异常: {e}")
    print()

    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
    print()
    print("如果测试显示 '健康检查异常'，请先启动服务器：")
    print("  python no_flask_solution.py")
    print()
    print("启动服务器后，可以：")
    print("1. 在浏览器中打开: file:///E:/ai-apps/rag-system/app/index.html")
    print("2. 测试对话功能")

if __name__ == "__main__":
    test_server()
