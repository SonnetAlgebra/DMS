"""关联分析接口的 Pydantic 模式定义"""
from pydantic import BaseModel
from typing import List


class CorrelationRequest(BaseModel):
    """关联分析请求"""
    metric_ids: List[int]
    resample: str = "D"  # 重采样频率，默认天（D）


class CorrelationResponse(BaseModel):
    """关联分析响应"""
    matrix: List[List[float]]  # 相关系数矩阵
    metrics: List[int]  # 指标 ID 列表
    common_points: int  # 公共时间点数量


class CorrelationError(BaseModel):
    """关联分析错误"""
    code: str
    message: str
