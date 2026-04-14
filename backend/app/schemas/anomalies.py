"""异常查询 API 数据模型"""
from pydantic import BaseModel


class AnomalyDetail(BaseModel):
    """异常记录详情"""
    id: int
    metric_id: int
    metric_name: str
    timestamp: str
    value: float
    z_score: float
    threshold_used: float
    mean_used: float
    std_used: float
    detected_at: str

    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    """异常记录列表响应"""
    anomalies: list[AnomalyDetail]
    total: int
    metric_id: int | None = None
