"""
PDF文档解析器
支持从PDF文件中提取文本内容和结构信息
"""
import os
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import PyPDF2
import pdfplumber

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """文档块数据结构"""
    content: str
    metadata: Dict[str, Any]
    page_num: int
    chunk_id: str


class PDFParser:
    """PDF解析器类"""

    def __init__(self, extract_images: bool = False, preserve_layout: bool = True):
        """
        初始化PDF解析器

        Args:
            extract_images: 是否提取图片内容
            preserve_layout: 是否保持文档布局
        """
        self.extract_images = extract_images
        self.preserve_layout = preserve_layout
        logger.info("PDF解析器初始化完成")

    def parse_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        """
        解析PDF文件，返回文档块列表

        Args:
            pdf_path: PDF文件路径

        Returns:
            包含文本内容和元数据的文档块列表
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")

        logger.info(f"开始解析PDF文件: {pdf_path}")

        try:
            # 使用pdfplumber解析（更好的文本提取）
            chunks = self._parse_with_pdfplumber(pdf_path)

            logger.info(f"PDF解析完成，共提取 {len(chunks)} 个文档块")
            return chunks

        except Exception as e:
            logger.error(f"PDF解析失败: {str(e)}")
            # 回退到PyPDF2
            logger.info("尝试使用PyPDF2解析...")
            return self._parse_with_pypdf2(pdf_path)

    def _parse_with_pdfplumber(self, pdf_path: str) -> List[DocumentChunk]:
        """使用pdfplumber解析PDF"""
        chunks = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"PDF总页数: {total_pages}")

            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # 提取文本
                    text = page.extract_text()

                    if text and text.strip():
                        # 创建文档块
                        chunk = DocumentChunk(
                            content=text,
                            metadata={
                                'source': pdf_path,
                                'page': page_num,
                                'total_pages': total_pages,
                                'width': page.width,
                                'height': page.height
                            },
                            page_num=page_num,
                            chunk_id=f"{os.path.basename(pdf_path)}_page_{page_num}"
                        )
                        chunks.append(chunk)

                        logger.debug(f"第 {page_num}/{total_pages} 页解析完成")

                except Exception as e:
                    logger.warning(f"第 {page_num} 页解析失败: {str(e)}")
                    continue

        return chunks

    def _parse_with_pypdf2(self, pdf_path: str) -> List[DocumentChunk]:
        """使用PyPDF2解析PDF（备选方案）"""
        chunks = []

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if text and text.strip():
                        chunk = DocumentChunk(
                            content=text,
                            metadata={
                                'source': pdf_path,
                                'page': page_num + 1,
                                'total_pages': total_pages
                            },
                            page_num=page_num + 1,
                            chunk_id=f"{os.path.basename(pdf_path)}_page_{page_num + 1}"
                        )
                        chunks.append(chunk)

                except Exception as e:
                    logger.warning(f"第 {page_num + 1} 页解析失败: {str(e)}")
                    continue

        return chunks

    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        提取PDF文件的元数据

        Args:
            pdf_path: PDF文件路径

        Returns:
            包含元数据的字典
        """
        metadata = {
            'filename': os.path.basename(pdf_path),
            'filepath': pdf_path,
            'size': os.path.getsize(pdf_path)
        }

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    })

                metadata['page_count'] = len(pdf_reader.pages)

        except Exception as e:
            logger.warning(f"提取元数据失败: {str(e)}")

        return metadata


def main():
    """测试PDF解析器"""
    parser = PDFParser()

    # 测试解析（需要实际的PDF文件）
    test_pdf = "data/test.pdf"
    if os.path.exists(test_pdf):
        print(f"解析PDF文件: {test_pdf}")

        # 提取元数据
        metadata = parser.extract_metadata(test_pdf)
        print("文档元数据:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # 解析内容
        chunks = parser.parse_pdf(test_pdf)
        print(f"\n解析完成，共 {len(chunks)} 个文档块")

        # 显示前几个文档块的前100个字符
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n文档块 {i+1} (页 {chunk.page_num}):")
            print(f"  {chunk.content[:100]}...")
    else:
        print(f"测试文件 {test_pdf} 不存在")


if __name__ == "__main__":
    main()