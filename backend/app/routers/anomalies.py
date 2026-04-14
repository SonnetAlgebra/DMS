"""异常查询 API 路由"""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.anomalies import AnomalyListResponse, AnomalyDetail
from app.config import settings
import sqlite3

router = APIRouter()
DB_PATH = settings.database_path


@router.get("/anomalies", response_model=AnomalyListResponse)
async def get_anomalies(
    metric_id: int | None = Query(None, description="指标 ID，不传则返回所有指标的异常"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制，默认 100，最大 500"),
    offset: int = Query(0, ge=0, description="偏移量，用于分页")
):
    """
    获取异常记录（历史快照）

    接口路径: /api/v1/anomalies

    参数:
        metric_id: 指标 ID，不传则返回所有指标的异常
        limit: 返回数量限制（默认 100，最大 500）
        offset: 偏移量（默认 0）

    返回:
        - anomalies: 异常记录列表
        - total: 总数
        - metric_id: 当前查询的指标 ID（如果指定）

    说明:
        - 异常记录是 /detect 接口保存的快照
        - 每次检测会删除该指标的旧快照并保存新快照
        - 返回按检测时间倒序排列
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 构建查询条件
    if metric_id is not None:
        # 检查指标是否存在
        cursor.execute("SELECT id, name FROM metrics WHERE id = ?", (metric_id,))
        metric = cursor.fetchone()
        if metric is None:
            conn.close()
            raise HTTPException(status_code=404, detail="指标不存在")

        # 查询特定指标的异常记录
        cursor.execute(
            """
            SELECT a.*, m.name as metric_name
            FROM anomalies a
            JOIN metrics m ON a.metric_id = m.id
            WHERE a.metric_id = ?
            ORDER BY a.detected_at DESC, a.timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (metric_id, limit, offset)
        )

        # 查询总数
        cursor.execute(
            "SELECT COUNT(*) FROM anomalies WHERE metric_id = ?",
            (metric_id,)
        )
        total = cursor.fetchone()[0]
    else:
        # 查询所有指标的异常记录
        cursor.execute(
            """
            SELECT a.*, m.name as metric_name
            FROM anomalies a
            JOIN metrics m ON a.metric_id = m.id
            ORDER BY a.detected_at DESC, a.timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )

        # 查询总数
        cursor.execute("SELECT COUNT(*) FROM anomalies")
        total = cursor.fetchone()[0]

    rows = cursor.fetchall()
    conn.close()

    anomalies = [
        AnomalyDetail(
            id=row["id"],
            metric_id=row["metric_id"],
            metric_name=row["metric_name"],
            timestamp=row["timestamp"],
            value=row["value"],
            z_score=row["z_score"],
            threshold_used=row["threshold_used"],
            mean_used=row["mean_used"],
            std_used=row["std_used"],
            detected_at=row["detected_at"]
        )
        for row in rows
    ]

    return AnomalyListResponse(
        anomalies=anomalies,
        total=total,
        metric_id=metric_id
    )
