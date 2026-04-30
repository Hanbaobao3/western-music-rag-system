"""
RAG系统Web服务器
提供API接口给前端网页使用
"""
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.online_pipeline import OnlinePipeline

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 全局变量
rag_pipeline = None
anthropic_client = None

def init_rag_pipeline():
    """初始化RAG管道"""
    global rag_pipeline
    if rag_pipeline is None:
        try:
            vector_store_path = os.getenv('VECTOR_STORE_PATH', os.path.join(project_root, 'processed', 'vector_store'))
            config_path = os.getenv('CONFIG_PATH', os.path.join(project_root, 'config', 'config.yaml'))
            rag_pipeline = OnlinePipeline(vector_store_path=vector_store_path, config_path=config_path)
            print("RAG管道初始化成功")
        except Exception as e:
            print(f"RAG管道初始化失败: {str(e)}")
            rag_pipeline = None

def init_anthropic_client():
    """初始化Anthropic客户端"""
    global anthropic_client
    if anthropic_client is None:
        try:
            api_key = os.getenv('ZAI_API_KEY')
            api_base = os.getenv('ZAI_API_BASE', 'https://api.anthropic.com')
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

            if not api_key:
                print("警告：未找到ZAI_API_KEY，将使用mock模式")
                return None

            try:
                anthropic_client = anthropic.Anthropic(
                    api_key=api_key,
                    base_url=api_base
                )
                print(f"Anthropic客户端初始化成功 - 模型: {model}")
                return anthropic_client

            except ImportError:
                print("警告：anthropic库未安装，将使用mock模式")
                return None
            except Exception as e:
                print(f"Anthropic客户端初始化失败: {str(e)}，将使用mock模式")
                return None

        except Exception as e:
            print(f"Anthropic初始化过程出错: {str(e)}")
            return None

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'index.html')

@app.route('/api/query', methods=['POST'])
def query():
    """查询接口"""
    global anthropic_client

    if rag_pipeline is None:
        init_rag_pipeline()

    if rag_pipeline is None:
        return jsonify({
            'success': False,
            'error': 'RAG管道未初始化'
        }), 500

    try:
        data = request.json
        query = data.get('query', '').strip()
        period = data.get('period', 'all')
        use_ai = data.get('use_ai', True)  # 默认使用AI

        if not query:
            return jsonify({
                'success': False,
                'error': '查询不能为空'
            }), 400

        print(f"收到查询请求: query='{query}', period='{period}', use_ai={use_ai}")

        # 执行RAG查询
        rag_result = rag_pipeline.query(query)

        # 如果使用AI且Anthropic客户端可用，则用Claude生成答案
        if use_ai and rag_result.get('success') and anthropic_client is not None:
            try:
                model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

                # 构建Prompt
                retrieved_docs_text = ""
                if rag_result.get('retrieved_docs'):
                    for i, doc in enumerate(rag_result.get('retrieved_docs')[:3], 1):
                        retrieved_docs_text += f"[文档 {i}] {doc.get('content', '')}\n"

                prompt = f"""You are a professional Western music history expert. Answer the user's question based on the retrieved documents.

Retrieved Documents:
{retrieved_docs_text}

User Question: {query}

Instructions:
1. Only use information from the retrieved documents
2. If the documents don't contain relevant information, clearly state this
3. Provide accurate, clear, and well-structured answers
4. For complex topics, organize your response with bullet points
5. Maintain a professional and educational tone
6. Answer in Chinese since the user asked in Chinese
7. Keep your response concise but informative
"""

                print(f"正在调用Claude API，Prompt长度: {len(prompt)}")

                # 调用Anthropic API
                response = anthropic_client.messages.create(
                    model=model,
                    max_tokens=800,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # 提取AI生成的答案
                ai_answer = response.content[0].text

                # 更新结果
                rag_result['answer'] = ai_answer
                rag_result['ai_generated'] = True
                rag_result['model'] = model

                print(f"Claude答案生成完成，长度: {len(ai_answer)}")

            except Exception as e:
                print(f"Claude API调用失败: {str(e)}，使用RAG原始答案")
                # 回退到RAG原始答案
                rag_result['ai_generated'] = False
        else:
            rag_result['ai_generated'] = False

        # 添加时期信息
        rag_result['period'] = period
        rag_result['timestamp'] = os.popen('date +"%Y-%m-%d %H:%M:%S"').read().strip()

        return jsonify(rag_result)

    except Exception as e:
        print(f"查询接口错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch-query', methods=['POST'])
def batch_query():
    """批量查询接口"""
    if rag_pipeline is None:
        init_rag_pipeline()

    if rag_pipeline is None:
        return jsonify({
            'success': False,
            'error': 'RAG管道未初始化'
        }), 500

    try:
        data = request.json
        questions = data.get('questions', [])

        if not questions:
            return jsonify({
                'success': False,
                'error': '问题列表不能为空'
            }), 400

        # 执行批量查询
        results = rag_pipeline.batch_query(questions)

        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'timestamp': os.popen('date +"%Y-%m-%d %H:%M:%S"').read().strip()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查接口"""
    global anthropic_client

    rag_status = 'ready' if rag_pipeline is not None else 'not_initialized'
    ai_status = 'ready' if anthropic_client is not None else 'not_configured'

    return jsonify({
        'status': 'operational',
        'rag_pipeline': rag_status,
        'ai_client': ai_status,
        'anthropic_available': anthropic_client is not None,
        'timestamp': os.popen('date +"%Y-%m-%d %H:%M:%S"').read().strip(),
        'version': '1.0.0'
    })

@app.route('/api/stats', methods=['GET'])
def stats():
    """获取系统统计信息"""
    global anthropic_client

    if rag_pipeline is None:
        return jsonify({
            'success': False,
            'error': 'RAG管道未初始化'
        }), 500

    try:
        vector_stats = rag_pipeline.vector_store.get_statistics()

        return jsonify({
            'success': True,
            'stats': {
                **vector_stats,
                'model': 'claude-3-5-sonnet-20241022' if anthropic_client is not None else 'mock',
                'provider': 'anthropic' if anthropic_client is not None else 'local',
                'anthropic_available': anthropic_client is not None
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("西方音乐史RAG问答系统 - Web服务器")
    print("=" * 60)
    print()
    print("服务器信息:")
    print("  地址: http://localhost:5000")
    print("  静态文件: ./index.html")
    print("  API接口: /api/query, /api/batch-query, /api/health, /api/stats")
    print()
    print("正在启动服务器...")
    print("=" * 60)
    print()

    # 启动Flask服务器
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )