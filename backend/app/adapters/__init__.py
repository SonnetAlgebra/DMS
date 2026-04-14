"""数据源适配器模块

提供数据源接入的标准接口，支持扩展不同数据源：
- CSVAdapter: CSV 文件数据源
- （未来可扩展）KafkaAdapter, DatabaseAdapter 等
"""

from .base import BaseAdapter, DataPoint
from .csv_adapter import CSVAdapter

__all__ = [
    "BaseAdapter",
    "DataPoint",
    "CSVAdapter",
]
