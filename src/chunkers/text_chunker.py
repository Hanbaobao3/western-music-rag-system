"""
文本切块器
将长文档智能分割为语义完整的小块
"""
import re
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from ..parsers.pdf_parser import DocumentChunk

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """文本切块数据结构"""
    content: str
    metadata: Dict[str, Any]
    chunk_index: int
    chunk_id: str
    token_count: int


class TextChunker:
    """文本切块器类"""

    def __init__(self,
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 separator: str = "\n\n",
                 use_semantic: bool = True):
        """
        初始化文本切块器

        Args:
            chunk_size: 每块的最大token数
            chunk_overlap: 块之间的重叠token数
            separator: 分隔符，用于优先分割位置
            use_semantic: 是否使用语义分块
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        self.use_semantic = use_semantic
        logger.info(f"文本切块器初始化完成 - 块大小: {chunk_size}, 重叠: {chunk_overlap}")

    def chunk_documents(self, documents: List[DocumentChunk]) -> List[TextChunk]:
        """
        对文档列表进行切块

        Args:
            documents: 文档块列表

        Returns:
            切块后的文本块列表
        """
        logger.info(f"开始切块 {len(documents)} 个文档")

        all_chunks = []
        chunk_index = 0

        for doc in documents:
            chunks = self._chunk_single_document(doc, chunk_index)
            all_chunks.extend(chunks)
            chunk_index += len(chunks)

        logger.info(f"切块完成，共生成 {len(all_chunks)} 个文本块")
        return all_chunks

    def _chunk_single_document(self, document: DocumentChunk, start_index: int) -> List[TextChunk]:
        """对单个文档进行切块"""
        if self.use_semantic:
            return self._semantic_chunking(document, start_index)
        else:
            return self._fixed_size_chunking(document, start_index)

    def _fixed_size_chunking(self, document: DocumentChunk, start_index: int) -> List[TextChunk]:
        """固定大小切块"""
        chunks = []
        content = document.content

        # 按分隔符分割
        segments = content.split(self.separator)

        current_chunk = ""
        current_size = 0

        for i, segment in enumerate(segments):
            segment_size = self._estimate_tokens(segment)

            # 如果当前块为空，直接添加
            if not current_chunk:
                current_chunk = segment
                current_size = segment_size
            # 如果添加后不超过块大小
            elif current_size + segment_size <= self.chunk_size:
                current_chunk += self.separator + segment
                current_size += segment_size
            # 否则创建新块
            else:
                chunks.append(self._create_text_chunk(
                    current_chunk, document, start_index + len(chunks), current_size
                ))
                current_chunk = segment
                current_size = segment_size

        # 添加最后一个块
        if current_chunk:
            chunks.append(self._create_text_chunk(
                current_chunk, document, start_index + len(chunks), current_size
            ))

        return chunks

    def _semantic_chunking(self, document: DocumentChunk, start_index: int) -> List[TextChunk]:
        """语义切块 - 基于段落和句子边界"""
        chunks = []
        content = document.content

        # 首先按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_chunk = ""
        current_size = 0

        for i, paragraph in enumerate(paragraphs):
            # 如果单个段落就超过块大小，需要进一步切分
            para_size = self._estimate_tokens(paragraph)

            if para_size > self.chunk_size:
                # 先保存当前块
                if current_chunk:
                    chunks.append(self._create_text_chunk(
                        current_chunk, document, start_index + len(chunks), current_size
                    ))
                    current_chunk = ""
                    current_size = 0

                # 对大段落进行句子级切分
                sentences = self._split_sentences(paragraph)
                for sentence in sentences:
                    sent_size = self._estimate_tokens(sentence)

                    if not current_chunk:
                        current_chunk = sentence
                        current_size = sent_size
                    elif current_size + sent_size <= self.chunk_size:
                        current_chunk += " " + sentence
                        current_size += sent_size
                    else:
                        chunks.append(self._create_text_chunk(
                            current_chunk, document, start_index + len(chunks), current_size
                        ))
                        # 保留重叠部分
                        current_chunk = self._create_overlap_chunk(current_chunk, sentence)
                        current_size = self._estimate_tokens(current_chunk)
            else:
                # 正常段落处理
                if not current_chunk:
                    current_chunk = paragraph
                    current_size = para_size
                elif current_size + para_size <= self.chunk_size:
                    current_chunk += "\n\n" + paragraph
                    current_size += para_size
                else:
                    chunks.append(self._create_text_chunk(
                        current_chunk, document, start_index + len(chunks), current_size
                    ))
                    # 保留重叠部分
                    current_chunk = self._create_overlap_chunk(current_chunk, paragraph)
                    current_size = self._estimate_tokens(current_chunk)

        # 添加最后一个块
        if current_chunk:
            chunks.append(self._create_text_chunk(
                current_chunk, document, start_index + len(chunks), current_size
            ))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 使用简单的正则表达式分句
        sentences = re.split(r'[.!?。！？]\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_overlap_chunk(self, previous_chunk: str, new_content: str) -> str:
        """创建包含重叠内容的新块"""
        if not self.chunk_overlap:
            return new_content

        # 获取前一个块的最后部分
        words = previous_chunk.split()
        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words

        overlap_text = ' '.join(overlap_words)
        return overlap_text + " " + new_content

    def _create_text_chunk(self, content: str, document: DocumentChunk,
                         chunk_index: int, token_count: int) -> TextChunk:
        """创建文本块对象"""
        metadata = document.metadata.copy()
        metadata['chunk_index'] = chunk_index
        metadata['token_count'] = token_count

        return TextChunk(
            content=content,
            metadata=metadata,
            chunk_index=chunk_index,
            chunk_id=f"{document.chunk_id}_chunk_{chunk_index}",
            token_count=token_count
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的token数量（粗略估计）
        英文：约4字符=1token
        中文：约1.5字符=1token
        """
        if not text:
            return 0

        # 简单统计中文字符数
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        other_chars = len(text) - chinese_chars

        # 估算token数
        chinese_tokens = chinese_chars * 1.5
        other_tokens = other_chars / 4

        return int(chinese_tokens + other_tokens)

    def get_chunk_statistics(self, chunks: List[TextChunk]) -> Dict[str, Any]:
        """
        获取切块统计信息

        Args:
            chunks: 文本块列表

        Returns:
            统计信息字典
        """
        if not chunks:
            return {}

        token_counts = [chunk.token_count for chunk in chunks]
        content_lengths = [len(chunk.content) for chunk in chunks]

        return {
            'total_chunks': len(chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': sum(token_counts) / len(token_counts),
            'max_tokens': max(token_counts),
            'min_tokens': min(token_counts),
            'avg_content_length': sum(content_lengths) / len(content_lengths),
            'max_content_length': max(content_lengths),
            'min_content_length': min(content_lengths)
        }


def main():
    """测试文本切块器"""
    from ..parsers.pdf_parser import DocumentChunk

    # 创建测试文档
    test_doc = DocumentChunk(
        content="这是一个测试文档。它包含多个段落。\n\n这是第二个段落，用于测试切块功能。"
                "这个段落比较长，用来验证切块器是否能够正确处理长文本。"
                "我们还需要测试边界情况，比如空段落和特殊字符。\n\n"
                "这是最后一个段落。测试完成！",
        metadata={'test': True},
        page_num=1,
        chunk_id="test_doc"
    )

    # 创建切块器
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)

    # 执行切块
    chunks = chunker.chunk_documents([test_doc])

    # 显示结果
    print(f"切块结果，共 {len(chunks)} 个块:")
    for i, chunk in enumerate(chunks):
        print(f"\n块 {i+1} ({chunk.token_count} tokens):")
        print(f"  {chunk.content[:100]}...")

    # 显示统计信息
    stats = chunker.get_chunk_statistics(chunks)
    print(f"\n统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()