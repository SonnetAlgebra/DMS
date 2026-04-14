"""Pearson 关联分析服务"""
import pandas as pd
import sqlite3
from typing import List, Dict, Tuple, Optional
from scipy.stats import pearsonr


class CorrelationService:
    """Pearson 相关性分析服务"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_series(self, metric_id: int) -> pd.Series:
        """
        查询指定指标的时序数据

        Args:
            metric_id: 指标 ID

        Returns:
            pandas Series，index 为 timestamp，value 为数据值
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, value
            FROM time_series
            WHERE metric_id = ?
            ORDER BY timestamp
            """,
            (metric_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return pd.Series(dtype=float)

        # 转换为 pandas Series
        data = [(row['timestamp'], row['value']) for row in rows if row['value'] is not None]
        if not data:
            return pd.Series(dtype=float)

        timestamps, values = zip(*data)
        # 标准化时间戳格式：移除 T00:00:00 后缀
        normalized_timestamps = [ts.split('T')[0] if 'T' in ts else ts for ts in timestamps]
        return pd.Series(values, index=pd.to_datetime(normalized_timestamps))

    def resample_series(self, series: pd.Series, freq: str) -> pd.Series:
        """
        对时序数据进行重采样（取均值）

        Args:
            series: 原始时序数据
            freq: 重采样频率（如 "D"=天, "H"=小时, "W"=周）

        Returns:
            重采样后的 Series
        """
        if series.empty:
            return series
        return series.resample(freq).mean()

    def calculate_correlation(
        self,
        metric_ids: List[int],
        resample: str = "D"
    ) -> Dict:
        """
        计算多指标间的 Pearson 相关系数矩阵

        Args:
            metric_ids: 指标 ID 列表
            resample: 重采样频率，默认 "D"（天）

        Returns:
            {
                "matrix": [[r11, r12, ...], [r21, r22, ...], ...],  # 相关系数矩阵
                "metrics": [id1, id2, ...],  # 指标 ID 列表
                "common_points": N  # 公共时间点数量
            }

        错误返回:
            {
                "error": {
                    "code": "INSUFFICIENT_DATA",
                    "message": "有效数据点不足3对"
                }
            }
        """
        if len(metric_ids) < 2:
            return {
                "error": {
                    "code": "INVALID_INPUT",
                    "message": "至少需要2个指标才能计算相关性"
                }
            }

        # 1. 查询各指标时序数据
        series_list = []
        for metric_id in metric_ids:
            series = self.get_series(metric_id)
            if series.empty:
                return {
                    "error": {
                        "code": "NO_DATA",
                        "message": f"指标 {metric_id} 没有有效数据"
                    }
                }
            series_list.append(series)

        # 2. 重采样
        resampled_list = [self.resample_series(s, resample) for s in series_list]

        # 3. 取时间交集
        common_idx = resampled_list[0].index
        for series in resampled_list[1:]:
            common_idx = common_idx.intersection(series.index)

        if len(common_idx) < 3:
            return {
                "error": {
                    "code": "INSUFFICIENT_DATA",
                    "message": f"有效数据点不足3对（实际：{len(common_idx)}对）"
                }
            }

        # 4. 计算相关系数矩阵
        n = len(metric_ids)
        matrix = []

        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                else:
                    # 取公共时间点的数据
                    s1 = resampled_list[i][common_idx]
                    s2 = resampled_list[j][common_idx]
                    # 移除 NaN
                    mask = ~(s1.isna() | s2.isna())
                    s1_clean = s1[mask]
                    s2_clean = s2[mask]

                    if len(s1_clean) < 3:
                        return {
                            "error": {
                                "code": "INSUFFICIENT_DATA",
                                "message": f"指标 {metric_ids[i]} 与 {metric_ids[j]} 有效数据点不足3对（实际：{len(s1_clean)}对）"
                            }
                        }

                    # 计算 Pearson 相关系数
                    try:
                        r, _ = pearsonr(s1_clean, s2_clean)
                        row.append(round(float(r), 2))
                    except Exception:
                        # 计算失败时返回 NaN
                        row.append(float('nan'))

            matrix.append(row)

        return {
            "matrix": matrix,
            "metrics": metric_ids,
            "common_points": len(common_idx)
        }
