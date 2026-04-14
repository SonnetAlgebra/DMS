"""关联分析 API 路由"""
from fastapi import APIRouter, HTTPException
from app.schemas.correlation import CorrelationRequest, CorrelationResponse
from app.services.correlation import CorrelationService
from app.config import settings

router = APIRouter()
correlation_service = CorrelationService(settings.database_path)


@router.post("/correlation", response_model=CorrelationResponse)
async def correlation_analysis(request: CorrelationRequest):
    """
    Pearson 关联分析接口

    接口路径: /api/v1/correlation

    参数:
        metric_ids: 指标 ID 列表（至少2个）
        resample: 重采样频率，默认 "D"（天）

    返回:
        - matrix: 相关系数矩阵（N x N）
        - metrics: 指标 ID 列表
        - common_points: 公共时间点数量

    错误:
        - INSUFFICIENT_DATA: 有效数据点不足3对
        - NO_DATA: 指标没有有效数据
        - INVALID_INPUT: 输入参数无效
    """
    if len(request.metric_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_INPUT",
                "message": "至少需要2个指标才能计算相关性"
            }
        )

    result = correlation_service.calculate_correlation(
        metric_ids=request.metric_ids,
        resample=request.resample
    )

    if "error" in result:
        error = result["error"]
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return CorrelationResponse(
        matrix=result["matrix"],
        metrics=result["metrics"],
        common_points=result["common_points"]
    )
