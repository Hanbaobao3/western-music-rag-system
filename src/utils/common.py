"""
通用工具函数
"""
import os
import yaml
import logging
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {str(e)}")


def setup_logging(log_config: Dict[str, Any]):
    """
    设置日志

    Args:
        log_config: 日志配置字典
    """
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file')

    # 创建日志目录
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 配置日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 控制台输出
            logging.FileHandler(log_file, encoding='utf-8') if log_file else None  # 文件输出
        ]
    )


def ensure_dir(directory: str):
    """
    确保目录存在，不存在则创建

    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_file_extension(filepath: str) -> str:
    """
    获取文件扩展名

    Args:
        filepath: 文件路径

    Returns:
        文件扩展名（小写，不带点）
    """
    return os.path.splitext(filepath)[1].lower().replace('.', '')


def is_supported_format(filepath: str, supported_formats: list) -> bool:
    """
    检查文件格式是否支持

    Args:
        filepath: 文件路径
        supported_formats: 支持的格式列表

    Returns:
        是否支持
    """
    ext = get_file_extension(filepath)
    return ext in supported_formats