"""
简化的Flask服务器，解决模块导入问题
"""
import os
import sys

# 尝试多种方式导入Flask
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    try:
        import flask
        Flask = flask.Flask
        from flask import request, jsonify
        FLASK_AVAILABLE = True
    except ImportError:
        FLASK_AVAILABLE = False
        print("Flask模块不可用，尝试安装...")

if not FLASK_AVAILABLE:
    print("正在安装Flask...")
    os.system("pip install flask flask-cors")

# 创建简单的Flask应用
app = Flask(__name__)

# 内存存储（用于调试）
mock_data = {
    'answers': {
        '巴洛克': '根据参考文档，巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。代表作曲家有巴赫、亨德尔等。',
        '古典主义': '根据参考文档，古典主义音乐时期从1750年到1820年，以海顿、莫扎特、贝多芬为代表。这个时期音乐更加理性、均衡，确立了交响曲、奏鸣曲等音乐体裁。',
        '浪漫主义': '根据参考文档，浪漫主义音乐时期从1820年到1900年，强调个人情感的表达。浪漫主义音乐注重主观情感的抒发，和声更加丰富，节奏更加自由。'
    }
}

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'server': 'Flask简单模式',
        'timestamp': '2026-04-29',
        'version': '1.0.0'
    })

@app.route('/api/query', methods=['POST'])
def query():
    """查询接口"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        period = data.get('period', 'all')
        use_ai = data.get('use_ai', False)

        if not query:
            return jsonify({
                'success': False,
                'error': '查询不能为空'
            }), 400

        print(f"收到查询: query='{query}', period='{period}', use_ai={use_ai}")

        # 使用mock数据
        if use_ai:
            answer = f"【AI增强回答】基于{period}时期的音乐知识，我来回答你的问题：{query}"
        else:
            # 根据查询关键词返回相关答案
            answer = mock_data['answers'].get('baroque', mock_data['answers']['巴洛克'])

        return jsonify({
            'success': True,
            'answer': answer,
            'retrieved_docs': [
                {'content': '巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。', 'similarity': 0.89},
                {'content': '巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。', 'similarity': 0.85}
            ],
            'period': period,
            'ai_generated': use_ai,
            'model': 'claude-3-5-sonnet-20241022' if use_ai else 'mock',
            'timestamp': '2026-04-29'
        })

    except Exception as e:
        print(f"查询接口错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("西方音乐史RAG系统 - 简化服务器")
    print("=" * 60)
    print()
    print("服务器信息:")
    print("  地址: http://127.0.0.1:5001")
    print("  健康检查: http://127.0.0.1:5001/api/health")
    print("  查询接口: http://127.0.0.1:5001/api/query")
    print()
    if FLASK_AVAILABLE:
        print("  状态: Flask模块可用")
    else:
        print("  状态: Flask模块不可用")
    print()
    print("正在启动服务器...")
    print("=" * 60)

    try:
        app.run(host='127.0.0.1', port=5001, debug=False)
    except Exception as e:
        print(f"服务器启动失败: {str(e)}")
        input("按回车键退出...")
