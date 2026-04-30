"""
答案生成器
基于Prompt和LLM生成最终答案
"""
import logging
from typing import Optional, Dict, Any
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerGenerator:
    """答案生成器类"""

    def __init__(self,
                 llm_provider: str = "ollama",
                 model_name: Optional[str] = None,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None):
        """
        初始化答案生成器

        Args:
            llm_provider: LLM提供商 (ollama, openai, anthropic, etc.)
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
        """
        self.llm_provider = llm_provider
        self.model_name = model_name or self._get_default_model(llm_provider)
        self.api_key = api_key or os.getenv(self._get_api_key_env(llm_provider))
        self.base_url = base_url or self._get_default_base_url(llm_provider)

        logger.info(f"答案生成器初始化完成 - 提供商: {llm_provider}, 模型: {self.model_name}")

    def _get_default_model(self, provider: str) -> str:
        """获取默认模型名称"""
        default_models = {
            'ollama': 'llama2',
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229',
            'zhipu': 'glm-4',
            'qianfan': 'ernie-4.0'
        }
        return default_models.get(provider, 'llama2')

    def _get_api_key_env(self, provider: str) -> str:
        """获取API密钥环境变量名"""
        env_keys = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'zhipu': 'ZHIPU_API_KEY',
            'qianfan': 'QIANFAN_ACCESS_KEY'
        }
        return env_keys.get(provider, '')

    def _get_default_base_url(self, provider: str) -> str:
        """获取默认基础URL"""
        base_urls = {
            'ollama': 'http://localhost:11434',
            'openai': 'https://api.openai.com/v1',
            'anthropic': 'https://api.anthropic.com'
        }
        return base_urls.get(provider, '')

    def generate_answer(self,
                      prompt: str,
                      temperature: float = 0.7,
                      max_tokens: int = 1000) -> str:
        """
        生成答案

        Args:
            prompt: 输入的Prompt
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            生成的答案
        """
        logger.info(f"开始生成答案 - 提供商: {self.llm_provider}")

        try:
            if self.llm_provider == 'ollama':
                return self._generate_with_ollama(prompt, temperature, max_tokens)
            elif self.llm_provider == 'openai':
                return self._generate_with_openai(prompt, temperature, max_tokens)
            elif self.llm_provider == 'anthropic':
                return self._generate_with_anthropic(prompt, temperature, max_tokens)
            elif self.llm_provider == 'mock':
                return self._generate_mock_answer(prompt)
            else:
                raise ValueError(f"不支持的LLM提供商: {self.llm_provider}")

        except Exception as e:
            logger.error(f"答案生成失败: {str(e)}")
            raise

    def _generate_with_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """使用Ollama生成答案"""
        try:
            import requests

            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            answer = result.get('response', '')

            logger.info(f"Ollama生成完成，答案长度: {len(answer)}")
            return answer

        except ImportError:
            logger.warning("requests库未安装，使用模拟答案")
            return self._generate_mock_answer(prompt)
        except Exception as e:
            logger.error(f"Ollama生成失败: {str(e)}")
            raise

    def _generate_with_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """使用OpenAI生成答案"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            answer = response.choices[0].message.content

            logger.info(f"OpenAI生成完成，答案长度: {len(answer)}")
            return answer

        except ImportError:
            logger.warning("openai库未安装，使用模拟答案")
            return self._generate_mock_answer(prompt)
        except Exception as e:
            logger.error(f"OpenAI生成失败: {str(e)}")
            raise

    def _generate_with_anthropic(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """使用Anthropic生成答案"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.content[0].text

            logger.info(f"Anthropic生成完成，答案长度: {len(answer)}")
            return answer

        except ImportError:
            logger.warning("anthropic库未安装，使用模拟答案")
            return self._generate_mock_answer(prompt)
        except Exception as e:
            logger.error(f"Anthropic生成失败: {str(e)}")
            raise

    def _generate_mock_answer(self, prompt: str) -> str:
        """生成模拟答案（用于测试）"""
        # 这里是一个简单的规则基础答案生成器
        if "巴洛克" in prompt:
            return "根据参考文档，巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。巴洛克音乐的特点是华丽、装饰性强，使用通奏低音，强调戏剧性对比。代表作曲家有巴赫、亨德尔等。"
        elif "古典主义" in prompt:
            return "根据参考文档，古典主义音乐时期从1750年到1820年，以海顿、莫扎特、贝多芬为代表。这个时期音乐更加理性、均衡，确立了交响曲、奏鸣曲等音乐体裁。"
        elif "浪漫主义" in prompt:
            return "根据参考文档，浪漫主义音乐时期从1820年到1900年，强调个人情感的表达。浪漫主义音乐注重主观情感的抒发，和声更加丰富，节奏更加自由。"
        else:
            return "根据提供的参考文档，我找到了相关信息。不过建议您提供更具体的问题，这样我可以给出更准确的回答。"

    def generate_with_context(self,
                          query: str,
                          retrieved_docs: list,
                          conversation_history: list = None) -> Dict[str, Any]:
        """
        带上下文的生成方法

        Args:
            query: 用户查询
            retrieved_docs: 检索到的文档
            conversation_history: 对话历史

        Returns:
            包含答案和元数据的字典
        """
        from .prompt_assembler import PromptAssembler

        # 创建Prompt组装器
        assembler = PromptAssembler()

        # 组装Prompt
        prompt = assembler.assemble_prompt(query, retrieved_docs, conversation_history)

        # 生成答案
        answer = self.generate_answer(prompt)

        return {
            'answer': answer,
            'prompt': prompt,
            'query': query,
            'num_retrieved_docs': len(retrieved_docs),
            'model': self.model_name,
            'provider': self.llm_provider
        }


def main():
    """测试答案生成器"""
    # 创建模拟答案生成器（无需API密钥）
    generator = AnswerGenerator(llm_provider='mock')

    # 测试基础生成
    test_prompt = "请根据以下信息回答问题：巴洛克音乐时期大约在1600年至1750年间，以复调音乐为主。\n\n问题：巴洛克音乐有什么特点？"

    answer = generator.generate_answer(test_prompt)

    print("=" * 60)
    print("测试Prompt:")
    print("=" * 60)
    print(test_prompt)
    print()

    print("=" * 60)
    print("生成的答案:")
    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()