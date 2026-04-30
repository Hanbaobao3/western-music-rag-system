"""
西方音乐史RAG问答系统 - 高级版本
改进：精细文本切块、智能检索、针对性答案生成
"""
import json
import os
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

# 知识库数据路径 - 使用相对路径以支持Render部署
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
        self.importance = importance  # 重要性评分
        self.similarity_score = 0  # 相似度评分

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

                # 识别章节标题
                if line_stripped.startswith('第') and '章' in line_stripped:
                    # 保存前一个块
                    if current_section and current_chunk:
                        chunk_content = '\n'.join(current_chunk).strip()
                        if chunk_content:
                            chunks.append(create_intelligent_chunk(
                                chunk_content, chunk_keywords, current_section
                            ))

                    # 开始新章节
                    current_section = line_stripped
                    current_chunk = []
                    chunk_keywords = []

                # 识别重要的知识点标题
                elif current_section and is_important_heading(line_stripped):
                    # 保存前一个块（如果非空）
                    if current_chunk:
                        chunk_content = '\n'.join(current_chunk).strip()
                        if chunk_content:
                            chunks.append(create_intelligent_chunk(
                                chunk_content, chunk_keywords, current_section
                            ))

                    # 开始新的知识块
                    current_chunk = [line]
                    # 提取关键词
                    chunk_keywords = extract_keywords_from_heading(line_stripped)

                # 普通内容行
                elif current_section and line_stripped:
                    current_chunk.append(line)

            # 保存最后一个块
            if current_section and current_chunk:
                chunk_content = '\n'.join(current_chunk).strip()
                if chunk_content:
                    chunks.append(create_intelligent_chunk(
                        chunk_content, chunk_keywords, current_section
                    ))

        except Exception as e:
            print(f"[ERROR] 读取文件 {file_path} 时出错: {e}")

    print(f"[INFO] 成功创建 {len(chunks)} 个知识块")
    return chunks

def is_important_heading(line):
    """判断是否是重要的知识标题"""
    important_patterns = [
        r'^一、',  # 一级标题
        r'^（一）',  # 二级标题
        r'^二、',
        r'^（二）',
        r'^三、',
        r'^（三）',
        r'^定义',
        r'^特征',
        r'^特点',
        r'^主要',
        r'^核心',
        r'^代表',
        r'^人物',  # 添加人物相关标题
        r'^作曲家',  # 添加作曲家相关标题
    ]
    return any(re.match(pattern, line) for pattern in important_patterns)

def extract_keywords_from_heading(heading):
    """从标题中提取关键词"""
    # 移除标点符号和数字
    cleaned = re.sub(r'[一、（）、\d、]', '', heading)
    # 分解成关键词
    keywords = [word for word in cleaned.split() if len(word) > 1]
    return keywords

def create_intelligent_chunk(content, keywords, section):
    """创建智能知识块"""
    # 计算重要性
    importance = calculate_importance(content)

    # 如果没有关键词，从内容中提取
    if not keywords:
        keywords = extract_keywords_from_content(content)

    return KnowledgeChunk(
        content=content,
        keywords=keywords,
        section=section,
        importance=importance
    )

def calculate_importance(content):
    """计算内容重要性"""
    importance_score = 0

    # 检查重要性关键词
    importance_keywords = [
        '定义', '特征', '特点', '主要', '核心', '代表',
        '重要', '关键', '意义', '影响', '作用', '地位',
        '确立', '发展', '演变', '形成', '开创'
    ]

    for keyword in importance_keywords:
        if keyword in content:
            importance_score += 1

    # 检查是否有详细解释（内容长度也是一个指标）
    if len(content) > 100:
        importance_score += 1
    if len(content) > 300:
        importance_score += 1

    return importance_score

def extract_keywords_from_content(content):
    """从内容中提取关键词"""
    # 简单的关键词提取策略
    keywords = []

    # 提取人名（通常是专有名词）
    names = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', content)
    keywords.extend(names[:5])  # 取前5个

    # 提取重要的音乐术语
    music_terms = [
        '通奏低音', '赋格', '奏鸣曲', '协奏曲', '交响曲',
        '格里高利圣咏', '奥尔加农', '经文歌', '牧歌',
        '和声', '调式', '音程', '节奏', '旋律',
        '巴洛克', '古典主义', '浪漫主义', '文艺复兴'
    ]

    for term in music_terms:
        if term in content and term not in keywords:
            keywords.append(term)

    return keywords[:8]  # 限制关键词数量

