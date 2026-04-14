"""CSV 适配器 - 解析 CSV 文件提取指标和数据"""
import pandas as pd
from typing import Iterator, Dict
import io
from .base import BaseAdapter, DataPoint


class CSVAdapter(BaseAdapter):
    """CSV 数据解析适配器

    支持的 CSV 格式：
    - 必须包含时间戳列：timestamp, time, 日期, 时间, ts, datetime（大小写不敏感）
    - 其他列作为指标列，值为空则保留 NULL
    """

    def __init__(self, file_content: bytes | None = None):
        """
        初始化 CSV 适配器

        Args:
            file_content: CSV 文件内容（bytes）
        """
        self.file_content = file_content
        self._df: pd.DataFrame | None = None
        self._timestamp_col: str | None = None
        self._metric_cols: list[str] = []

    def set_content(self, file_content: bytes) -> None:
        """设置 CSV 文件内容"""
        self.file_content = file_content
        self._df = None

    def validate(self) -> bool:
        """
        验证数据源是否有效

        Returns:
            bool: CSV 格式是否有效
        """
        if not self.file_content:
            return False

        try:
            self._ensure_loaded()
            # 检查是否有有效的时间戳列和指标列
            return self._timestamp_col is not None and len(self._metric_cols) > 0
        except Exception:
            return False

    def get_metrics(self) -> dict[str, str]:
        """
        获取数据源中的指标信息

        Returns:
            dict[str, str]: 指标 ID 到指标名称的映射
        """
        self._ensure_loaded()
        return {col: col for col in self._metric_cols}

    def parse(self) -> Iterator[DataPoint]:
        """
        解析 CSV 文件，返回数据点迭代器

        Yields:
            DataPoint: 数据点（metric_id, metric_name, timestamp, value）

        Raises:
            ValueError: CSV 格式不符合要求
        """
        self._ensure_loaded()

        for metric_name in self._metric_cols:
            for _, row in self._df.iterrows():
                value = row[metric_name]
                # 保留 NULL：pandas NaN -> None
                if pd.isna(value):
                    value = None

                yield DataPoint(
                    metric_id=metric_name,  # 使用指标名称作为 ID
                    metric_name=metric_name,
                    timestamp=str(row[self._timestamp_col]),
                    value=value
                )

    def _ensure_loaded(self) -> None:
        """确保 DataFrame 已加载"""
        if self._df is not None:
            return

        if not self.file_content:
            raise ValueError("CSV 文件内容为空")

        # 1. 读取 CSV（UTF-8 编码，处理 BOM）
        self._df = pd.read_csv(io.BytesIO(self.file_content), encoding='utf-8-sig')

        # 2. 识别时间戳列
        self._timestamp_col = self._find_timestamp_column(self._df.columns)

        # 3. 识别指标列（除时间戳外的所有列）
        self._metric_cols = [c for c in self._df.columns if c != self._timestamp_col]

    def _find_timestamp_column(self, columns) -> str:
        """
        识别时间戳列

        支持的列名：timestamp, time, 日期, 时间, ts, datetime
        大小写不敏感
        """
        candidates = ['timestamp', 'time', '日期', '时间', 'ts', 'datetime']
        for col in columns:
            if col.lower() in candidates:
                return col
        raise ValueError("未找到时间戳列，支持的列名：timestamp, time, 日期, 时间, ts, datetime")
