"""异常检测服务 - Z-Score 算法"""
import numpy as np
from typing import List, Dict, Optional


class AnomalyService:
    """异常检测服务 - Z-Score 算法"""

    def detect(self, values: List[Optional[float]], threshold: float = 3.0) -> Dict:
        """
        执行 Z-Score 异常检测

        参数:
            values: 数值列表（含 None 表示缺失值）
            threshold: Z-Score 阈值，默认 3.0

        返回: {mean, std, z_scores, error}
        """
        # 1. 过滤有效值
        valid_values = [v for v in values if v is not None]

        # 2. 边界判断：有效数据点 < 2
        if len(valid_values) < 2:
            return {
                "error": {
                    "code": "INSUFFICIENT_DATA",
                    "message": "有效数据点不足2个"
                }
            }

        # 3. 计算统计量（全局）
        mean = float(np.mean(valid_values))
        std = float(np.std(valid_values))

        # 4. 除零保护：标准差为 0 时 z_scores 返回 0
        z_scores = []
        for v in values:
            if v is None:
                z_scores.append(0.0)
            elif std == 0:
                z_scores.append(0.0)
            else:
                z_scores.append(abs((v - mean) / std))

        return {
            "mean": mean,
            "std": std,
            "z_scores": z_scores
        }
