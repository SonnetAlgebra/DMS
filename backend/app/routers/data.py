"""时序数据查询 API 路由"""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.data import DataResponse, DataPoint
from app.services.anomaly import AnomalyService
from app.config import settings
import sqlite3

router = APIRouter()
anomaly_service = AnomalyService()
DB_PATH = settings.database_path
MAX_LIMIT = 5000


@router.get("/{metric_id}/data", response_model=DataResponse)
async def get_metric_data(
    metric_id: int,
    threshold: float = Query(3.0, description="Z-Score 阈值", ge=0.1, le=10.0),
    limit: int = Query(1000, description="返回条数限制", ge=1, le=MAX_LIMIT),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """
    获取指定指标的时序数据（含动态异常判定）

    接口路径: /api/v1/metrics/{metric_id}/data

    参数:
        metric_id: 指标 ID
        threshold: Z-Score 阈值，默认 3.0
        limit: 返回条数限制，最大 5000
        offset: 偏移量，用于分页

    方案4: 分页全局统计量
    - 先查询全部数据（limit=5000内）计算全局 mean/std
    - 再分页返回具体数据
    - 保证翻页时判定标准一致
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 检查指标是否存在
    cursor.execute("SELECT id FROM metrics WHERE id = ?", (metric_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="指标不存在")

    # 2. 查询总数
    cursor.execute(
        "SELECT COUNT(*) FROM time_series WHERE metric_id = ?",
        (metric_id,)
    )
    total = cursor.fetchone()[0]

    # 3. 方案4：先查询全部数据计算全局统计量（limit=5000限制）
    cursor.execute(
        """
        SELECT timestamp, value
        FROM time_series
        WHERE metric_id = ?
        ORDER BY timestamp
        LIMIT ?
        """,
        (metric_id, MAX_LIMIT)
    )
    all_rows = cursor.fetchall()

    # 4. 提取全部数值用于计算全局统计量
    all_values = [row[1] for row in all_rows]

    # 5. 执行异常检测（基于全部数据）
    result = anomaly_service.detect(all_values, threshold)

    # 6. 处理错误
    if "error" in result:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

    # 7. 分页查询返回数据（使用 all_rows 进行切片）
    if offset >= len(all_rows):
        # offset 超过总数，返回空数组
        data_points = []
    else:
        page_rows = all_rows[offset:offset + limit]
        # 注意：z_scores 需要根据 offset 进行对齐
        data_points = []
        for i, row in enumerate(page_rows):
            global_index = offset + i
            is_anomaly = result["z_scores"][global_index] > threshold if result["std"] > 0 else False
            data_points.append(
                DataPoint(
                    timestamp=row[0],
                    value=row[1],
                    is_anomaly=is_anomaly,
                    z_score=result["z_scores"][global_index]
                )
            )

    conn.close()

    return DataResponse(
        data=data_points,
        mean=result["mean"],
        std=result["std"],
        limit=limit,
        offset=offset,
        total=total
    )
