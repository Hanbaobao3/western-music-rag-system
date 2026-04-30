"""
Prompt组装器
根据检索到的文档和用户问题构建高质量的Prompt
"""
import logging
from typing import List, Dict, Any, Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptAssembler:
    """Prompt组装器类"""

    def __init__(self,
                 system_prompt: Optional[str] = None,
                 max_context_length: int = 3000):
        """
        初始化Prompt组装器

        Args:
            system_prompt: 系统提示词
            max_context_length: 最大上下文长度（字符数）
        """
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.max_context_length = max_context_length

        logger.info(f"Prompt组装器初始化完成 - 最大上下文长度: {max_context_length}")

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是一个专业的问答助手，擅长基于提供的文档内容回答用户的问题。

请遵循以下原则：
1. 仅基于提供的文档内容回答问题，不要添加文档中未提及的信息
2. 如果文档中没有相关信息，请明确告知用户
3. 回答要准确、清晰、有条理
4. 可以适当引用文档中的具体内容来支持你的回答
5. 对于复杂问题，可以分点列出答案
6. 保持语言自然流畅，避免机械地拼接文档内容
"""

    def assemble_prompt(self,
                    query: str,
                    retrieved_docs: List[Dict[str, Any]],
                    conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        组装完整的Prompt

        Args:
            query: 用户查询
            retrieved_docs: 检索到的文档列表
            conversation_history: 对话历史（用于多轮对话）

        Returns:
            完整的Prompt字符串
        """
        logger.info(f"开始组装Prompt - 查询: {query}")

        # 构建系统提示词
        prompt_parts = [self.system_prompt]

        # 添加对话历史（如果有）
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            prompt_parts.append(f"## 对话历史\n{history_text}")

        # 添加检索到的文档
        docs_text = self._format_retrieved_docs(retrieved_docs)
        prompt_parts.append(f"## 参考文档\n{docs_text}")

        # 添加用户问题
        prompt_parts.append(f"## 用户问题\n{query}")

        # 添加回答要求
        prompt_parts.append("## 回答要求\n请基于上述参考文档，用清晰、准确的语言回答用户的问题。")

        # 组合所有部分
        full_prompt = "\n\n".join(prompt_parts)

        logger.info(f"Prompt组装完成，长度: {len(full_prompt)} 字符")
        return full_prompt

    def _format_retrieved_docs(self, docs: List[Dict[str, Any]]) -> str:
        """格式化检索到的文档"""
        if not docs:
            return "未找到相关参考文档。"

        formatted_docs = []
        total_length = 0

        for i, doc in enumerate(docs, 1):
            # 检查是否超过长度限制
            doc_text = f"[文档 {i}] (相关度: {doc['similarity']:.2%})\n{doc['content']}\n"

            if total_length + len(doc_text) > self.max_context_length:
                logger.info(f"达到最大长度限制，已包含 {i-1} 个文档")
                break

            formatted_docs.append(doc_text)
            total_length += len(doc_text)

        return "\n".join(formatted_docs)

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        if not history:
            return ""

        formatted_history = []
        for i, turn in enumerate(history, 1):
            user_q = turn.get('user', '')
            assistant_a = turn.get('assistant', '')
            formatted_history.append(f"[对话 {i}]\n用户: {user_q}\n助手: {assistant_a}")

        return "\n\n".join(formatted_history)

    def create_rag_prompt_template(self) -> str:
        """
        创建RAG专用的Prompt模板

        Returns:
            RAG Prompt模板
        """
        template = """{system_prompt}

## 对话历史
{conversation_history}

## 参考文档
{retrieved_docs}

## 用户问题
{query}

## 回答要求
1. 仔细阅读参考文档，理解文档内容
2. 基于文档内容回答问题，不要编造信息
3. 如果文档内容不足以回答问题，明确告知用户
4. 回答要准确、清晰、有条理
5. 可以引用文档中的具体内容来支持回答
"""
        return template

    def create_qa_prompt(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """
        创建简洁的问答Prompt

        Args:
            query: 用户问题
            docs: 检索到的文档

        Returns:
            问答Prompt
        """
        prompt = f"""请根据以下参考文档回答问题：

参考文档：
{self._format_retrieved_docs(docs)}

问题：{query}

要求：
- 基于文档内容回答
- 如果文档中没有相关信息，请明确说明
- 回答要准确、清晰"""
        return prompt

    def create_chain_of_thought_prompt(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """
        创建思维链Prompt

        Args:
            query: 用户问题
            docs: 检索到的文档

        Returns:
            思维链Prompt
        """
        prompt = f"""请基于以下参考文档回答问题，并展示你的思考过程：

参考文档：
{self._format_retrieved_docs(docs)}

问题：{query}

请按以下步骤回答：
1. 分析问题，明确问题的核心要求
2. 从参考文档中查找相关信息
3. 整理找到的信息，构建答案框架
4. 最终给出清晰、准确的回答

开始回答："""
        return prompt

    def optimize_prompt_for_length(self, prompt: str, target_length: int = 2000) -> str:
        """
        优化Prompt长度

        Args:
            prompt: 原始Prompt
            target_length: 目标长度

        Returns:
            优化后的Prompt
        """
        if len(prompt) <= target_length:
            return prompt

        # 如果超长，优先缩短文档部分
        logger.info(f"Prompt长度 {len(prompt)} 超过目标 {target_length}，开始优化")

        lines = prompt.split('\n')
        optimized_lines = []
        current_length = 0

        for line in lines:
            if current_length + len(line) + 1 <= target_length:
                optimized_lines.append(line)
                current_length += len(line) + 1
            else:
                # 如果添加这行会超长，检查是否是文档部分
                if '文档' in line:
                    optimized_lines.append("... [文档内容已截断]")
                break

        optimized_prompt = '\n'.join(optimized_lines)
        logger.info(f"Prompt优化完成: {len(prompt)} -> {len(optimized_prompt)} 字符")

        return optimized_prompt


def main():
    """测试Prompt组装器"""
    # 创建测试检索结果
    test_docs = [
        {
            'content': '巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。代表作曲家有巴赫、亨德尔等。',
            'metadata': {'source': 'music_history.pdf', 'page': 5},
            'similarity': 0.89,
            'chunk_id': 'doc_1',
            'chunk_index': 0
        },
        {
            'content': '巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。',
            'metadata': {'source': 'music_history.pdf', 'page': 6},
            'similarity': 0.85,
            'chunk_id': 'doc_2',
            'chunk_index': 1
        }
    ]

    # 创建Prompt组装器
    assembler = PromptAssembler(max_context_length=500)

    # 测试基础Prompt组装
    query = "巴洛克音乐有什么特点？"
    prompt = assembler.assemble_prompt(query, test_docs)

    print("=" * 60)
    print("组装的Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    # 测试不同的Prompt类型
    print("\n【问答Prompt】")
    print(assembler.create_qa_prompt(query, test_docs))

    print("\n【思维链Prompt】")
    print(assembler.create_chain_of_thought_prompt(query, test_docs))


if __name__ == "__main__":
    main()