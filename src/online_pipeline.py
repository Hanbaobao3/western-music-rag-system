"""
RAG系统在线查询主程序
实现完整的问答流程：检索 → Prompt组装 → 答案生成
"""
import logging
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.embeddings.embedding_generator import EmbeddingGenerator
from src.storage.vector_store import VectorStore
from src.retriever.document_retriever import DocumentRetriever
from src.generator.prompt_assembler import PromptAssembler
from src.generator.answer_generator import AnswerGenerator
from src.utils.common import load_config, setup_logging

# 获取日志记录器
logger = logging.getLogger(__name__)


class OnlinePipeline:
    """在线查询流程类"""

    def __init__(self,
                 vector_store_path: str = "processed/vector_store",
                 config_path: str = "config/config.yaml"):
        """
        初始化在线查询流程

        Args:
            vector_store_path: 向量存储路径
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = load_config(config_path)

        # 设置日志
        setup_logging(self.config.get('logging', {}))

        logger.info("=" * 50)
        logger.info("RAG系统在线查询流程初始化")
        logger.info("=" * 50)

        # 初始化组件
        self._init_components(vector_store_path)

    def _init_components(self, vector_store_path: str):
        """初始化各个组件"""
        try:
            # 初始化嵌入生成器
            embedding_config = self.config.get('embeddings', {})
            self.embedding_generator = EmbeddingGenerator(
                model_name=embedding_config.get('model_name', 'paraphrase-multilingual-MiniLM-L12-v2'),
                device=embedding_config.get('device', 'cpu'),
                cache_dir=embedding_config.get('cache_dir', './models')
            )

            # 加载向量存储
            self.vector_store = VectorStore()
            self.vector_store.load(vector_store_path)

            logger.info(f"向量存储加载完成，包含 {len(self.vector_store.chunks)} 个向量")

            # 初始化文档检索器
            retrieval_config = self.config.get('retrieval', {})
            self.retriever = DocumentRetriever(
                vector_store=self.vector_store,
                embedding_generator=self.embedding_generator,
                top_k=retrieval_config.get('top_k', 5),
                min_similarity=retrieval_config.get('min_similarity', 0.7)
            )

            # 初始化Prompt组装器
            chunking_config = self.config.get('chunking', {})
            self.prompt_assembler = PromptAssembler(
                max_context_length=chunking_config.get('chunk_size', 512) * 2
            )

            # 初始化答案生成器（默认使用mock模式）
            self.answer_generator = AnswerGenerator(llm_provider='mock')

            logger.info("所有组件初始化完成")

        except Exception as e:
            logger.error(f"组件初始化失败: {str(e)}")
            raise

    def query(self,
             user_question: str,
             top_k: Optional[int] = None,
             min_similarity: Optional[float] = None,
             conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        执行完整的查询流程

        Args:
            user_question: 用户问题
            top_k: 返回的文档数量
            min_similarity: 最小相似度阈值
            conversation_history: 对话历史

        Returns:
            包含答案、检索文档和元数据的字典
        """
        logger.info(f"收到用户查询: {user_question}")

        try:
            # 步骤1: 检索相关文档
            logger.info("步骤 1/3: 检索相关文档")
            retrieved_docs = self.retriever.retrieve(
                query=user_question,
                top_k=top_k,
                min_similarity=min_similarity
            )

            if not retrieved_docs:
                logger.warning("未检索到相关文档")
                return {
                    'answer': '抱歉，我没有找到与您问题相关的文档内容。请尝试换个问法或提供更多背景信息。',
                    'retrieved_docs': [],
                    'success': False,
                    'reason': 'no_retrieved_docs'
                }

            logger.info(f"检索到 {len(retrieved_docs)} 个相关文档")

            # 步骤2: 组装Prompt
            logger.info("步骤 2/3: 组装Prompt")
            prompt = self.prompt_assembler.assemble_prompt(
                query=user_question,
                retrieved_docs=retrieved_docs,
                conversation_history=conversation_history
            )

            logger.info(f"Prompt组装完成，长度: {len(prompt)} 字符")

            # 步骤3: 生成答案
            logger.info("步骤 3/3: 生成答案")
            answer = self.answer_generator.generate_answer(prompt)

            logger.info(f"答案生成完成，长度: {len(answer)} 字符")

            # 返回完整结果
            return {
                'answer': answer,
                'retrieved_docs': retrieved_docs,
                'prompt': prompt,
                'success': True,
                'metadata': {
                    'query': user_question,
                    'num_retrieved_docs': len(retrieved_docs),
                    'model': self.answer_generator.model_name,
                    'provider': self.answer_generator.llm_provider
                }
            }

        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return {
                'answer': f'处理您的问题时出现错误: {str(e)}',
                'retrieved_docs': [],
                'success': False,
                'reason': f'error: {str(e)}'
            }

    def batch_query(self,
                  questions: List[str]) -> List[Dict[str, Any]]:
        """
        批量查询

        Args:
            questions: 问题列表

        Returns:
            结果列表
        """
        logger.info(f"开始批量查询，共 {len(questions)} 个问题")

        results = []
        for i, question in enumerate(questions, 1):
            logger.info(f"处理问题 {i}/{len(questions)}")
            result = self.query(question)
            results.append(result)

        logger.info(f"批量查询完成，成功 {sum(1 for r in results if r['success'])}/{len(questions)} 个")
        return results

    def interactive_mode(self):
        """交互式问答模式"""
        print("=" * 60)
        print("RAG系统交互式问答模式")
        print("=" * 60)
        print("输入您的问题，输入 'quit' 或 'exit' 退出")
        print()

        conversation_history = []

        while True:
            try:
                # 获取用户输入
                user_input = input("用户: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("感谢使用，再见！")
                    break

                # 执行查询
                print("正在处理...")
                result = self.query(user_input, conversation_history=conversation_history)

                # 显示答案
                print(f"\n助手: {result['answer']}")

                # 显示检索到的文档信息（可选）
                if result['success'] and result['retrieved_docs']:
                    print(f"\n[参考了 {len(result['retrieved_docs'])} 个文档片段]")

                # 更新对话历史
                conversation_history.append({
                    'user': user_input,
                    'assistant': result['answer']
                })

                # 限制历史长度
                if len(conversation_history) > 5:
                    conversation_history = conversation_history[-5:]

                print()  # 空行分隔

            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"处理出错: {str(e)}")
                continue


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="RAG系统在线查询")
    parser.add_argument('--query', '-q', type=str, help='单次查询')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    parser.add_argument('--vector-store', '-v', type=str, default='processed/vector_store',
                       help='向量存储路径')
    parser.add_argument('--config', '-c', type=str, default='config/config.yaml',
                       help='配置文件路径')

    args = parser.parse_args()

    try:
        # 创建查询流程
        pipeline = OnlinePipeline(
            vector_store_path=args.vector_store,
            config_path=args.config
        )

        if args.interactive:
            # 交互式模式
            pipeline.interactive_mode()
        elif args.query:
            # 单次查询
            result = pipeline.query(args.query)

            print("=" * 60)
            print("查询结果")
            print("=" * 60)
            print(f"问题: {args.query}")
            print(f"答案: {result['answer']}")
            print(f"状态: {'成功' if result['success'] else '失败'}")

            if result['success']:
                print(f"检索文档数: {len(result['retrieved_docs'])}")
                print(f"使用模型: {result['metadata']['model']}")
            else:
                print(f"失败原因: {result.get('reason', 'unknown')}")

            print("=" * 60)
        else:
            print("请指定 --query 或 --interactive 参数")
            parser.print_help()

    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()