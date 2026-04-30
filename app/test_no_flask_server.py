"""
测试Flask-free服务器功能
"""
import requests
import json
import time

def test_server():
    """测试服务器各项功能"""
    base_url = "http://127.0.0.1:5001"

    print("=" * 50)
    print("开始测试Flask-free服务器")
    print("=" * 50)
    print()

    # 测试1: 健康检查
    print("[测试1] 健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 健康检查成功: {data}")
        else:
            print(f"✗ 健康检查失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
    print()

    # 测试2: 基本查询
    print("[测试2] 基本查询（巴洛克音乐）...")
    try:
        query_data = {
            "query": "介绍一下巴洛克音乐的特点",
            "period": "baroque",
            "use_ai": False
        }
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 查询成功")
            print(f"  答案: {data.get('answer', '')[:100]}...")
            print(f"  时期: {data.get('period')}")
            print(f"  AI生成: {data.get('ai_generated')}")
        else:
            print(f"✗ 查询失败: 状态码 {response.status_code}")
            print(f"  响应: {response.text}")
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
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 古典主义查询成功")
            print(f"  答案: {data.get('answer', '')[:100]}...")
        else:
            print(f"✗ 查询失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"✗ 查询异常: {e}")
    print()

    # 测试4: 浪漫主义查询
    print("[测试4] 浪漫主义查询...")
    try:
        query_data = {
            "query": "肖邦和李斯特的音乐风格",
            "period": "romantic",
            "use_ai": False
        }
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 浪漫主义查询成功")
            print(f"  答案: {data.get('answer', '')[:100]}...")
        else:
            print(f"✗ 查询失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"✗ 查询异常: {e}")
    print()

    # 测试5: 通用查询（自动时期识别）
    print("[测试5] 通用查询（自动时期识别）...")
    try:
        query_data = {
            "query": "德彪西和斯特拉文斯基的音乐",
            "period": "all",
            "use_ai": False
        }
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 自动识别查询成功")
            print(f"  时期: {data.get('period')}")
            print(f"  答案: {data.get('answer', '')[:100]}...")
        else:
            print(f"✗ 查询失败: 状态码 {response.status_code}")
    except Exception as e:
        print(f"✗ 查询异常: {e}")
    print()

    # 测试6: 错误处理
    print("[测试6] 错误处理（空查询）...")
    try:
        query_data = {
            "query": "",
            "period": "all"
        }
        response = requests.post(f"{base_url}/api/query", json=query_data, timeout=5)
        if response.status_code == 400:
            data = response.json()
            print(f"✓ 错误处理正确")
            print(f"  错误信息: {data.get('error')}")
        else:
            print(f"✗ 错误处理异常: 状态码 {response.status_code}")
    except Exception as e:
        print(f"✗ 错误处理测试异常: {e}")
    print()

    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
    print()
    print("如果所有测试都显示 ✓，说明服务器工作正常。")
    print("现在可以在浏览器中打开前端页面测试对话功能。")

if __name__ == "__main__":
    test_server()
