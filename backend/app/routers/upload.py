"""CSV 上传 API 路由"""
from fastapi import APIRouter, UploadFile, File
from app.adapters.csv_adapter import CSVAdapter
from app.schemas.upload import UploadResponse, MetricInfo
from app.config import settings
import sqlite3
from datetime import datetime

router = APIRouter()
adapter = CSVAdapter()
DB_PATH = settings.database_path  # 使用配置文件中的数据库路径


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    上传 CSV 文件并导入时序数据

    接口路径: /api/v1/data/upload
    """
    # 1. 读取文件内容
    content = await file.read()

    # 2. 解析 CSV
    metric_names, data_points = adapter.parse(content)

    # 3. 原生 SQLite 操作
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted_count = 0
    imported_metrics = []

    try:
        for metric_name in metric_names:
            # 检查/创建指标
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

            # 批量插入时序数据（保留 NULL，避免重复）
            metric_data = [d for d in data_points if d["metric_name"] == metric_name]
            for d in metric_data:
                # 先检查是否已存在（metric_id + timestamp 组合）
                cursor.execute(
                    "SELECT id FROM time_series WHERE metric_id = ? AND timestamp = ?",
                    (metric_id, d["timestamp"])
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO time_series (metric_id, timestamp, value) VALUES (?, ?, ?)",
                        (metric_id, d["timestamp"], d["value"])
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