def intelligent_retrieve(query, knowledge_chunks):
    """智能检索：找到最相关的知识块"""
    query_lower = query.lower()

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
    person_names = [
        '贝多芬', '莫扎特', '海顿', '巴赫', '亨德尔', '肖邦',
        '李斯特', '瓦格纳', '德彪西', '勋伯格', '帕莱斯特里那',
        '迪法伊', '奥克冈', '佩里', '蒙泰韦尔迪', '吕利', '拉莫',
        '珀塞尔', '科雷利', '维瓦尔第', '韦伯', '门德尔松', '舒曼',
        '舒伯特', '勃拉姆斯', '威尔第', '罗西尼', '贝利尼', '多尼采蒂',
        '马肖', '若斯坎', '兰迪尼', '格里格', '西贝柳斯', '柴可夫斯基',
        '穆索尔斯基', '里姆斯基', '斯特拉文斯基', '普罗科菲耶夫', '肖斯塔科维奇'
    ]

    music_terms = [
        '通奏低音', '赋格', '奏鸣曲', '协奏曲', '交响曲', '弥撒曲',
        '格里高利圣咏', '奥尔加农', '经文歌', '牧歌', '歌剧',
        '和声', '调式', '音程', '节奏', '旋律', '对位法',
        '巴洛克', '古典主义', '浪漫主义', '文艺复兴', '印象主义',
        '表现主义', '十二音', '新古典主义', '标题音乐'
    ]

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

    # 3. 术语匹配 - 给予中等优先级
    if query_entity_type != 'person':
        for term in music_terms:
            if term.lower() in query_lower:
                if term.lower() in chunk.content.lower():
                    entity_types['term'] += 10  # 术语完全匹配给高分
                elif any(word in chunk.content.lower() for word in term.lower().split()):
                    entity_types['term'] += 7  # 术语部分匹配给中分

    # 4. 时期匹配 - 给予确认性权重
    detected_period = identify_period_from_query(query_lower)
    if detected_period and detected_period in chunk.section.lower():
        entity_types['period'] += 8  # 时期匹配给予中等权重

    # 5. 关键词匹配（降低权重，避免误判）
    for keyword in chunk.keywords:
        if keyword.lower() in query_lower:
            entity_types['general'] += 3  # 关键词匹配给低分
        elif any(word in query_lower for word in keyword.lower().split()):
            entity_types['general'] += 1  # 部分匹配给最低分

    # 6. 内容词汇匹配（最低权重）
    query_words = set(query_lower.split())
    for word in query_words:
        if len(word) > 1 and word in chunk.content.lower():
            entity_types['general'] += 0.5

    # 7. 计算总分 - 优先考虑实体匹配
    total_score = sum(entity_types.values())

    # 8. 重要性加权（谨慎使用）
    if entity_types['person'] > 0:
        # 如果匹配到人名，降低重要性权重的影响
        total_score += chunk.importance * 0.1
    else:
        # 否则正常加权
        total_score += chunk.importance * 0.5

    # 保存实体类型信息用于调试
    chunk.entity_types = entity_types

    return total_score

def identify_period_from_query(query_lower):
    """从查询中识别时期"""
    period_mapping = {
        '中世纪': ['中世纪', '格里高利', '圣咏', '教会', '奥尔加农', '经文歌'],
        '文艺复兴': ['文艺复兴', '迪法伊', '勃艮第', '奥克冈', '帕莱斯特里那', '人文主义'],
        '巴洛克': ['巴洛克', '佩里', '蒙泰韦尔迪', '吕利', '拉莫', '珀塞尔', '科雷利', '通奏低音', '赋格', '巴赫', '亨德尔', '维瓦尔第'],
        '古典主义': ['古典主义', '海顿', '莫扎特', '贝多芬', '华美风格', '敏感风格', '曼海姆', '斯塔米茨', '奏鸣曲式', '交响曲', 'CPE巴赫'],
        '浪漫主义': ['浪漫主义', '韦伯', '门德尔松', '舒曼', '肖邦', '李斯特', '瓦格纳', '马勒', '施特劳斯', '情感至上', '标题音乐', '民族主义', '歌剧', '舒伯特', '勃拉姆斯', '威尔第'],
        '20世纪': ['20世纪', '德彪西', '拉威尔', '勋伯格', '表现主义', '十二音', '新古典主义', '梅西安', '艾夫斯', '印象主义', '简约主义', '斯特拉文斯基', '凯奇']
    }

    for period, keywords in period_mapping.items():
        if any(keyword in query_lower for keyword in keywords):
            return period

    return None

