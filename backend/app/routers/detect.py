"""异常检测 API 路由"""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.data import DetectRequest, DetectResponse, AnomalyPoint
from app.services.anomaly import AnomalyService
from app.services import alert_service
from app.config import settings
from app.database import get_db
from datetime import datetime

router = APIRouter()
anomaly_service = AnomalyService()
MAX_LIMIT = 5000


@router.post("/detect", response_model=DetectResponse)
async def detect_anomalies(request: DetectRequest):
    """
    异常检测并保存快照

    接口路径: /api/v1/metrics/detect

    参数:
        metric_id: 指标 ID
        threshold: Z-Score 阈值，默认 3.0

    流程:
        1. 查询该指标全部数据（limit=5000）计算统计量
        2. 计算Z-Score，筛选异常点
        3. 删除该指标旧异常快照
        4. 保存新异常快照（含threshold_used/mean_used/std_used）
        5. 返回异常点列表
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. 检查指标是否存在，同时获取指标名称
        cursor.execute("SELECT id, name FROM metrics WHERE id = ?", (request.metric_id,))
        metric = cursor.fetchone()
        if metric is None:
            raise HTTPException(status_code=404, detail="指标不存在")
        metric_id, metric_name = metric

        # 2. 查询该指标全部数据（limit=5000限制）
        cursor.execute(
            """
            SELECT timestamp, value
            FROM time_series
            WHERE metric_id = ?
            ORDER BY timestamp
            LIMIT ?
            """,
            (request.metric_id, MAX_LIMIT)
        )
        all_rows = cursor.fetchall()

        if len(all_rows) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INSUFFICIENT_DATA",
                    "message": "有效数据点不足2个"
                }
            )

        # 3. 提取全部数值用于计算全局统计量
        all_values = [row[1] for row in all_rows]

        # 4. 执行异常检测（基于全部数据）
        result = anomaly_service.detect(all_values, request.threshold)

        # 5. 处理错误
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )

        mean = result["mean"]
        std = result["std"]
        z_scores = result["z_scores"]

        # 6. 筛选异常点（z_score > threshold）
        anomaly_points = []
        for i, (timestamp, value) in enumerate(all_rows):
            z_score = z_scores[i]
            if z_score > request.threshold and value is not None:
                anomaly_points.append({
                    "timestamp": timestamp,
                    "value": value,
                    "z_score": z_score
                })

        # 7. 删除该指标旧异常快照
        cursor.execute(
            "DELETE FROM anomalies WHERE metric_id = ?",
            (request.metric_id,)
        )

        # 8. 保存新异常快照
        detected_at = datetime.now().isoformat()
        for anomaly in anomaly_points:
            cursor.execute(
                """
                INSERT INTO anomalies
                (metric_id, timestamp, value, z_score, threshold_used, mean_used, std_used, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.metric_id,
                    anomaly["timestamp"],
                    anomaly["value"],
                    anomaly["z_score"],
                    request.threshold,
                    mean,
                    std,
                    detected_at
                )
            )

        conn.commit()

    # 触发报警：对每个异常点记录报警日志
    for anomaly in anomaly_points:
        alert_service.alert(metric_name, anomaly)

    return DetectResponse(
        anomalies=[AnomalyPoint(**a) for a in anomaly_points],
        count=len(anomaly_points),
        mean=mean,
        std=std,
        threshold_used=request.threshold
    )
