"""
西方音乐史RAG问答系统 - AI增强版本
集成Z.ai大语言模型，提供智能对话体验
"""
import json
import os
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Z.ai API配置
ZAI_API_KEY = os.getenv('ZAI_API_KEY')
ZAI_API_BASE = os.getenv('ZAI_API_BASE', 'https://api.z.ai/api/anthropic')
ZAI_MODEL = os.getenv('ZAI_MODEL', 'claude-sonnet-4-20250514')

# 知识库数据路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
KNOWLEDGE_FILES = [
    os.path.join(DATA_DIR, 'music history.txt'),
    os.path.join(DATA_DIR, 'music history 2.txt')
]

def get_available_data_files():
    """获取可用的数据文件列表"""
    available_files = []
    if os.path.exists(DATA_DIR):
        for file_name in ['music history.txt', 'music history 2.txt']:
            file_path = os.path.join(DATA_DIR, file_name)
            if os.path.exists(file_path):
                available_files.append(file_path)
            else:
                print(f"[WARNING] 文件不存在: {file_path}")
    else:
        print(f"[WARNING] 数据目录不存在: {DATA_DIR}")
        print(f"[INFO] 当前工作目录: {os.getcwd()}")
        print(f"[INFO] 项目根目录: {BASE_DIR}")
    return available_files

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
    print(f"[INFO] 当前工作目录: {os.getcwd()}")

    for file_path in KNOWLEDGE_FILES:
        if not os.path.exists(file_path):
            print(f"[WARNING] 文件不存在: {file_path}")
            continue

        print(f"[INFO] 正在读取文件: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"[INFO] 文件大小: {len(content)} 字符")

            # 章节化的文件格式解析 + 精细切块
            lines = content.split('\n')
            current_section = None
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
                            chunk = KnowledgeChunk(chunk_text, chunk_keywords, current_section, importance=calculate_importance(chunk_text))
                            chunks.append(chunk)

                    # 开始新章节
                    current_section = line_stripped.replace('#', '').strip()
                    current_chunk = []
                    chunk_keywords = extract_keywords_from_heading(current_section)

                else:
                    # 收集当前行到当前块中
                    if line_stripped or current_chunk:
                        current_chunk.append(line)

                        # 如果块足够大，创建新块
                        if len(current_chunk) > 15:  # 15行为一个块
                            chunk_text = '\n'.join(current_chunk).strip()
                            if chunk_text and len(chunk_text) > 50:
                                chunk = KnowledgeChunk(chunk_text, chunk_keywords, current_section, importance=calculate_importance(chunk_text))
                                chunks.append(chunk)
                            current_chunk = []

            # 处理最后一个块
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text and len(chunk_text) > 50:
                    chunk = KnowledgeChunk(chunk_text, chunk_keywords, current_section, importance=calculate_importance(chunk_text))
                    chunks.append(chunk)

        except Exception as e:
            print(f"[ERROR] 处理文件 {file_path} 时出错: {str(e)}")

    print(f"[INFO] 总共加载了 {len(chunks)} 个知识块")
    return chunks

def calculate_importance(content):
    """计算内容的重要性评分"""
    score = 0

    # 检查重要人物
    important_persons = ['贝多芬', '莫扎特', '海顿', '巴赫', '亨德尔', '肖邦',
                       '李斯特', '瓦格纳', '德彪西', '帕莱斯特里那']
    for person in important_persons:
        if person in content:
            score += 2

    # 检查重要概念
    important_terms = ['奏鸣曲', '交响曲', '赋格', '对位法', '和声', '调式']
    for term in important_terms:
        if term in content:
            score += 1

    # 检查历史时期关键词
    periods = ['巴洛克', '古典主义', '浪漫主义', '文艺复兴', '中世纪', '现代主义']
    for period in periods:
        if period in content:
            score += 1

    return score

def extract_keywords_from_content(content):
    """从内容中提取关键词"""
    keywords = []
    important_terms = ['奏鸣曲', '交响曲', '赋格', '对位法', '和声', '调式',
                    '巴洛克', '古典主义', '浪漫主义', '文艺复兴', '中世纪']
    for term in important_terms:
        if term in content:
            keywords.append(term)
    return keywords[:5]  # 最多返回5个关键词

def intelligent_retrieve(query, knowledge_chunks):
    """智能检索最相关的知识块"""
    query_lower = query.lower()

    print(f"[INFO] 检索查询: {query}")

    # 1. 为每个知识块计算相似度
    for chunk in knowledge_chunks:
        chunk.similarity_score = calculate_similarity(query_lower, chunk)

    # 2. 按相似度排序
    sorted_chunks = sorted(knowledge_chunks, key=lambda x: -x.similarity_score)

    # 3. 选择前3个最相关的块
    relevant_chunks = sorted_chunks[:3]

    # 4. 进一步过滤 - 确保相关性
    filtered_chunks = [chunk for chunk in relevant_chunks if chunk.similarity_score > 0]

    return filtered_chunks if filtered_chunks else relevant_chunks

def calculate_similarity(query_lower, chunk):
    """计算查询与知识块的相似度 - 改进版"""
    score = 0
    entity_types = {'person': 0, 'term': 0, 'period': 0, 'general': 0}

    # 1. 实体识别 - 区分人名、术语、时期
    person_names = ['贝多芬', '莫扎特', '海顿', '巴赫', '亨德尔', '肖邦',
                   '李斯特', '瓦格纳', '德彪西', '勋伯格', '帕莱斯特里那']

    music_terms = ['通奏低音', '赋格', '奏鸣曲', '协奏曲', '交响曲', '弥撒曲',
                   '格里高利圣咏', '奥尔加农', '经文歌', '牧歌', '歌剧',
                   '和声', '调式', '音程', '节奏', '旋律', '对位法']

    # 2. 实体匹配 - 人名给予最高优先级
    query_entity_type = None
    for person in person_names:
        if person.lower() in query_lower:
            query_entity_type = 'person'
            if person.lower() in chunk.content.lower():
                entity_types['person'] += 20  # 人名完全匹配给予最高分
                break
            elif any(word in chunk.content.lower() for word in person.lower().split()):
                entity_types['person'] += 15  # 人名部分匹配给予高分
                break

    # 3. 术语匹配
    for term in music_terms:
        if term in query_lower:
            query_entity_type = 'term'
            if term in chunk.content:
                entity_types['term'] += 10
                score += 5  # 术语匹配额外加分

    # 4. 时期匹配
    periods = ['巴洛克', '古典主义', '浪漫主义', '文艺复兴', '中世纪', '印象主义']
    for period in periods:
        if period in query_lower:
            entity_types['period'] = True
            if period in chunk.content:
                score += 8

    # 5. 关键词匹配
    for keyword in chunk.keywords:
        if keyword in query_lower:
            score += 3

    # 6. 内容相似度 - 简单的词频匹配
    query_words = set(query_lower.split())
    content_words = set(chunk.content.lower().split())
    common_words = query_words.intersection(content_words)
    if common_words:
        similarity_ratio = len(common_words) / len(query_words)
        score += similarity_ratio * 30

    # 7. 实体类型匹配奖励
    if query_entity_type:
        entity_types['general'] = sum([entity_types['person'], entity_types['term']])

    return score

def identify_period_from_query(query_lower):
    """从查询中识别历史时期"""
    periods = {
        '中世纪': ['中世纪', '格里高利圣咏', '单声部'],
        '文艺复兴': ['文艺复兴', '帕莱斯特里那', '复调'],
        '巴洛克': ['巴洛克', '巴赫', '亨德尔', '通奏低音'],
        '古典主义': ['古典主义', '海顿', '莫扎特', '贝多芬'],
        '浪漫主义': ['浪漫主义', '肖邦', '李斯特', '瓦格纳'],
        '现代主义': ['现代主义', '德彪西', '斯特拉文斯基']
    }

    for period, keywords in periods.items():
        for keyword in keywords:
            if keyword in query_lower:
                return period

    return None

def generate_targeted_answer(query, relevant_chunks, question_type):
    """生成针对不同问题类型的答案"""
    if not relevant_chunks:
        return "很抱歉，我在知识库中找不到相关信息。建议您重新组织问题或扩大查询范围。"

    # 获取最相关的内容
    content = relevant_chunks[0].content

    if question_type == 'definition':
        return f"**【名词解释】**\n\n{query}\n\n{content[:500]}..."

    elif question_type == 'short_answer':
        # 提取要点
        lines = content.split('\n')
        key_points = []
        for line in lines[:8]:
            line_clean = line.strip()
            if line_clean and len(line_clean) > 10:
                key_points.append(line_clean)
            if len(key_points) >= 4:
                break

        if key_points:
            points_text = '\n'.join([f"• {point}" for point in key_points])
            return f"**【简答题】**\n\n{query}\n\n{points_text}"
        else:
            return f"**【简答题】**\n\n{query}\n\n{content[:300]}..."

    elif question_type == 'essay':
        # 对于论述题，使用完整的第一个相关块
        if len(relevant_chunks) > 1:
            combined_content = '\n\n'.join([chunk.content for chunk in relevant_chunks[:2]])
            return f"**【论述题】**\n\n{query}\n\n{combined_content}"
        else:
            return f"**【论述题】**\n\n{query}\n\n{content}"

    else:  # general
        # 提取最相关的内容段落
        lines = content.split('\n')
        relevant_lines = []

        for line in lines[:10]:
            line_clean = line.strip()
            if line_clean and len(line_clean) > 10:
                relevant_lines.append(line_clean)
            if len(relevant_lines) >= 5:
                break

        if relevant_lines:
            return f"**【综合回答】**\n\n{query}\n\n" + '\n'.join([line for line in relevant_lines[:5]])
        else:
            return f"**【综合回答】**\n\n{query}\n\n{content[:400]}..."

def classify_question_type(question):
    """分类问题类型"""
    question_lower = question.lower()

    if any(keyword in question_lower for keyword in ['是什么', '什么', '定义', '解释', '何为', '指的是']):
        return 'definition'

    elif any(keyword in question_lower for keyword in ['特点', '特征', '风格', '主要', '简述', '简答', '谈谈', '概括']):
        return 'short_answer'

    elif any(keyword in question_lower for keyword in ['论述', '分析', '发展', '演变', '过程', '历史', '影响', '意义', '贡献', '作用', '重要性']):
        return 'essay'

    elif any(keyword in question_lower for keyword in ['对比', '比较', '区别', '差异', '相同', '不同']):
        return 'comparison'

    else:
        return 'general'

# Z.ai API调用函数
def call_zai_api(prompt, max_tokens=2000, temperature=0.7):
    """调用Z.ai API生成AI增强的回答"""
    if not ZAI_API_KEY:
        print("[WARNING] Z.ai API Key未配置，使用基础检索模式")
        return None

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
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
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

    except requests.exceptions.Timeout:
        print("[ERROR] Z.ai API调用超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Z.ai API调用异常: {str(e)}")
        return None
    except Exception as e:
        print(f"[ERROR] Z.ai API调用未知错误: {str(e)}")
        return None

def generate_ai_enhanced_answer(query, retrieved_content, question_type, context=""):
    """使用Z.ai AI生成增强的回答"""
    # 构建系统提示词
    system_prompt = """你是一位专业的西方音乐史专家，擅长用清晰、准确的方式回答音乐史问题。
你的回答应该：
1. 基于提供的知识库内容
2. 结构清晰，重点突出
3. 适当使用专业术语但避免晦涩
4. 根据问题类型调整回答风格
5. 如果知识库信息不足，诚实地说明"""

    # 构建用户提示词
    if question_type == 'definition':
        user_prompt = f"""请基于以下西方音乐史知识，定义和解释"{query}"：

知识库内容：
{retrieved_content}

要求：
- 给出准确的定义
- 举例说明
- 适当介绍相关概念"""

    elif question_type == 'short_answer':
        user_prompt = f"""请基于以下西方音乐史知识，简明回答关于"{query}"的问题：

知识库内容：
{retrieved_content}

要求：
- 回答简洁明了，200字以内
- 重点突出关键信息
- 条理清晰"""

    elif question_type == 'essay':
        user_prompt = f"""请基于以下西方音乐史知识，详细论述"{query}"：

知识库内容：
{retrieved_content}

要求：
- 回答详细，结构完整
- 分析深入，逻辑清晰
- 适当引用知识库内容
- 字数控制在800字以内"""

    elif question_type == 'comparison':
        user_prompt = f"""请基于以下西方音乐史知识，分析比较"{query}"：

知识库内容：
{retrieved_content}

要求：
- 明确比较对象和方面
- 指出相同点和不同点
- 分析原因和影响
- 结构清晰，对比明确"""

    else:  # general
        user_prompt = f"""请基于以下西方音乐史知识，全面回答"{query}"这个问题：

知识库内容：
{retrieved_content}

要求：
- 回答全面准确
- 重点突出关键信息
- 条理清晰，易于理解
- 适当组织成段落"""

    # 添加上下文信息（如果是多轮对话）
    if context:
        user_prompt += f"\n\n对话上下文：{context}"

    # 调用Z.ai API
    ai_answer = call_zai_api(user_prompt, max_tokens=1500, temperature=0.7)

    if ai_answer:
        return ai_answer
    else:
        print("[WARNING] AI回答生成失败，回退到基础检索模式")
        return generate_targeted_answer(query, [], question_type)

class AIEnhancedRAGHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode()

    def do_GET(self):
        if self.path == '/api/health':
            # API健康检查端点
            self._set_headers()
            response = {
                'status': 'ok',
                'message': '西方音乐史RAG系统运行正常（AI增强版本）',
                'server': 'Python http.server',
                'version': '8.0.0',
                'knowledge_base': '基于Z.ai AI增强的专业知识库',
                'data_sources': KNOWLEDGE_FILES,
                'features': [
                    '智能文本切块',
                    '细粒度知识检索',
                    '针对性答案生成',
                    '多维度相似度计算',
                    'Z.ai AI智能对话增强'
                ]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/':
            # 服务前端HTML页面
            try:
                html_file = os.path.join(os.path.dirname(__file__), 'index.html')
                if os.path.exists(html_file):
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    # 设置HTML响应头
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(html_content)))
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    self.send_error(404, "HTML file not found")
            except Exception as e:
                self.send_error(500, f"Error serving HTML: {str(e)}")
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
                        # 1. 智能检索最相关的知识块
                        relevant_chunks = intelligent_retrieve(query, knowledge_chunks)

                        # 2. 分类问题类型
                        question_type = classify_question_type(query)

                        # 3. 获取时期信息
                        detected_period = identify_period_from_query(query.lower())

                        # 4. 使用Z.ai AI生成增强答案
                        retrieved_content = '\n'.join([chunk.content for chunk in relevant_chunks[:3]])
                        try:
                            ai_answer = generate_ai_enhanced_answer(query, retrieved_content, question_type)
                            ai_generated = True
                            model_used = f'Z.ai {ZAI_MODEL}'
                        except Exception as e:
                            print(f"[WARNING] AI生成失败，使用基础检索模式: {str(e)}")
                            # 回退到基础检索模式
                            ai_answer = generate_targeted_answer(query, relevant_chunks, question_type)
                            ai_generated = False
                            model_used = '智能检索增强的音乐史知识库'

                        self._set_headers(200)
                        # 获取最佳块的信息用于调试
                        best_chunk_info = {}
                        if relevant_chunks:
                            best_chunk_info = {
                                'score': relevant_chunks[0].similarity_score,
                                'entity_types': getattr(relevant_chunks[0], 'entity_types', {}),
                                'content_preview': relevant_chunks[0].content[:100] + '...'
                            }

                        response = {
                            'success': True,
                            'answer': ai_answer,
                            'period': detected_period,
                            'question_type': question_type,
                            'retrieved_chunks_count': len(relevant_chunks),
                            'best_chunk_score': relevant_chunks[0].similarity_score if relevant_chunks else 0,
                            'ai_generated': ai_generated,
                            'model': model_used,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'debug_info': {
                                'detected_period': detected_period,
                                'total_chunks': len(knowledge_chunks),
                                'retrieved_chunks': len(relevant_chunks),
                                'query_length': len(query),
                                'similarity_score': relevant_chunks[0].similarity_score if relevant_chunks else 0,
                                'best_chunk_info': best_chunk_info
                            }
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

def run_ai_enhanced_server():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - AI增强版本")
    print("=" * 70)
    print()

    print("系统特性:")
    print("  - 智能文本切块：按知识点分块，不是整章")
    print("  - 细粒度检索：找到最相关的知识段落")
    print("  - 针对性答案：根据问题类型生成格式化回答")
    print("  - 多维度相似度：关键词匹配 + 内容匹配 + 时期匹配")
    print("  - 智能问答体验：真正的RAG，不是文档检索")
    print("  - Z.ai AI增强：基于大语言模型的智能对话")
    print()

    # 从环境变量获取端口，默认8000（Render会提供PORT环境变量）
    PORT = int(os.environ.get('PORT', 8000))
    print(f"[INFO] 端口: {PORT}")
    print(f"[INFO] 环境: {'生产环境' if os.environ.get('PORT') else '开发环境'}")
    print(f"[INFO] AI提供商: {'Z.ai API' if ZAI_API_KEY else '基础检索模式'}")

    # 使用0.0.0.0以支持外部访问（Render部署需要）
    server_address = ('0.0.0.0', PORT)

    try:
        # 加载并切块知识库
        global knowledge_chunks
        knowledge_chunks = load_and_chunk_knowledge()

        if not knowledge_chunks:
            print("[ERROR] 知识库为空，请检查数据文件")
            print("[ERROR] 尝试查找可用的数据文件:")
            import glob
            data_files = glob.glob("**/*.txt", recursive=True)
            print(f"[INFO] 找到的txt文件: {data_files}")
            return

        print()
        print(f"启动服务器在 0.0.0.0:{PORT}")
        print(f"API接口: http://0.0.0.0:{PORT}/api/query")
        print(f"知识块数量: {len(knowledge_chunks)}")
        print()

        httpd = HTTPServer(server_address, AIEnhancedRAGHandler)
        print("=" * 70)
        print("AI增强RAG服务器启动成功！")
        print("=" * 70)
        print()
        print("按Ctrl+C停止服务器")
        print()

        httpd.serve_forever()

    except Exception as e:
        print(f"[ERROR] 服务器启动失败: {e}")
        import traceback
        import sys
        traceback.print_exc()
        print(f"[ERROR] 详细错误: {str(e)}", file=sys.stderr)
        print(f"[ERROR] 错误类型: {type(e).__name__}", file=sys.stderr)

if __name__ == "__main__":
    run_ai_enhanced_server()
