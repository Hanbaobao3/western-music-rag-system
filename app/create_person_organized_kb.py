"""
创建按人物和主题组织的知识库
这样可以解决"贝多芬"这类查询的准确匹配问题
"""
import os
import re

DATA_DIR = r"E:\ai-apps\rag-system\data"
INPUT_FILES = [
    os.path.join(DATA_DIR, 'music history.txt'),
    os.path.join(DATA_DIR, 'music history 2.txt')
]
OUTPUT_FILE = os.path.join(DATA_DIR, 'music_history_by_person.txt')

def extract_person_info(content):
    """从内容中提取人物信息"""
    persons = []

    # 主要作曲家列表
    person_patterns = {
        '巴赫': r'巴赫.*?(?:约翰|塞巴斯蒂安|JS)',
        '亨德尔': r'亨德尔.*?(?:乔治|弗里德里希)',
        '维瓦尔第': r'维瓦尔第.*?(?:安东尼奥)',
        '贝多芬': r'贝多芬.*?(?:路德维希)',
        '莫扎特': r'莫扎特.*?(?:沃尔夫冈|阿马多伊斯)',
        '海顿': r'海顿.*?(?:约瑟夫|弗朗茨)',
        '舒伯特': r'舒伯特.*?(?:弗朗茨)',
        '肖邦': r'肖邦.*?(?:弗雷德里克)',
        '李斯特': r'李斯特.*?(?:弗朗茨)',
        '瓦格纳': r'瓦格纳.*?(?:理查德)',
        '德彪西': r'德彪西.*?(?:克劳德)',
        '舒曼': r'舒曼.*?(?:罗伯特|克拉拉)',
        '勃拉姆斯': r'勃拉姆斯.*?(?:约翰内斯)',
        '柴可夫斯基': r'柴可夫斯基.*?(?:彼得|伊里奇)',
        '门德尔松': r'门德尔松.*?(?:菲利克斯)',
        '格里格': r'格里格.*?(?:爱德华)',
        '马肖': r'马肖.*?(?:克劳德)',
        '斯特拉文斯基': r'斯特拉文斯基.*?(?:伊戈尔)'
    }

    content_lower = content.lower()

    for person_name, pattern in person_patterns.items():
        if re.search(pattern, content_lower):
            # 提取相关段落
            lines = content.split('\n')
            person_content = []
            in_person_section = False

            for line in lines:
                if person_name in line or any(name in line for name in person_patterns.keys()):
                    in_person_section = True
                    person_content.append(line)
                elif in_person_section:
                    if line.strip():
                        person_content.append(line)

            if person_content:
                persons.append({
                    'name': person_name,
                    'content': '\n'.join(person_content).strip()
                })

    return persons

def extract_concept_info(content):
    """从内容中提取概念/术语信息"""
    concepts = []

    concept_patterns = {
        '奏鸣曲式': r'奏鸣曲式|sonata\s+form',
        '通奏低音': r'通奏低音|basso\s+continuo',
        '赋格': r'赋格|fugue',
        '格里高利圣咏': r'格里高利|gregorian',
        '奥尔加农': r'奥尔加农|organum',
        '对位法': r'对位法|counterpoint',
        '歌剧': r'歌剧|opera',
        '交响曲': r'交响曲|symphony',
        '和声': r'和声|harmony',
        '调式': r'调式|mode',
        '音乐史': r'音乐史|history'
    }

    content_lower = content.lower()

    for concept_name, pattern in concept_patterns.items():
        if re.search(pattern, content_lower):
            # 提取相关段落
            lines = content.split('\n')
            concept_content = []
            in_concept_section = False

            for line in lines:
                if concept_name in line.lower() or re.search(pattern, line.lower()):
                    in_concept_section = True
                    concept_content.append(line)
                elif in_concept_section:
                    if line.strip():
                        concept_content.append(line)

            if concept_content:
                concepts.append({
                    'name': concept_name,
                    'content': '\n'.join(concept_content).strip()
                })

    return concepts

def create_organized_kb():
    """创建按人物和主题组织的知识库"""
    print("=" * 70)
    print("创建按人物和主题组织的音乐史知识库")
    print("=" * 70)

    all_content = ""

    # 读取所有原始文件
    for file_path in INPUT_FILES:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                all_content += f.read() + "\n\n"

    # 提取人物信息
    persons = extract_person_info(all_content)
    print(f"找到 {len(persons)} 位作曲家")

    # 提取概念信息
    concepts = extract_concept_info(all_content)
    print(f"找到 {len(concepts)} 个音乐概念")

    # 创建按人物和主题组织的内容
    organized_content = []

    # 按时期组织
    organized_content.append("=" * 70)
    organized_content.append("西方音乐史 - 按人物和主题组织")
    organized_content.append("=" * 70)
    organized_content.append("\n")

    # 人物部分
    organized_content.append("【重要作曲家】")
    organized_content.append("\n")
    for i, person in enumerate(persons, 1):
        organized_content.append(f"人物{i}：{person['name']}")
        organized_content.append(f"内容：{person['content'][:200]}...")
        organized_content.append("\n")

    # 概念部分
    organized_content.append("\n")
    organized_content.append("【音乐概念与术语】")
    organized_content.append("\n")
    for i, concept in enumerate(concepts, 1):
        organized_content.append(f"概念{i}：{concept['name']}")
        organized_content.append(f"定义：{concept['content'][:150]}...")
        organized_content.append("\n")

    # 保存到文件
    output_content = '\n'.join(organized_content)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"\n已创建按人物和主题组织的知识库：")
    print(f"文件路径：{OUTPUT_FILE}")
    print(f"包含 {len(persons)} 位作曲家和 {len(concepts)} 个音乐概念")

if __name__ == "__main__":
    create_organized_kb()
