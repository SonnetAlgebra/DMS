"""数据接口的 Pydantic 模式定义"""
from pydantic import BaseModel
from typing import List, Optional


class DataPoint(BaseModel):
    """时序数据点"""
    timestamp: str
    value: Optional[float]        # NULL 表示缺失值
    is_anomaly: bool = False
    z_score: float = 0.0


class DataResponse(BaseModel):
    """时序数据响应"""
    data: List[DataPoint]
    mean: Optional[float] = None
    std: Optional[float] = None
    limit: int
    offset: int
    total: int


class MetricInfo(BaseModel):
    """指标信息"""
    id: int
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None


class MetricsListResponse(BaseModel):
    """指标列表响应"""
    metrics: List[MetricInfo]
    total: int
