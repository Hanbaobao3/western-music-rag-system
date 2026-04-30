"""
西方音乐史RAG问答系统 - 基础版本
先确保基础RAG功能正常工作
"""
import json
import os
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

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

            for line in lines:
                line_stripped = line.strip()

                # 检测章节标题
                if line_stripped and (line_stripped.startswith('#') or re.match(r'^[一二三四五六七八九十]+[、．.]', line_stripped)):
                    # 保存当前块
                    if current_chunk:
                        chunk_text = '\n'.join(current_chunk).strip()
                        if chunk_text and len(chunk_text) > 50:
                            chunk = KnowledgeChunk(chunk_text, [], None, importance=0)
                            chunks.append(chunk)

                    # 开始新章节
                    current_chunk = []
                else:
                    # 收集当前行到当前块中
                    if line_stripped or current_chunk:
                        current_chunk.append(line)

                        # 如果块足够大，创建新块
                        if len(current_chunk) > 15:
                            chunk_text = '\n'.join(current_chunk).strip()
                            if chunk_text and len(chunk_text) > 50:
                                chunk = KnowledgeChunk(chunk_text, [], None, importance=0)
                                chunks.append(chunk)
                            current_chunk = []

            # 处理最后一个块
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text and len(chunk_text) > 50:
                    chunk = KnowledgeChunk(chunk_text, [], None, importance=0)
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

def generate_basic_answer(query, relevant_chunks):
    """生成基础的RAG回答"""
    if not relevant_chunks:
        return "很抱歉，我在知识库中找不到相关信息。建议您重新组织问题或扩大查询范围。"

    # 获取最相关的内容
    content = relevant_chunks[0].content

    # 简化的答案生成
    lines = content.split('\n')
    relevant_lines = []

    for line in lines[:10]:
        line_clean = line.strip()
        if line_clean and len(line_clean) > 10:
            relevant_lines.append(line_clean)
        if len(relevant_lines) >= 5:
            break

    if relevant_lines:
        return f"**【综合回答】**\n\n{query}\n\n" + "\n".join([line for line in relevant_lines[:5]])
    else:
        return f"**【综合回答】**\n\n{query}\n\n{content[:400]}..."

class BasicRAGHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))

    def do_GET(self):
        if self.path == '/api/health':
            # API健康检查端点
            self._set_headers()
            response = {
                'status': 'ok',
                'message': '西方音乐史RAG系统运行正常（基础版本）',
                'server': 'Python http.server',
                'version': '10.0.0',
                'knowledge_base': '基础RAG知识库',
                'features': ['智能文本检索', '基础问答']
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/':
            # 服务前端HTML页面
            try:
                html_file = os.path.join(os.path.dirname(__file__), 'index.html')
                if os.path.exists(html_file):
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html_content)))
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    self.send_error(404, "HTML file not found")
            except Exception as e:
                self.send_error(500, f"Error: {str(e)}")
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode('utf-8'))

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

                        # 2. 生成基础回答
                        answer = generate_basic_answer(query, relevant_chunks)

                        self._set_headers(200)
                        response = {
                            'success': True,
                            'answer': answer,
                            'period': None,
                            'question_type': 'general',
                            'retrieved_chunks_count': len(relevant_chunks),
                            'best_chunk_score': relevant_chunks[0].similarity_score if relevant_chunks else 0,
                            'ai_generated': False,
                            'model': '基础RAG检索',
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                    else:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({'success': False, 'error': '查询不能为空'}).encode('utf-8'))
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'success': False, 'error': '请求体为空'}).encode('utf-8'))
            except Exception as e:
                self._set_headers(500)
                print(f"[ERROR] 处理请求时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode('utf-8'))

def run_basic_rag_server():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - 基础版本")
    print("=" * 70)
    print()

    print("系统特性:")
    print("  - 智能文本检索")
    print("  - 基础问答")
    print("  - 简单高效的响应")
    print()

    PORT = int(os.environ.get('PORT', 8000))
    print(f"[INFO] 端口: {PORT}")

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

        httpd = HTTPServer(server_address, BasicRAGHandler)
        print("=" * 70)
        print("基础RAG服务器启动成功！")
        print("=" * 70)
        print()

        httpd.serve_forever()

    except Exception as e:
        print(f"[ERROR] 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_basic_rag_server()
