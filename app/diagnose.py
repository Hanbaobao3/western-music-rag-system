"""
系统诊断和修复脚本
"""
import socket
import subprocess
import sys
import requests

def check_port_usage(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
        return result == 0  # 0表示端口可用
    except Exception as e:
        print(f"端口检查失败: {e}")
        return False

def test_flask_import():
    """测试Flask导入"""
    try:
        import flask
        return True, "Flask版本正常"
    except ImportError as e:
        return False, f"Flask导入失败: {str(e)}"

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get('http://127.0.0.1:5001/api/health', timeout=5)
        return response.status_code == 200, f"健康检查正常"
    except Exception as e:
        return False, f"API连接失败: {str(e)}"

def test_query_endpoint():
    """测试查询接口"""
    try:
        response = requests.post(
            'http://127.0.0.1:5001/api/query',
            json={"query": "巴洛克音乐", "period": "baroque", "use_ai": False},
            timeout=5
        )
        return response.status_code == 200, f"查询接口正常"
    except Exception as e:
        return False, f"查询接口失败: {str(e)}"

def kill_existing_processes():
    """停止可能存在的Flask进程"""
    try:
        # Windows上停止python进程
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], check=True)
        print("已尝试停止Python进程")
    except Exception as e:
        print(f"停止进程失败: {e}")

def main():
    print("=" * 60)
    print("西方音乐史RAG系统 - 诊断和修复")
    print("=" * 60)
    print()

    # 1. 检查Flask导入
    print("[1/5] 检查Flask导入...")
    flask_ok, msg = test_flask_import()
    print(f"结果: {msg}")

    if not flask_ok:
        print()
        print("正在尝试安装Flask...")
        import subprocess
        subprocess.run(['pip', 'install', 'flask', 'flask-cors'], check=True)
        print()

    # 2. 检查端口占用
    print()
    print("[2/5] 检查端口占用...")
    ports = [5000, 5001]
    for port in ports:
        if check_port_usage(port):
            print(f"  端口 {port} 被占用")
        else:
            print(f"  端口 {port} 可用")

    # 3. 测试API连接
    print()
    print("[3/5] 测试API连接...")
    api_ok = test_api_connection()
    print(f"结果: {api_ok}")

    if api_ok:
        print("[4/5] 测试查询接口...")
        query_ok = test_query_endpoint()
        print(f"结果: {query_ok}")
    else:
        print("[4/5] 跳过查询接口测试")

    # 4. 停止可能冲突的进程
    print()
    print("[4/5] 停止可能冲突的Python进程...")
    kill_existing_processes()

    print()
    print("=" * 60)
    print("诊断完成！")
    print("=" * 60)
    print()
    print("建议解决方案:")
    print("1. 使用简化版本服务器 (simple_server.py)")
    print("2. 或手动检查Flask模块安装")
    print("3. 确认5000端口没有被其他程序占用")
    print()

    input("按回车键退出...")
    input()