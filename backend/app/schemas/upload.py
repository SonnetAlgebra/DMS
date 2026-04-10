"""上传接口的 Pydantic 模式定义"""
from pydantic import BaseModel
from typing import List


class MetricInfo(BaseModel):
    """导入的指标信息"""
    id: int
    name: str


class UploadResponse(BaseModel):
    """CSV 上传响应"""
    success: bool
    inserted: int          # 插入的数据点总数
    metrics: List[MetricInfo]    # 导入的指标列表
