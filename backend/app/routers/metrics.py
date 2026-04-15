"""指标列表 API 路由"""
from fastapi import APIRouter
from app.schemas.data import MetricsListResponse, MetricInfo
from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("", response_model=MetricsListResponse)
async def get_metrics():
    """
    获取所有指标列表

    接口路径: /api/v1/metrics
    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, description, unit FROM metrics ORDER BY id"
        )
        rows = cursor.fetchall()

    metrics = [
        MetricInfo(
            id=row[0],
            name=row[1],
            description=row[2],
            unit=row[3]
        )
        for row in rows
    ]

    return MetricsListResponse(
        metrics=metrics,
        total=len(metrics)
    )
