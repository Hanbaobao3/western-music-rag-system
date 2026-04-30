"""
测试知识库加载
"""
import os

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
                    section_content.append(line)

            # 保存最后一个章节
            if current_section and section_content:
                knowledge_base[current_section] = '\n'.join(section_content).strip()

        except Exception as e:
            print(f"[ERROR] 读取文件 {file_path} 时出错: {e}")

    return knowledge_base

print("=" * 60)
print("知识库加载测试")
print("=" * 60)
print()

knowledge_base = load_knowledge_base()

print(f"成功加载 {len(knowledge_base)} 个章节:")
print()
for i, chapter in enumerate(knowledge_base.keys(), 1):
    print(f"{i}. {chapter}")
    print(f"   内容长度: {len(knowledge_base[chapter])} 字符")
    print()

print("=" * 60)
print("测试查询")
print("=" * 60)

test_periods = [
    "古代与中世纪音乐（公元前～1400年）",
    "巴洛克时期音乐（约1600—1750年）"
]

for period in test_periods:
    if period in knowledge_base:
        print(f"✓ 找到章节: {period}")
        print(f"  前100字符: {knowledge_base[period][:100]}...")
        print()
    else:
        print(f"✗ 未找到章节: {period}")
        print()
