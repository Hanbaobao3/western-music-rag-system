"""
西方音乐史RAG问答系统 - 最终优化版本
基于用户更新的专业知识库，提供准确的学术级问答
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

            # 简化的文件格式解析
            lines = content.split('\n')
            current_section = None
            section_content = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 识别章节标题
                if line.startswith('第') and '章' in line:
                    if current_section:
                        knowledge_base[current_section] = '\n'.join(section_content).strip()
                    current_section = line
                    section_content = []

                # 识别重要标题
                elif line.startswith(('、', '、', '（', '【')):
                    # 跳过这些标记，保持内容连贯
                    section_content.append(line)

            # 保存最后一个章节
            if current_section and section_content:
                knowledge_base[current_section] = '\n'.join(section_content).strip()

        except Exception as e:
            print(f"[ERROR] 读取文件 {file_path} 时出错: {e}")

    print(f"[INFO] 成功加载知识库，共 {len(knowledge_base)} 个章节")
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
                    '专业级知识库内容',
                    '准确的时期识别算法',
                    '结构化学术答题',
                    '调试信息便于排查',
                    '基于实际文件实时加载'
                ]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

    def identify_period_ultimate(self, question):
        """最终的时期识别算法"""
        question_lower = question.lower()

        # 为每个时期打分
        scores = {}

        # 古希腊
        ancient_keywords = ['古希腊', '古罗马', '毕达哥拉斯', '柏拉图', '亚里士多德', '调式', '音程', '理论', '颂歌', '悲剧合唱', '竞技颂歌', '品达']
        scores['ancient'] = sum(1 for kw in ancient_keywords if kw in question_lower)

        # 中世纪
        medieval_keywords = ['中世纪', '格里高利', '圣咏', '基督教', '奥尔加农', '经文歌', '等节奏', '教会调式', '弥撒', '礼拜']
        scores['medieval'] = sum(1 for kw in medieval_keywords if kw in question_lower)

        # 文艺复兴
        renaissance_keywords = ['文艺复兴', '迪法伊', '勃艮第', '奥克冈', '帕莱斯特里那', '世俗', '人文主义', '印刷术', '牧歌', '尚松', '利德']
        scores['renaissance'] = sum(1 for kw in renaissance_keywords if kw in question_lower)

        # 巴洛克
        baroque_keywords = ['巴洛克', '佩里', '蒙泰韦尔迪', '吕利', '拉莫', '珀塞尔', '科雷利', '协奏曲', '通奏低音', '歌剧', '奏鸣曲', '赋格']
        scores['baroque'] = sum(1 for kw in baroque_keywords if kw in question_lower)

        # 古典主义
        classical_keywords = ['古典主义', '海顿', '莫扎特', '贝多芬', '华美风格', '敏感风格', '曼海姆', '斯塔米茨', '奏鸣曲式', '回旋曲', '变奏曲', '交响曲']
        scores['classical'] = sum(1 for kw in classical_keywords if kw in question_lower)

        # 浪漫主义
        romantic_keywords = ['浪漫主义', '韦伯', '门德尔松', '舒曼', '肖邦', '李斯特', '瓦格纳', '马勒', '施特劳斯', '情感至上', '标题音乐', '民族主义', '歌剧', '利德']
        scores['romantic'] = sum(1 for kw in romantic_keywords if kw in question_lower)

        # 20世纪
        twentieth_keywords = ['20世纪', '德彪西', '拉威尔', '勋伯格', '表现主义', '十二音', '新古典主义', '梅西安', '艾夫斯', '偶然音乐', '电子音乐', '简约主义', '印象主义']
        scores['20th_century'] = sum(1 for kw in twentieth_keywords if kw in question_lower)

        # 选择得分最高的时期
        max_score = max(scores.values())
        best_periods = [k for k, v in scores.items() if v == max_score]

        # 边界检查：如果分数太低，返回None避免错误匹配
        if max_score < 2:
            return None

        # 如果多个时期分数相同，优先顺序：古典主义 > 浪漫主义 > 巴洛克 > 文艺复兴 > 中世纪 > 古代 > 20世纪
        if len(best_periods) > 1:
            for priority in ['classical', 'romantic', 'baroque', 'renaissance', 'medieval', 'ancient', '20th_century']:
                if priority in best_periods:
                    return priority

        return best_periods[0] if best_periods else None

    def generate_answer_final(self, question, period_key, knowledge_base):
        """生成准确的专业答案"""

        if period_key not in knowledge_base:
            return "该问题不在西方音乐史知识库范围内，请提供与古希腊、中世纪、文艺复兴、巴洛克、古典主义、浪漫主义或20世纪音乐相关的问题。"

        knowledge_content = knowledge_base[period_key]

        # 判断问题类型
        question_type = self._classify_question_type(question)

        if question_type == 'definition':
            # 名词解释：直接定义
            return f"**【名词解释】** {period_key}\n\n{self._extract_core_definition(knowledge_content)}"

        elif question_type == 'short_answer':
            # 简答题：主要特征
            return f"**【简答题】** {period_key}\n\n{self._extract_key_features(knowledge_content)}"

        elif question_type == 'essay':
            # 论述题：详细展开
            return f"**【论述题】** {period_key}\n\n{knowledge_content}"

        else:
            # 一般性问题：完整内容
            return f"**【综合回答】** {period_key}\n\n{knowledge_content}"

    def _extract_core_definition(self, content):
        """提取核心定义"""
        # 简单实现，直接返回内容
        lines = content.split('\n')
        definition_parts = []
        for line in lines[:10]:  # 取前10行作为核心定义
            if line.strip() and not line.startswith(('第', '（', '【', '*')):
                definition_parts.append(line.strip())
        return '\n'.join(definition_parts) if definition_parts else content[:200]

    def _extract_key_features(self, content):
        """提取关键特征"""
        lines = content.split('\n')
        key_features = []

        feature_keywords = ['特征', '特点', '主要', '核心', '重要', '代表', '发展', '意义', '影响', '作用', '主要特征：']

        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in feature_keywords):
                key_features.append(line.strip())
                if len(key_features) >= 6:  # 收集6个关键特征
                    break

        return '\n'.join(key_features) if key_features else content[:300]

    def _classify_question_type(self, question):
        """题目分类"""
        question_lower = question.lower()

        if any(kw in question_lower for kw in ['什么是', '定义', '名词解释', '解释', '概念', '含义', '术语']):
            return 'definition'
        elif any(kw in question_lower for kw in ['特点', '特征', '风格', '主要', '简述', '简答', '谈谈']):
            return 'short_answer'
        elif any(kw in question_lower for kw in ['论述', '分析', '发展', '演变', '过程', '历史', '影响', '意义', '贡献']):
            return 'essay'
        elif any(kw in question_lower for kw in ['对比', '比较', '区别', '差异', '相同', '不同']):
            return 'comparison'
        else:
            return 'general'

    def do_POST(self):
        if self.path == '/api/query':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    request_data = json.loads(post_data)

                    query = request_data.get('query', '').strip()

                    if query:
                        # 加载最新的知识库
                        knowledge_base = load_knowledge_base()

                        # 识别时期
                        period_key = self.identify_period_ultimate(query)

                        # 生成答案
                        answer = self.generate_answer_final(query, period_key, knowledge_base)

                        # 记录请求信息（调试用）
                        print(f"[REQUEST] 问题: {query}")
                        print(f"[REQUEST] 识别时期: {period_key}")
                        print(f"[REQUEST] 知识库章节: {len(knowledge_base)} 个")

                        self._set_headers(200)
                        response = {
                            'success': True,
                            'answer': answer,
                            'period': period_key,
                            'question_type': self._classify_question_type(query),
                            'knowledge_base_info': f'基于{len(knowledge_base)} 个章节的知识库',
                            'data_sources': KNOWLEDGE_FILES,
                            'ai_generated': False,
                            'model': '专业音乐史知识库',
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'debug_info': {
                                'detected_period': period_key,
                                'knowledge_size': len(knowledge_base),
                                'question_length': len(query),
                                'confidence': 'high' if period_key else 'low'
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

def run_final_server():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - 最终优化版本")
    print("=" * 70)
    print()

    print("优化内容:")
    print("  ✓ 基于用户更新的专业知识库")
    print("  ✓ 实时加载E:\\ai-apps\\rag-system\\data目录知识库")
    print("  ✓ 提高时期识别准确性")
    print("  ✓ 减少答非所问的情况")
    print("  ✓ 增加详细调试信息")
    print()

    PORT = 5001
    server_address = ('127.0.0.1', PORT)
    print(f"启动服务器在 http://127.0.0.1:{PORT}")
    print(f"API接口: http://127.0.0.1:{PORT}/api/query")
    print(f"数据源: {KNOWLEDGE_FILES}")
    print()

    print("系统特点:")
    print("  - 实时知识库加载")
    print("  - 专业级学术答题")
    print("  - 准确的时期识别")
    print("  - 调试信息输出")
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
    run_final_server()
