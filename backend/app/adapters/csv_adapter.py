"""CSV 适配器 - 解析 CSV 文件提取指标和数据"""
import pandas as pd
from typing import List, Dict, Tuple
import io


class CSVAdapter:
    """CSV 数据解析适配器"""

    def parse(self, file_content: bytes) -> Tuple[List[str], List[Dict]]:
        """
        解析 CSV 文件

        返回: (指标名称列表, 数据点列表)
        数据点格式: {metric_name, timestamp, value}
        """
        # 1. 读取 CSV（UTF-8 编码，处理 BOM）
        df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8-sig')

        # 2. 识别时间戳列（支持 timestamp/time/日期，大小写不敏感）
        timestamp_col = self._find_timestamp_column(df.columns)

        # 3. 识别数值列（除时间戳外的所有列）
        metric_cols = [c for c in df.columns if c != timestamp_col]

        # 4. 转换为标准格式，保留 NULL
        data_points = []
        for col in metric_cols:
            for _, row in df.iterrows():
                value = row[col]
                # 保留 NULL：pandas NaN -> None
                if pd.isna(value):
                    value = None
                data_points.append({
                    "metric_name": col,
                    "timestamp": row[timestamp_col],
                    "value": value
                })

        return metric_cols, data_points

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
        raise ValueError("未找到时间戳列")
