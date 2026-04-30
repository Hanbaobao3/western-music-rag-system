"""
西方音乐史RAG问答系统 - 简单AI增强版本
"""
import json
import os
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

# Z.ai API配置
ZAI_API_KEY = "213f38c105744112a8d3a518d8a4f10b.5Z9oqAY7LInlIpcC"
ZAI_API_BASE = "https://api.z.ai/api/anthropic"
ZAI_MODEL = "claude-sonnet-4-20250514"

# 知识库数据路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
KNOWLEDGE_FILES = [
    os.path.join(DATA_DIR, 'music history.txt'),
    os.path.join(DATA_DIR, 'music history 2.txt')
]

class KnowledgeChunk:
    """知识块类 - 用于细粒度检索"""
    def __init__(self, content, keywords=None, section=None, importance=0):
        self.content = content
        self.keywords = keywords or []
        self.section = section
        self.importance = importance
        self.similarity_score = 0

def load_and_chunk_knowledge():
    """加载并细粒度切块知识库"""
    chunks = []

    print(f"[INFO] 开始加载知识库...")
    print(f"[INFO] 数据目录: {DATA_DIR}")

    for file_path in KNOWLEDGE_FILES:
        if not os.path.exists(file_path):
            print(f"[WARNING] 文件不存在: {file_path}")
            continue

        print(f"[INFO] 正在读取文件: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"[INFO] 文件大小: {len(content)} 字符")

            # 简化的文本切块
            lines = content.split('\n')
            current_chunk = []
            chunk_keywords = []

            for line in lines:
                line_stripped = line.strip()

                # 检测章节标题
                if line_stripped and (line_stripped.startswith('#') or re.match(r'^[一二三四五六七八九十]+[、．.]', line_stripped)):
                    # 保存当前块
                    if current_chunk:
                        chunk_text = '\n'.join(current_chunk).strip()
                        if chunk_text and len(chunk_text) > 50:
                            chunk = KnowledgeChunk(chunk_text, chunk_keywords, None, importance=0)
                            chunks.append(chunk)

                    # 开始新章节
                    current_chunk = []
                    chunk_keywords = []
                else:
                    # 收集当前行到当前块中
                    if line_stripped or current_chunk:
                        current_chunk.append(line)

                        # 如果块足够大，创建新块
                        if len(current_chunk) > 15:
                            chunk_text = '\n'.join(current_chunk).strip()
                            if chunk_text and len(chunk_text) > 50:
                                chunk = KnowledgeChunk(chunk_text, chunk_keywords, None, importance=0)
                                chunks.append(chunk)
                            current_chunk = []

            # 处理最后一个块
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text and len(chunk_text) > 50:
                    chunk = KnowledgeChunk(chunk_text, chunk_keywords, None, importance=0)
                    chunks.append(chunk)

        except Exception as e:
            print(f"[ERROR] 处理文件 {file_path} 时出错: {str(e)}")

    print(f"[INFO] 总共加载了 {len(chunks)} 个知识块")
    return chunks

def simple_retrieve(query, knowledge_chunks):
    """简单的关键词检索"""
    query_lower = query.lower()
    print(f"[INFO] 检索查询: {query}")

    scores = []
    for chunk in knowledge_chunks:
        score = 0
        # 简单的关键词匹配
        query_words = set(query_lower.split())
        content_words = set(chunk.content.lower().split())
        common_words = query_words.intersection(content_words)
        if common_words:
            score = len(common_words) / len(query_words)

        chunk.similarity_score = score
        scores.append((score, chunk))

    # 按相似度排序
    scores.sort(key=lambda x: -x[0])

    # 返回前3个最相关的块
    relevant_chunks = [chunk for score, chunk in scores[:3] if score > 0]
    return relevant_chunks

def call_zai_api(query, retrieved_content):
    """调用Z.ai API生成增强的回答"""
    try:
        print(f"[INFO] 正在调用Z.ai API...")
        headers = {
            'x-api-key': ZAI_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
            'user-agent': 'WesternMusicRAG/1.0'
        }

        data = {
            'model': ZAI_MODEL,
            'max_tokens': 1500,
            'temperature': 0.7,
            'messages': [
                {
                    'role': 'user',
                    'content': f"""你是一位专业的西方音乐史专家。请基于以下知识库内容，准确回答用户的问题。

用户问题：{query}

知识库内容：
{retrieved_content}

要求：
1. 回答要基于知识库内容
2. 结构清晰，重点突出
3. 适当使用专业术语
4. 如果知识库信息不足，诚实地说明
5. 回答控制在500字以内"""
                }
            ]
        }

        # 构建完整的API URL
        api_url = f"{ZAI_API_BASE}/v1/messages"

        response = requests.post(api_url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            print(f"[INFO] Z.ai API调用成功，生成{len(content)}字符的AI回答")
            return content
        else:
            print(f"[ERROR] Z.ai API调用失败: {response.status_code}")
            print(f"[ERROR] 响应内容: {response.text}")
            return None

    except Exception as e:
        print(f"[ERROR] Z.ai API调用异常: {str(e)}")
        return None

class SimpleAIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def do_GET(self):
        if self.path == '/api/health':
            self._set_headers()
            response = {
                'status': 'ok',
                'message': '西方音乐史RAG系统运行正常（AI增强版本）',
                'server': 'Python http.server',
                'version': '9.0.0',
                'knowledge_base': 'Z.ai AI增强的专业知识库',
                'features': ['智能文本检索', 'Z.ai AI对话增强']
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        elif self.path == '/':
            try:
                html_file = os.path.join(os.path.dirname(__file__), 'index.html')
                if os.path.exists(html_file):
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html_content)))
                    self.end_headers()
                    self.wfile.write(html_content.encode())
                else:
                    self.send_error(404, "HTML file not found")
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

    def do_POST(self):
        if self.path == '/api/query':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
                    request_data = json.loads(post_data)

                    query = request_data.get('query', '').strip()

                    if query:
                        # 1. 检索相关知识
                        relevant_chunks = simple_retrieve(query, knowledge_chunks)

                        # 2. 生成AI增强回答
                        retrieved_content = '\n'.join([chunk.content for chunk in relevant_chunks[:3]])

                        if relevant_chunks:
                            try:
                                ai_answer = call_zai_api(query, retrieved_content)
                                ai_generated = ai_answer is not None
                                model_used = f'Z.ai {ZAI_MODEL}'
                            except Exception as e:
                                print(f"[WARNING] AI生成失败: {str(e)}")
                                ai_answer = retrieved_content[:500]
                                ai_generated = False
                                model_used = '基础检索模式'
                        else:
                            ai_answer = "很抱歉，我在知识库中找不到相关信息。"
                            ai_generated = False
                            model_used = '知识库检索'

                        self._set_headers(200)
                        response = {
                            'success': True,
                            'answer': ai_answer,
                            'period': None,
                            'question_type': 'general',
                            'retrieved_chunks_count': len(relevant_chunks),
                            'best_chunk_score': relevant_chunks[0].similarity_score if relevant_chunks else 0,
                            'ai_generated': ai_generated,
                            'model': model_used,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    else:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({'success': False, 'error': '查询不能为空'}).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'success': False, 'error': '请求体为空'}).encode())
            except Exception as e:
                self._set_headers(500)
                print(f"[ERROR] 处理请求时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

def run_simple_ai_server():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - 简单AI增强版本")
    print("=" * 70)
    print()

    print("系统特性:")
    print("  - 智能文本检索")
    print("  - Z.ai AI对话增强")
    print("  - 简单高效的响应")
    print()

    PORT = int(os.environ.get('PORT', 8000))
    print(f"[INFO] 端口: {PORT}")
    print(f"[INFO] AI提供商: Z.ai API")

    server_address = ('0.0.0.0', PORT)

    try:
        global knowledge_chunks
        knowledge_chunks = load_and_chunk_knowledge()

        if not knowledge_chunks:
            print("[ERROR] 知识库为空，请检查数据文件")
            return

        print()
        print(f"启动服务器在 0.0.0.0:{PORT}")
        print(f"API接口: http://0.0.0.0:{PORT}/api/query")
        print(f"知识块数量: {len(knowledge_chunks)}")
        print()

        httpd = HTTPServer(server_address, SimpleAIHandler)
        print("=" * 70)
        print("简单AI增强RAG服务器启动成功！")
        print("=" * 70)
        print()

        httpd.serve_forever()

    except Exception as e:
        print(f"[ERROR] 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simple_ai_server()
