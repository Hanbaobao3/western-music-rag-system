"""
考研西方音乐史问答系统
专业、严谨、精确的问答助手
"""
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# 考研西方音乐史知识库
RAG_KNOWLEDGE_BASE = {
    'ancient_greek_roman': {
        'definition': '古希腊、古罗马音乐（公元前8世纪-公元5世纪）',
        'background': '古希腊音乐是西方音乐史的源头，强调音乐与哲学、数学的结合。古罗马音乐继承并发展了古希腊音乐传统。',
        'characteristics': [
            '音乐与哲学紧密结合，认为音乐具有教化作用',
            '使用单声部音乐形式，旋律性强',
            '器乐主要有里拉琴、基萨拉琴、阿夫洛斯管',
            '音乐理论发展完善，包括调式、音程理论',
            '戏剧表演中音乐与舞蹈、诗歌结合'
        ],
        'representative': ['毕达哥拉斯（音乐理论家）', '亚里士多塞乌斯（音乐理论）'],
        'significance': '为西方音乐理论奠定基础，影响中世纪乃至文艺复兴音乐发展。'
    },
    'medieval': {
        'definition': '中世纪音乐（5世纪-14世纪）',
        'background': '中世纪音乐以教会音乐为主导，格里高利圣咏是核心。后期复调音乐开始发展。',
        'characteristics': [
            '以单声部格里高利圣咏为主，拉丁文歌词',
            '教会调式系统（多里安调式、弗里吉亚调式等）',
            '记谱法从纽姆记谱发展到线谱',
            '复调音乐在9世纪后开始发展（奥尔加农、狄斯康特）',
            '音乐服务宗教，具有庄严、神圣的风格'
        ],
        'representative': ['圣安布罗斯', '格里高利一世', '莱奥南（巴黎圣母院乐派）'],
        'works': ['《格里高利圣咏》', '《奥尔加农》'],
        'significance': '建立西方教会音乐传统，为复调音乐发展奠定基础。'
    },
    'renaissance': {
        'definition': '文艺复兴音乐（15世纪-16世纪）',
        'background': '人文主义思想兴起，音乐从宗教向世俗发展。复调技术达到高峰。',
        'characteristics': [
            '人文主义影响，世俗音乐创作活跃',
            '复调技术高度发展，声部关系更加清晰',
            '牧歌、香颂等世俗体裁繁荣',
            '器乐音乐开始独立发展',
            '和声理论开始形成',
            '音乐印刷术发展推动音乐传播'
        ],
        'representative': ['若斯坎·德·普雷', '帕莱斯特里纳', '威廉·伯德', '维拉尔特'],
        'works': ['《教皇弥撒》', '《马德利加尔》', '《牧歌集》'],
        'significance': '复调音乐技术达到巅峰，为巴洛克音乐奠定基础。'
    },
    'baroque': {
        'definition': '巴洛克音乐（1600年-1750年）',
        'background': '巴洛克时期音乐追求华丽、戏剧性效果，强调情感表达。器乐和歌剧快速发展。',
        'characteristics': [
            '使用通奏低音，建立功能和声体系',
            '协奏曲、奏鸣曲、赋格等体裁确立',
            '歌剧诞生并快速发展（卡梅拉塔会社）',
            '复调音乐与主调音乐并存',
            '音乐强调装饰性和戏剧性对比',
            '大小调体系确立',
            '十二平均律理论完善'
        ],
        'representative': ['巴赫（1685-1750）', '亨德尔（1685-1759）', '维瓦尔第（1678-1741）', '斯卡拉蒂（1685-1757）'],
        'works': ['《平均律钢琴曲集》', '《勃兰登堡协奏曲》', '《弥赛亚》', '《四季》'],
        'significance': '确立西方功能和声体系，为古典主义音乐奠定基础。'
    },
    'classical': {
        'definition': '古典主义音乐（1750年-1820年）',
        'background': '启蒙运动影响，音乐追求理性、均衡、清晰。维也纳古典乐派达到高峰。',
        'characteristics': [
            '音乐结构清晰，逻辑性强，追求理性与均衡',
            '奏鸣曲式确立并广泛应用于交响曲、奏鸣曲、协奏曲',
            '和声功能明确，调性转换规范',
            '旋律优美，节奏规整',
            '室内乐、交响曲、协奏曲、歌剧全面发展',
            '钢琴成为重要独奏乐器',
            '乐队编制相对固定（双管制）'
        ],
        'representative': ['海顿（1732-1809）', '莫扎特（1756-1791）', '贝多芬（1770-1827）'],
        'works': ['《伦敦交响曲》', '《魔笛》', '《第九交响曲》', '《钢琴奏鸣曲》'],
        'significance': '确立古典主义音乐范式，影响后世音乐发展。'
    },
    'romantic': {
        'definition': '浪漫主义音乐（1820年-1900年）',
        'background': '浪漫主义强调个人情感表达，突破古典主义束缚。音乐形式和和声都有重大发展。',
        'characteristics': [
            '强调个人情感和主观表达',
            '和声更加丰富复杂，半音化和声发展',
            '节奏更加自由，速度变化频繁',
            '标题音乐发展，文学与音乐结合紧密',
            '钢琴音乐达到高峰（肖邦、李斯特）',
            '民族乐派兴起，民族特色显著',
            '歌剧、交响诗、艺术歌曲等体裁繁荣'
        ],
        'representative': ['肖邦（1810-1849）', '李斯特（1811-1886）', '瓦格纳（1813-1883）', '勃拉姆斯（1833-1897）', '柴可夫斯基（1840-1893）'],
        'works': ['《夜曲》', '《匈牙利狂想曲》', '《特里斯坦与伊索尔德》', '《第四交响曲》'],
        'significance': '推动音乐向个性化、多样化发展，为20世纪音乐奠定基础。'
    },
    'modern_20th': {
        'definition': '20世纪及现代音乐（1900年至今）',
        'background': '20世纪音乐多元化发展，突破传统调性和声体系。各种现代技法层出不穷。',
        'characteristics': [
            '音乐风格多元化，打破传统调性体系',
            '十二音序列主义（勋伯格学派）',
            '印象主义强调色彩和氛围（德彪西）',
            '表现主义强调主观情感和心理表达',
            '新古典主义回归古典形式和结构',
            '电子音乐、计算机音乐等新技术应用',
            '民族音乐元素广泛融入',
            '节奏复杂化，不规则节拍使用'
        ],
        'representative': ['德彪西（1862-1918）', '斯特拉文斯基（1882-1971）', '勋伯格（1874-1951）', '巴托克（1881-1945）', '梅西安（1908-1992）'],
        'works': ['《牧神午后》', '《春之祭》', '《月迷彼埃罗》', '《为弦乐器、打击乐和钢片琴的音乐》'],
        'significance': '打破传统音乐范式，开辟音乐表现新领域。'
    }
}

