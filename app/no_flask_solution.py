"""
不依赖Flask的RAG API服务器
使用Python内置http.server提供静态文件服务
"""
import os
import sys
import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

# RAG API接口数据（模拟）
RAG_RESPONSES = {
    '巴洛克': '根据参考文档，巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。代表作曲家有巴赫、亨德尔等。',
    '古典主义': '根据参考文档，古典主义音乐时期从1750年到1820年，以海顿、莫扎特、贝多芬为代表。这个时期音乐更加理性、均衡，确立了交响曲、奏鸣曲等音乐体裁。',
    '浪漫主义': '根据参考文档，浪漫主义音乐时期从1820年到1900年，强调个人情感的表达。浪漫主义音乐注重主观情感的抒发，和声更加丰富，节奏更加自由。',
    '现代主义': '根据参考文档，现代主义音乐时期从1900年至今，多元化发展，突破传统和声与调性。代表人物：德彪西、斯特拉文斯基。'
}

class RAGRequestHandler(SimpleHTTPRequestHandler):
    """简单的RAG请求处理器"""

    def do_GET(self):
        if self.path == '/' or self.path == '/api/health':
            self.send_json_response(200, {
                'status': 'ok' if self.path == '/' else 'healthy',
                'message': 'RAG API服务运行正常',
                'server': 'Python http.server',
                'version': '1.0.0'
            })
        else:
            self.send_json_response(404, {
                'success': False,
                'error': '路径不存在'
            })

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            try:
                post_data = self.rfile.read(content_length).decode('utf-8')
                request_data = json.loads(post_data)

                query = request_data.get('query', '').strip()
                period = request_data.get('period', 'all')

                if query:
                    answer = self._get_answer(query, period)
                    self.send_response(200, {
                        'success': True,
                        'answer': answer,
                        'period': period,
                        'retrieved_docs': self._get_mock_retrieved_docs(period),
                        'ai_generated': False,
                        'model': 'mock',
                        'timestamp': self._get_timestamp()
                    })
                else:
                    self.send_response(400, {
                        'success': False,
                        'error': '查询不能为空'
                    })
            except Exception as e:
                self.send_response(500, {
                    'success': False,
                    'error': f'处理请求时出错: {str(e)}'
                })
        else:
            self.send_response(400, {
                'success': False,
                'error': '请求体为空'
            })

    def send_json_response(self, status_code, data):
        """发送JSON响应"""
        response_data = json.dumps(data, ensure_ascii=False)
        # 调用父类方法发送状态码
        super().send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_data.encode('utf-8'))

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_json_response(200, {'status': 'ok'})

    def _get_answer(self, query, period):
        """根据查询和时期返回答案"""
        # 如果指定了时期，使用特定答案
        if period != 'all' and period in RAG_RESPONSES:
            base_answer = RAG_RESPONSES[period]
            if query and any(keyword in query.lower() for keyword in ['巴洛克', '古典', '浪漫', '现代', '文艺复兴', '中世纪']):
                return base_answer

        # 模拟的检索过程
        if '巴洛克' in query or any(kw in query for kw in ['华丽', '装饰', '通奏低音', '巴赫', '亨德尔']):
            return RAG_RESPONSES['巴洛克']
        elif '古典主义' in query or any(kw in query for kw in ['海顿', '莫扎特', '贝多芬', '交响曲', '奏鸣曲']):
            return RAG_RESPONSES['古典主义']
        elif '浪漫主义' in query or any(kw in query for kw in ['肖邦', '李斯特', '瓦格纳', '情感', '自由']):
            return RAG_RESPONSES['浪漫主义']
        elif '现代主义' in query or any(kw in query for kw in ['德彪西', '斯特拉文', '多元化', '突破', '现代']):
            return RAG_RESPONSES['现代主义']
        elif '文艺复兴' in query or any(kw in query for kw in ['文艺复兴', '帕莱斯特里纳', '人文', '复调']):
            return f"根据参考文档，关于{query}的问题，文艺复兴时期（1400-1600年）音乐以人文主义为特色，强调和声和旋律的和谐。"
        elif '中世纪' in query or any(kw in query for kw in ['宗教', '单声部', '格列高特']):
            return f"根据参考文档，关于{query}的问题，中世纪音乐（500-1400年）以宗教音乐为主，格列高利圣歌是其典型代表。"
        else:
            # 通用答案
            return f"根据参考文档，关于{query}的问题，可以在系统中查询相关历史时期的详细信息。西方音乐史涵盖了从5世纪到现代的主要音乐发展历程，每个时期都有其独特的风格特征和代表人物。"

    def _get_mock_retrieved_docs(self, period):
        """获取模拟的检索文档"""
        if period == 'baroque' or period == '巴洛克':
            return [
                {'content': '巴洛克音乐大约在1600年至1750年间，以复调音乐为主。', 'similarity': 0.89},
                {'content': '巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。', 'similarity': 0.85}
            ]
        elif period == 'classical' or period == '古典主义':
            return [
                {'content': '古典主义音乐时期从1750年到1820年，以海顿、莫扎特、贝多芬为代表。这个时期音乐更加理性、均衡，确立了交响曲、奏鸣曲等音乐体裁。', 'similarity': 0.91}
            ]
        elif period == 'romantic' or period == '浪漫主义':
            return [
                {'content': '浪漫主义音乐时期从1820年到1900年，强调个人情感的表达。浪漫主义音乐注重主观情感的抒发，和声更加丰富，节奏更加自由。', 'similarity': 0.88}
            ]
        elif period == 'modern' or period == '现代主义':
            return [
                {'content': '现代主义音乐时期从1900年至今，多元化发展，突破传统和声与调性。代表人物：德彪西、斯特拉文斯基。', 'similarity': 0.87}
            ]
        elif period != 'all':
            return [
                {'content': f'关于{period}时期的音乐历史信息。', 'similarity': 0.85}
            ]
        else:
            return []

    def _get_timestamp(self):
        """获取当前时间戳"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

def find_available_port():
    """查找可用的端口"""
    for port in [8000, 8080, 5000, 5001]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('127.0.0.1', port))
                s.close()
                return port
        except OSError:
            continue
    return None

def main():
    print("=" * 60)
    print("西方音乐史RAG系统 - 无Flask依赖版本")
    print("=" * 60)
    print()

    # 查找可用端口
    print("正在查找可用端口...")
    port = find_available_port()
    if port:
        print(f"使用端口: {port}")
    else:
        print("警告：没有找到可用端口，尝试使用8000端口")
        port = 8000

    # 启动HTTP服务器
    server_address = ('127.0.0.1', port)
    print(f"启动HTTP服务器在 {server_address}")

    try:
        httpd = HTTPServer(server_address, RAGRequestHandler)
        print(f"服务器启动成功！")
        print()
        print("=" * 60)
        print("服务信息:")
        print(f"  前端页面: file:///E:/ai-apps/rag-system/app/index.html")
        print(f"  API接口: http://127.0.0.1:{port}/api/query")
        print(f"  健康检查: http://127.0.0.1:{port}/api/health")
        print()
        print("按Ctrl+C停止服务器")
        print("=" * 60)
        print()

        httpd.serve_forever()

    except OSError as e:
        print(f"服务器启动失败: {e}")
        print(f"原因: {str(e)}")
        print()
        print("解决方案:")
        print("1. 检查端口是否被其他程序占用")
        print("2. 确认Python环境正常")
        print("3. 直接在浏览器中打开前端文件，不依赖后端API")
        input("按回车键退出...")

if __name__ == "__main__":
    main()