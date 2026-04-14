"""CSV 上传 API 路由"""
from fastapi import APIRouter, UploadFile, File
from app.adapters.csv_adapter import CSVAdapter
from app.schemas.upload import UploadResponse, MetricInfo
from app.config import settings
import sqlite3
from datetime import datetime

router = APIRouter()
DB_PATH = settings.database_path  # 使用配置文件中的数据库路径


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    上传 CSV 文件并导入时序数据

    接口路径: /api/v1/data/upload

    流程：
        1. 读取文件内容
        2. 使用 CSVAdapter 解析（适配器模式）
        3. 原生 SQLite 操作，保留 NULL，避免重复

    Returns:
        UploadResponse: 包含导入成功数量和指标列表
    """
    # 1. 读取文件内容
    content = await file.read()

    # 2. 使用 CSVAdapter 解析（适配器模式）
    adapter = CSVAdapter(content)

    # 验证数据源
    if not adapter.validate():
        raise ValueError("CSV 格式无效，无法解析")

    # 3. 获取指标信息
    metrics_info = adapter.get_metrics()

    # 4. 原生 SQLite 操作
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted_count = 0
    imported_metrics = []
    metric_id_map: dict[str, int] = {}  # metric_name -> metric_id

    try:
        # 先创建或获取所有指标
        for metric_name in metrics_info.values():
            cursor.execute("SELECT id FROM metrics WHERE name = ?", (metric_name,))
            row = cursor.fetchone()
            if row:
                metric_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO metrics (name, description) VALUES (?, ?)",
                    (metric_name, f"指标: {metric_name}")
                )
                metric_id = cursor.lastrowid
                imported_metrics.append({"id": metric_id, "name": metric_name})
            metric_id_map[metric_name] = metric_id

        # 批量插入时序数据（保留 NULL，避免重复）
        for data_point in adapter.parse():
            metric_id = metric_id_map[data_point.metric_name]

            # 先检查是否已存在（metric_id + timestamp 组合）
            cursor.execute(
                "SELECT id FROM time_series WHERE metric_id = ? AND timestamp = ?",
                (metric_id, data_point.timestamp)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO time_series (metric_id, timestamp, value) VALUES (?, ?, ?)",
                    (metric_id, data_point.timestamp, data_point.value)
                )
                inserted_count += 1

        conn.commit()
    finally:
        conn.close()

    return UploadResponse(
        success=True,
        inserted=inserted_count,
        metrics=[MetricInfo(id=m["id"], name=m["name"]) for m in imported_metrics]
    )