# 题型分类逻辑
def classify_question_type(question):
    """根据问题内容判断题型"""
    question_lower = question.lower()

    # 名词解释类
    if any(keyword in question_lower for keyword in ['什么是', '定义', '名词解释', '解释', '概念', '含义']):
        return 'definition'

    # 简答题类
    elif any(keyword in question_lower for keyword in ['特点', '特征', '风格', '主要', '概括', '简述', '简答', '谈谈']):
        return 'short_answer'

    # 论述题类
    elif any(keyword in question_lower for keyword in ['论述', '分析', '发展', '演变', '过程', '历史', '影响', '意义', '贡献']):
        return 'essay'

    # 对比题类
    elif any(keyword in question_lower for keyword in ['对比', '比较', '区别', '差异', '相同', '不同']):
        return 'comparison'

    # 默认为简答题
    else:
        return 'short_answer'

def identify_period(question):
    """识别问题对应的音乐时期"""
    question_lower = question.lower()

    # 古希腊古罗马
    if any(keyword in question_lower for keyword in ['古希腊', '古罗马', '希腊', '罗马', '毕达哥拉斯', '亚里士多塞乌斯']):
        return 'ancient_greek_roman'

    # 中世纪
    elif any(keyword in question_lower for keyword in ['中世纪', '格里高利', '圣咏', '教会音乐', '奥尔加农', '狄斯康特']):
        return 'medieval'

    # 文艺复兴
    elif any(keyword in question_lower for keyword in ['文艺复兴', '人文主义', '帕莱斯特里纳', '若斯坎', '牧歌', '香颂']):
        return 'renaissance'

    # 巴洛克
    elif any(keyword in question_lower for keyword in ['巴洛克', '巴赫', '亨德尔', '通奏低音', '协奏曲', '赋格', '歌剧', '维瓦尔第', '斯卡拉蒂']):
        return 'baroque'

    # 古典主义
    elif any(keyword in question_lower for keyword in ['古典主义', '海顿', '莫扎特', '贝多芬', '奏鸣曲式', '交响曲', '维也纳']):
        return 'classical'

    # 浪漫主义
    elif any(keyword in question_lower for keyword in ['浪漫主义', '肖邦', '李斯特', '瓦格纳', '柴可夫斯基', '勃拉姆斯', '标题音乐', '民族乐派']):
        return 'romantic'

    # 20世纪及现代
    elif any(keyword in question_lower for keyword in ['20世纪', '现代', '德彪西', '斯特拉文', '印象主义', '表现主义', '新古典主义', '勋伯格', '十二音']):
        return 'modern_20th'

    return None

