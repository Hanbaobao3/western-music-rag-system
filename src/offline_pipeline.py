"""
RAG系统离线处理主程序
完成文档导入、解析、切块、向量化、存储等离线流程
"""
import os
import sys
import argparse
import logging
from typing import List

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.parsers.pdf_parser import PDFParser
from src.chunkers.text_chunker import TextChunker
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.storage.vector_store import VectorStore
from src.utils.common import load_config, setup_logging, ensure_dir, is_supported_format

# 获取日志记录器
logger = logging.getLogger(__name__)


class OfflinePipeline:
    """离线处理流程类"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化离线处理流程

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = load_config(config_path)

        # 设置日志
        log_config = self.config.get('logging', {})
        setup_logging(log_config)

        logger.info("=" * 50)
        logger.info("RAG系统离线处理流程初始化")
        logger.info("=" * 50)

        # 初始化各个处理模块
        self._init_components()

    def _init_components(self):
        """初始化处理组件"""
        try:
            # 文档解析器
            pdf_config = self.config.get('document_processing', {}).get('pdf', {})
            self.pdf_parser = PDFParser(
                extract_images=pdf_config.get('extract_images', False),
                preserve_layout=pdf_config.get('preserve_layout', True)
            )

            # 文本切块器
            chunking_config = self.config.get('chunking', {})
            self.text_chunker = TextChunker(
                chunk_size=chunking_config.get('chunk_size', 512),
                chunk_overlap=chunking_config.get('chunk_overlap', 50),
                use_semantic=chunking_config.get('use_semantic', True)
            )

            # 嵌入生成器
            embedding_config = self.config.get('embeddings', {})
            self.embedding_generator = EmbeddingGenerator(
                model_name=embedding_config.get('model_name', 'paraphrase-multilingual-MiniLM-L12-v2'),
                device=embedding_config.get('device', 'cpu'),
                cache_dir=embedding_config.get('cache_dir', './models')
            )

            # 向量存储
            vector_store_config = self.config.get('vector_store', {})
            self.vector_store = VectorStore(
                index_type=vector_store_config.get('index_type', 'flat'),
                metric=vector_store_config.get('metric', 'cosine')
            )

            logger.info("所有组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {str(e)}")
            raise

    def process_document(self, document_path: str) -> bool:
        """
        处理单个文档

        Args:
            document_path: 文档路径

        Returns:
            处理是否成功
        """
        logger.info(f"开始处理文档: {document_path}")

        try:
            # 1. 检查文件格式
            supported_formats = self.config.get('document_processing', {}).get('supported_formats', [])
            if not is_supported_format(document_path, supported_formats):
                logger.error(f"不支持的文件格式: {document_path}")
                return False

            # 2. 文档解析
            logger.info("步骤 1/4: 文档解析")
            file_ext = get_file_extension(document_path)

            if file_ext == 'pdf':
                doc_chunks = self.pdf_parser.parse_pdf(document_path)
            else:
                logger.error(f"暂不支持 {file_ext} 格式的文档")
                return False

            if not doc_chunks:
                logger.error("文档解析失败，未提取到内容")
                return False

            logger.info(f"文档解析完成，共提取 {len(doc_chunks)} 个文档块")

            # 3. 文本切块
            logger.info("步骤 2/4: 文本切块")
            text_chunks = self.text_chunker.chunk_documents(doc_chunks)

            if not text_chunks:
                logger.error("文本切块失败")
                return False

            # 显示切块统计信息
            chunk_stats = self.text_chunker.get_chunk_statistics(text_chunks)
            logger.info(f"文本切块完成，生成 {len(text_chunks)} 个文本块")
            logger.info(f"  平均Token数: {chunk_stats['avg_tokens_per_chunk']:.1f}")
            logger.info(f"  总Token数: {chunk_stats['total_tokens']}")

            # 4. 向量化
            logger.info("步骤 3/4: 向量化")
            embedding_result = self.embedding_generator.generate_embeddings(text_chunks)

            if embedding_result.embeddings.size == 0:
                logger.error("向量化失败")
                return False

            logger.info(f"向量化完成，嵌入维度: {embedding_result.embedding_dim}")

            # 5. 存储向量
            logger.info("步骤 4/4: 存储向量")
            self.vector_store.add_embeddings(embedding_result)

            logger.info(f"文档处理完成: {document_path}")
            return True

        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return False

    def process_directory(self, directory: str) -> int:
        """
        处理目录中的所有文档

        Args:
            directory: 目录路径

        Returns:
            成功处理的文档数量
        """
        if not os.path.exists(directory):
            logger.error(f"目录不存在: {directory}")
            return 0

        logger.info(f"开始处理目录: {directory}")

        # 获取支持的格式
        supported_formats = self.config.get('document_processing', {}).get('supported_formats', [])

        # 查找所有支持的文档
        documents = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if is_supported_format(file_path, supported_formats):
                    documents.append(file_path)

        if not documents:
            logger.warning("未找到支持的文档")
            return 0

        logger.info(f"找到 {len(documents)} 个文档")

        # 处理每个文档
        success_count = 0
        for i, doc_path in enumerate(documents, 1):
            logger.info(f"处理进度: {i}/{len(documents)}")

            if self.process_document(doc_path):
                success_count += 1

        logger.info(f"目录处理完成，成功处理 {success_count}/{len(documents)} 个文档")
        return success_count

    def save_results(self, save_path: str):
        """
        保存处理结果

        Args:
            save_path: 保存路径
        """
        try:
            ensure_dir(os.path.dirname(save_path))
            self.vector_store.save(save_path)
            logger.info(f"处理结果已保存到: {save_path}")
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")
            raise

    def get_statistics(self) -> dict:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        return self.vector_store.get_statistics()


def get_file_extension(filepath: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filepath)[1].lower().replace('.', '')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG系统离线处理流程")
    parser.add_argument('--input', '-i', type=str, required=True,
                       help='输入文件或目录路径')
    parser.add_argument('--output', '-o', type=str, default='processed/vector_store',
                       help='输出路径')
    parser.add_argument('--config', '-c', type=str, default='config/config.yaml',
                       help='配置文件路径')
    parser.add_argument('--stats', '-s', action='store_true',
                       help='显示统计信息')

    args = parser.parse_args()

    try:
        # 创建处理流程
        pipeline = OfflinePipeline(config_path=args.config)

        # 处理输入
        if os.path.isfile(args.input):
            success = pipeline.process_document(args.input)
            if not success:
                logger.error("文档处理失败")
                sys.exit(1)
        elif os.path.isdir(args.input):
            success_count = pipeline.process_directory(args.input)
            if success_count == 0:
                logger.error("目录处理失败")
                sys.exit(1)
        else:
            logger.error(f"输入路径不存在: {args.input}")
            sys.exit(1)

        # 保存结果
        pipeline.save_results(args.output)

        # 显示统计信息
        if args.stats:
            stats = pipeline.get_statistics()
            print("\n" + "=" * 50)
            print("处理统计信息")
            print("=" * 50)
            for key, value in stats.items():
                print(f"{key}: {value}")
            print("=" * 50)

        logger.info("离线处理流程完成！")

    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()