def generate_targeted_answer(query, relevant_chunks, question_type):
    """生成针对性的答案 - 改进版"""
    if not relevant_chunks:
        return "该问题不在西方音乐史知识库范围内，请提供与古希腊、中世纪、文艺复兴、巴洛克、古典主义、浪漫主义或20世纪音乐相关的问题。"

    # 1. 分析查询类型
    query_type_enhanced = analyze_query_intent(query)

    # 2. 根据查询意图选择最佳内容
    primary_chunk = select_best_chunk(query, relevant_chunks, query_type_enhanced)
    answer_content = primary_chunk.content

    # 3. 根据问题类型生成不同格式
    if question_type == 'definition':
        return generate_definition_answer(query, answer_content, relevant_chunks)
    elif question_type == 'short_answer':
        return generate_short_answer(query, answer_content, relevant_chunks)
    elif question_type == 'essay':
        return generate_essay_answer(query, answer_content, relevant_chunks)
    else:
        return generate_general_answer(query, answer_content, relevant_chunks)

def analyze_query_intent(query):
    """分析查询意图 - 改进版"""
    query_lower = query.lower()

    # 人名列表
    person_names = [
        '贝多芬', '莫扎特', '海顿', '巴赫', '亨德尔', '肖邦',
        '李斯特', '瓦格纳', '德彪西', '勋伯格', '帕莱斯特里那',
        '迪法伊', '奥克冈', '佩里', '蒙泰韦尔迪', '吕利', '拉莫',
        '珀塞尔', '科雷利', '维瓦尔第', '韦伯', '门德尔松', '舒曼',
        '舒伯特', '勃拉姆斯', '威尔第', '罗西尼', '贝利尼', '多尼采蒂'
    ]

    # 音乐术语列表
    music_terms = [
        '通奏低音', '赋格', '奏鸣曲', '协奏曲', '交响曲', '弥撒曲',
        '格里高利圣咏', '奥尔加农', '经文歌', '牧歌', '歌剧',
        '和声', '调式', '音程', '节奏', '旋律', '对位法'
    ]

    # 分析意图
    intent = {
        'type': 'general',
        'confidence': 'low'
    }

    # 1. 检查是否为人名查询
    for person in person_names:
        if person.lower() in query_lower:
            intent = {
                'type': 'person',
                'entity': person,
                'confidence': 'high'
            }
            break

    # 2. 如果不是人名，检查是否为术语查询
    if intent['type'] == 'general':
        for term in music_terms:
            if term.lower() in query_lower:
                intent = {
                    'type': 'term',
                    'entity': term,
                    'confidence': 'medium'
                }
                break

    return intent

def select_best_chunk(query, relevant_chunks, query_intent):
    """根据查询意图选择最佳知识块 - 改进版"""
    if not relevant_chunks:
        return None

    # 如果是人名查询，优先选择包含该人名的块
    if query_intent['type'] == 'person':
        person_name = query_intent['entity']

        # 1. 首先寻找直接包含该人名的块
        for chunk in relevant_chunks:
            if person_name.lower() in chunk.content.lower():
                return chunk

        # 2. 如果没有找到，寻找在人物列表或作曲家相关的块
        for chunk in relevant_chunks:
            content_lower = chunk.content.lower()
            # 检查是否为人物描述或作曲家介绍
            if any(indicator in content_lower for indicator in [
                '人物', '作曲家', '代表', '主要', '重要', '时期'
            ]):
                return chunk

        # 3. 如果都没有，检查知识块是否与该人物相关的时期匹配
        detected_period = identify_period_from_query(query.lower())
        if detected_period:
            for chunk in relevant_chunks:
                if detected_period in chunk.section.lower():
                    return chunk

    # 如果是术语查询，优先选择定义该术语的块
    if query_intent['type'] == 'term':
        for chunk in relevant_chunks:
            # 查找包含"定义"、"是什么"、"指"等内容的块
            if any(marker in chunk.content for marker in ['定义', '是指', '为', '是']):
                return chunk

    # 默认返回相似度最高的块
    return relevant_chunks[0]

def generate_definition_answer(query, content, relevant_chunks):
    """生成名词解释答案"""
    # 提取核心定义（通常是前几句）
    lines = content.split('\n')
    definition_lines = []

    for line in lines[:8]:  # 取前8行
        line_clean = line.strip()
        if line_clean and not line_clean.startswith(('一、', '（一）', '二、', '（二）')):
            if len(line_clean) > 10:  # 确保有实质内容
                definition_lines.append(line_clean)
                if len(definition_lines) >= 3:
                    break

    if definition_lines:
        definition = '\n'.join(definition_lines)
        return f"**【名词解释】**\n\n{query}\n\n{definition}"
    else:
        return f"**【名词解释】**\n\n{query}\n\n{content[:200]}..."