def generate_answer(question, period_key):
    """根据考研标准生成答案"""

    # 识别问题类型
    question_type = classify_question_type(question)

    # 如果无法识别时期，返回标准回复
    if not period_key or period_key not in RAG_KNOWLEDGE_BASE:
        return "该内容不在本次西方音乐史知识库范围内，请提供相关资料。"

    knowledge = RAG_KNOWLEDGE_BASE[period_key]

    # 根据不同题型生成答案
    if question_type == 'definition':
        # 名词解释：定义 + 特征 + 代表人物/作品
        answer = f"**【名词解释】** {knowledge['definition']}\n\n"
        answer += "**基本特征：**\n"
        for i, char in enumerate(knowledge['characteristics'][:3], 1):
            answer += f"{i}. {char}\n"
        answer += f"\n**代表人物/作品：** {', '.join(knowledge['representative'][:2])}"
        return answer

    elif question_type == 'short_answer':
        # 简答题：直接给出要点
        answer = f"**【简答题】** {knowledge['definition']}\n\n"
        answer += "**主要特征：**\n"
        for i, char in enumerate(knowledge['characteristics'], 1):
            answer += f"{i}. {char}\n"
        answer += f"\n**历史意义：** {knowledge['significance']}"
        return answer

    elif question_type == 'essay':
        # 论述题：背景 — 内容 — 特征 — 意义
        answer = f"**【论述题】**\n\n"
        answer += f"**一、背景**\n{knowledge['background']}\n\n"
        answer += f"**二、主要内容**\n"
        for i, char in enumerate(knowledge['characteristics'][:4], 1):
            answer += f"{i}. {char}\n"
        answer += f"\n**三、风格特征**\n"
        for i, char in enumerate(knowledge['characteristics'][4:], 5):
            answer += f"{i}. {char}\n"
        answer += f"\n**四、代表人物与作品**\n"
        answer += f"人物：{', '.join(knowledge['representative'])}\n"
        if 'works' in knowledge:
            answer += f"作品：{', '.join(knowledge['works'][:3])}\n"
        answer += f"\n**五、历史意义**\n{knowledge['significance']}"
        return answer

    elif question_type == 'comparison':
        # 对比题：明确比较维度
        answer = f"**【对比题】**\n\n"
        answer += f"本问题涉及{knowledge['definition']}的对比分析。\n\n"
        answer += "**比较维度：**\n"
        answer += "1. 时期：时间跨度\n"
        answer += "2. 风格：音乐特征\n"
        answer += "3. 体裁：主要音乐形式\n"
        answer += "4. 技法：创作技法特点\n\n"
        answer += "**请明确具体对比对象，以便提供详细对比分析。**"
        return answer

    else:
        # 默认简答题
        return generate_answer(question, period_key)

def get_mock_retrieved_docs(period_key):
    """获取模拟的检索文档"""
    if not period_key or period_key not in RAG_KNOWLEDGE_BASE:
        return []

    knowledge = RAG_KNOWLEDGE_BASE[period_key]
    docs = [
        {
            'content': f"【知识库片段1】{knowledge['definition']}",
            'similarity': 0.95
        },
        {
            'content': f"【知识库片段2】{knowledge['background']}",
            'similarity': 0.89
        }
    ]
    return docs

class RAGHandler(BaseHTTPRequestHandler):
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
            response = {
                'status': 'ok',
                'message': '考研西方音乐史问答系统运行正常',
                'server': 'Python http.server',
                'version': '3.0.0',
                'knowledge_base': '考研西方音乐史知识库',
                'question_types': ['名词解释', '简答题', '论述题', '对比题']
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

    def do_POST(self):
        if self.path == '/api/query':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    request_data = json.loads(post_data)

                    query = request_data.get('query', '').strip()

                    if query:
                        # 识别时期并生成答案
                        period_key = identify_period(query)
                        answer = generate_answer(query, period_key)

                        self._set_headers(200)
                        response = {
                            'success': True,
                            'answer': answer,
                            'period': period_key,
                            'question_type': classify_question_type(query),
                            'retrieved_docs': get_mock_retrieved_docs(period_key),
                            'ai_generated': False,
                            'model': '考研西方音乐史知识库',
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
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': '路径不存在'}).encode())

def run_server():
    print("=" * 70)
    print("考研西方音乐史问答系统")
    print("=" * 70)
    print()

    PORT = 5001
    server_address = ('127.0.0.1', PORT)
    print(f"启动服务器在 http://127.0.0.1:{PORT}")
    print(f"API接口: http://127.0.0.1:{PORT}/api/query")
    print()

    print("系统特点:")
    print("  - 专业严谨：严格依据考研音乐史知识库作答")
    print("  - 智能识别：自动识别题型（名词解释、简答、论述、对比）")
    print("  - 时期分类：涵盖古希腊至现代音乐各时期")
    print("  - 结构规范：符合考研答题标准")
    print()

    print("支持的题型:")
    print("  - 名词解释：定义 + 特征 + 代表人物/作品")
    print("  - 简答题：直接给出要点，条理清晰")
    print("  - 论述题：背景 — 内容 — 特征 — 意义")
    print("  - 对比题：明确比较维度分析")
    print()

    try:
        httpd = HTTPServer(server_address, RAGHandler)
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
    run_server()
