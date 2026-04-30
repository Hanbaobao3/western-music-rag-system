"""
西方音乐史RAG问答系统 - 最终优化版本（端口8000）
"""
import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# 知识库数据路径
DATA_DIR = r"E:\ai-apps\rag-system\data"
KNOWLEDGE_FILES = [
    os.path.join(DATA_DIR, 'music history.txt'),
    os.path.join(DATA_DIR, 'music history 2.txt')
]

def load_knowledge_base():
    """从文件加载知识库"""
    knowledge_base = {}

    for file_path in KNOWLEDGE_FILES:
        if not os.path.exists(file_path):
            print(f"[WARNING] 文件不存在: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 章节化的文件格式解析
            lines = content.split('\n')
            current_section = None
            section_content = []

            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # 识别章节标题（以"第"开头且包含"章"）
                if line_stripped.startswith('第') and '章' in line_stripped:
                    # 保存前一个章节
                    if current_section and section_content:
                        knowledge_base[current_section] = '\n'.join(section_content).strip()

                    # 开始新章节
                    current_section = line_stripped
                    section_content = []

                # 其他内容都加入当前章节
                elif current_section:
                    section_content.append(line)  # 保留原始格式

            # 保存最后一个章节
            if current_section and section_content:
                knowledge_base[current_section] = '\n'.join(section_content).strip()

        except Exception as e:
            print(f"[ERROR] 读取文件 {file_path} 时出错: {e}")

    print(f"[INFO] 成功加载知识库，共 {len(knowledge_base)} 个章节")
    print(f"[INFO] 章节列表: {list(knowledge_base.keys())}")
    return knowledge_base

class FinalRAGHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode())

    def do_GET(self):
        if self.path in ['/', '/api/health']:
            self._set_headers()
            knowledge_base = load_knowledge_base()
            response = {
                'status': 'ok',
                'message': '西方音乐史RAG系统运行正常（最终优化版）',
                'server': 'Python http.server',
                'version': '6.0.0',
                'knowledge_base': f'基于用户更新的专业音乐史知识库，共 {len(knowledge_base)} 个章节',
                'data_sources': KNOWLEDGE_FILES,
                'features': [
                    '实时知识库加载',
                    '专业级学术答题',
                    '准确的时期识别',
                    '结构化学术答题',
                    '基于用户更新的数据源'
                ]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

    def identify_period_ultimate(self, question):
        """最终的时期识别算法"""
        question_lower = question.lower()

        # 为每个时期打分 - 使用实际章节标题
        period_scores = {}

        # 第一章 古代与中世纪音乐（公元前～1400年）
        ancient_medieval_keywords = ['古希腊', '古罗马', '毕达哥拉斯', '柏拉图', '亚里士多德', '调式', '音程', '理论', '颂歌', '悲剧合唱', '竞技颂歌', '品达', '中世纪', '格里高利', '圣咏', '基督教', '奥尔加农', '经文歌', '等节奏', '教会调式', '弥撒', '礼拜']
        period_scores['第一章 古代与中世纪音乐（公元前～1400年）'] = sum(1 for kw in ancient_medieval_keywords if kw in question_lower)

        # 第二章 文艺复兴时期音乐（约1400—1600年）
        renaissance_keywords = ['文艺复兴', '迪法伊', '勃艮第', '奥克冈', '帕莱斯特里那', '世俗', '人文主义', '印刷术', '牧歌', '尚松', '利德', '若斯坎', '特伦托']
        period_scores['第二章 文艺复兴时期音乐（约1400—1600年）'] = sum(1 for kw in renaissance_keywords if kw in question_lower)

        # 第三章 巴洛克时期音乐（约1600—1750年）
        baroque_keywords = ['巴洛克', '佩里', '蒙泰韦尔迪', '吕利', '拉莫', '珀塞尔', '科雷利', '协奏曲', '通奏低音', '歌剧', '奏鸣曲', '赋格', '巴赫', '亨德尔', '维瓦尔第']
        period_scores['第三章 巴洛克时期音乐（约1600—1750年）'] = sum(1 for kw in baroque_keywords if kw in question_lower)

        # 第四章 古典主义时期音乐（约1750—1820年）
        classical_keywords = ['古典主义', '海顿', '莫扎特', '贝多芬', '华美风格', '敏感风格', '曼海姆', '斯塔米茨', '奏鸣曲式', '交响曲', 'CPE巴赫']
        period_scores['第四章 古典主义时期音乐（约1750—1820年）'] = sum(1 for kw in classical_keywords if kw in question_lower)

        # 第五章 浪漫主义时期音乐（约1820—1900年）
        romantic_keywords = ['浪漫主义', '韦伯', '门德尔松', '舒曼', '肖邦', '李斯特', '瓦格纳', '马勒', '施特劳斯', '情感至上', '标题音乐', '民族主义', '歌剧', '舒伯特', '勃拉姆斯', '威尔第']
        period_scores['第五章 浪漫主义时期音乐（约1820—1900年）'] = sum(1 for kw in romantic_keywords if kw in question_lower)

        # 第六章 二十世纪音乐（约1900—2000年）
        twentieth_keywords = ['20世纪', '德彪西', '拉威尔', '勋伯格', '表现主义', '十二音', '新古典主义', '梅西安', '艾夫斯', '印象主义', '简约主义', '斯特拉文斯基', '凯奇']
        period_scores['第六章 二十世纪音乐（约1900—2000年）'] = sum(1 for kw in twentieth_keywords if kw in question_lower)

        # 选择得分最高的时期
        max_score = max(period_scores.values())
        best_periods = [k for k, v in period_scores.items() if v == max_score]

        # 边界检查
        if max_score >= 2 and len(best_periods) > 1:
            print(f"[DEBUG] 多个时期匹配: {best_periods}")
        if max_score < 1:  # 降低阈值，更容易匹配
            # 分数太低，返回None
            return None

        return best_periods[0] if best_periods else None

    def generate_answer_final(self, question, period_key, knowledge_base):
        """生成准确的学术答案"""

        if not period_key or period_key not in knowledge_base:
            return "该问题不在西方音乐史知识库范围内，请提供与古希腊、中世纪、文艺复兴、巴洛克、古典主义、浪漫主义或20世纪音乐相关的问题。"

        knowledge_content = knowledge_base[period_key]

        # 判断问题类型
        question_type = self._classify_question_type(question)

        # 根据题型生成不同的回答
        if question_type == 'definition':
            # 名词解释：直接返回知识库内容
            return f"**【名词解释】** {period_key}\n\n{knowledge_content[:500]}..."

        elif question_type == 'short_answer':
            # 简答题：提取要点
            return f"**【简答题】** {period_key}\n\n{knowledge_content[:800]}..."

        elif question_type == 'essay':
            # 论述题：完整内容
            return f"**【论述题】** {period_key}\n\n{knowledge_content}"

        else:
            # 一般性问题：返回核心内容
            return f"**【综合回答】** {period_key}\n\n{knowledge_content}"

    def _classify_question_type(self, question):
        """题目分类"""
        question_lower = question.lower()

        # 名词解释类
        if any(keyword in question_lower for keyword in ['什么是', '定义', '名词解释', '解释', '概念', '含义', '术语']):
            return 'definition'

        # 简答题类
        elif any(keyword in question_lower for keyword in ['特点', '特征', '风格', '主要', '简述', '简答', '谈谈', '概括']):
            return 'short_answer'

        # 论述题类
        elif any(keyword in question_lower for keyword in ['论述', '分析', '发展', '演变', '过程', '历史', '影响', '意义', '贡献', '作用', '重要性']):
            return 'essay'

        # 对比题类
        elif any(keyword in question_lower for keyword in ['对比', '比较', '区别', '差异', '相同', '不同']):
            return 'comparison'

        else:
            return 'general'

    def do_POST(self):
        if self.path == '/api/query':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8', errors='ignore')
                    request_data = json.loads(post_data)

                    query = request_data.get('query', '').strip()

                    if query:
                        # 加载知识库
                        knowledge_base = load_knowledge_base()

                        # 识别时期
                        period_key = self.identify_period_ultimate(query)

                        # 生成答案
                        answer = self.generate_answer_final(query, period_key, knowledge_base)

                        self._set_headers(200)

                        # Handle period_key being None
                        chapter_info = "未知时期"
                        if period_key and period_key in knowledge_base:
                            try:
                                chapter_info = f'第{list(knowledge_base.keys()).index(period_key) + 1}章'
                            except (ValueError, IndexError):
                                chapter_info = "匹配章节"

                        response = {
                            'success': True,
                            'answer': answer,
                            'period': period_key,
                            'question_type': self._classify_question_type(query),
                            'knowledge_base_info': chapter_info,
                            'ai_generated': False,
                            'model': '用户更新的专业音乐史知识库',
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'debug_info': {
                                'detected_period': period_key,
                                'knowledge_chapters': len(knowledge_base),
                                'question_length': len(query),
                                'confidence': 'high' if period_key else 'medium'
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
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

def run_final_server_8000():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - 最终优化版本（端口8000）")
    print("=" * 70)
    print()

    print("优化内容:")
    print("  - 基于用户更新的专业知识库")
    print("  - 实时加载E:\\ai-apps\\rag-system\\data目录知识库")
    print("  - 提高时期识别准确性")
    print("  - 优化答题逻辑")
    print("  - 增加调试信息")
    print()

    PORT = 8000
    server_address = ('127.0.0.1', PORT)
    print(f"启动服务器在 http://127.0.0.1:{PORT}")
    print(f"API接口: http://127.0.0.1:{PORT}/api/query")
    print(f"数据源: {KNOWLEDGE_FILES}")
    print()

    print("系统特点:")
    print("  - 实时知识库加载")
    print("  - 专业学术级问答")
    print("  - 高精度时期识别")
    print("  - 基于用户更新的数据源")
    print()

    try:
        httpd = HTTPServer(server_address, FinalRAGHandler)
        print("=" * 70)
        print("服务器启动成功！")
        print("=" * 70)
        print()
        print("按Ctrl+C停止服务器")
        print()

        httpd.serve_forever()

    except Exception as e:
        print(f"服务器启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    run_final_server_8000()