def generate_short_answer(query, content, relevant_chunks):
    """生成简答题答案"""
    # 提取关键特征要点
    lines = content.split('\n')
    key_points = []

    for line in lines:
        line_clean = line.strip()
        # 识别特征、特点类内容
        if any(keyword in line_clean for keyword in ['特征', '特点', '主要', '核心', '重要', '代表']):
            if line_clean and len(line_clean) > 10:
                key_points.append(line_clean)
                if len(key_points) >= 4:  # 限制要点数量
                    break

    if key_points:
        points_text = '\n'.join([f"• {point}" for point in key_points])
        return f"**【简答题】**\n\n{query}\n\n{points_text}"
    else:
        return f"**【简答题】**\n\n{query}\n\n{content[:300]}..."

def generate_essay_answer(query, content, relevant_chunks):
    """生成论述题答案"""
    # 对于论述题，使用完整的第一个相关块
    # 如果有多个相关块，整合它们
    if len(relevant_chunks) > 1:
        combined_content = '\n\n'.join([chunk.content for chunk in relevant_chunks[:2]])
        return f"**【论述题】**\n\n{query}\n\n{combined_content}"
    else:
        return f"**【论述题】**\n\n{query}\n\n{content}"

def generate_general_answer(query, content, relevant_chunks):
    """生成一般性问题答案"""
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
        relevant_text = '\n'.join(relevant_lines)
        return f"**【综合回答】**\n\n{query}\n\n{relevant_text}"
    else:
        return f"**【综合回答】**\n\n{query}\n\n{content[:250]}..."

def classify_question_type(question):
    """题目分类"""
    question_lower = question.lower()

    if any(keyword in question_lower for keyword in ['什么是', '定义', '名词解释', '解释', '概念', '含义', '术语']):
        return 'definition'

    elif any(keyword in question_lower for keyword in ['特点', '特征', '风格', '主要', '简述', '简答', '谈谈', '概括']):
        return 'short_answer'

    elif any(keyword in question_lower for keyword in ['论述', '分析', '发展', '演变', '过程', '历史', '影响', '意义', '贡献', '作用', '重要性']):
        return 'essay'

    elif any(keyword in question_lower for keyword in ['对比', '比较', '区别', '差异', '相同', '不同']):
        return 'comparison'

    else:
        return 'general'

class AdvancedRAGHandler(BaseHTTPRequestHandler):
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
        if self.path == '/api/health':
            # API健康检查端点
            self._set_headers()
            response = {
                'status': 'ok',
                'message': '西方音乐史RAG系统运行正常（高级版本）',
                'server': 'Python http.server',
                'version': '7.0.0',
                'knowledge_base': '基于智能切块的专业知识库',
                'data_sources': KNOWLEDGE_FILES,
                'features': [
                    '智能文本切块',
                    '细粒度知识检索',
                    '针对性答案生成',
                    '多维度相似度计算',
                    '智能问答体验'
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

                        # 3. 生成针对性答案
                        answer = generate_targeted_answer(query, relevant_chunks, question_type)

                        # 4. 获取时期信息
                        detected_period = identify_period_from_query(query.lower())

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
                            'answer': answer,
                            'period': detected_period,
                            'question_type': question_type,
                            'retrieved_chunks_count': len(relevant_chunks),
                            'best_chunk_score': relevant_chunks[0].similarity_score if relevant_chunks else 0,
                            'ai_generated': False,
                            'model': '智能检索增强的音乐史知识库',
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

def run_advanced_server():
    print("=" * 70)
    print("西方音乐史RAG问答系统 - 高级版本")
    print("=" * 70)
    print()

    print("系统特性:")
    print("  - 智能文本切块：按知识点分块，不是整章")
    print("  - 细粒度检索：找到最相关的知识段落")
    print("  - 针对性答案：根据问题类型生成格式化回答")
    print("  - 多维度相似度：关键词匹配 + 内容匹配 + 时期匹配")
    print("  - 智能问答体验：真正的RAG，不是文档检索")
    print()

    # 从环境变量获取端口，默认8000（Render会提供PORT环境变量）
    PORT = int(os.environ.get('PORT', 8000))
    print(f"[INFO] 端口: {PORT}")
    print(f"[INFO] 环境: {'生产环境' if os.environ.get('PORT') else '开发环境'}")

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

        httpd = HTTPServer(server_address, AdvancedRAGHandler)
        print("=" * 70)
        print("高级RAG服务器启动成功！")
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
        # 将错误输出到stderr，这样在Render上也能看到
        print(f"[ERROR] 详细错误: {str(e)}", file=sys.stderr)
        print(f"[ERROR] 错误类型: {type(e).__name__}", file=sys.stderr)
        input("按回车键退出...")

if __name__ == "__main__":
    run_advanced_server()
