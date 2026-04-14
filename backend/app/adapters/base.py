"""数据源适配器基类接口"""
from abc import ABC, abstractmethod
from typing import Iterator, NamedTuple


class DataPoint(NamedTuple):
    """数据点"""
    metric_id: str
    metric_name: str
    timestamp: str
    value: float | None


class BaseAdapter(ABC):
    """数据源适配器基类

    定义数据源接入的标准接口，支持扩展不同数据源（CSV、Kafka、数据库等）
    """

    @abstractmethod
    def parse(self) -> Iterator[DataPoint]:
        """
        解析数据源，返回数据点迭代器

        Returns:
            Iterator[DataPoint]: 数据点迭代器，包含 metric_id, metric_name, timestamp, value

        Raises:
            ValueError: 数据格式不符合要求
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        验证数据源是否有效

        Returns:
            bool: 数据源是否有效
        """
        pass

    @abstractmethod
    def get_metrics(self) -> dict[str, str]:
        """
        获取数据源中的指标信息

        Returns:
            dict[str, str]: 指标 ID 到指标名称的映射
        """
        pass
