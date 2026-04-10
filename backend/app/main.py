from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path
from app.config import settings

# 数据库初始化（原生 SQLite）
DB_PATH = settings.database_path


def init_db():
    """初始化数据库（原生 SQLite）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 创建指标定义表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(200),
            unit VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. 创建时序数据表（无 UNIQUE 约束）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            value REAL,
            FOREIGN KEY (metric_id) REFERENCES metrics(id)
        )
    """)

    # 3. 创建异常记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            value REAL NOT NULL,
            z_score REAL NOT NULL,
            threshold_used REAL NOT NULL,
            mean_used REAL NOT NULL,
            std_used REAL NOT NULL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (metric_id) REFERENCES metrics(id)
        )
    """)

    # 4. 创建报警记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anomaly_id INTEGER NOT NULL,
            metric_id INTEGER NOT NULL,
            message TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (metric_id) REFERENCES metrics(id)
        )
    """)

    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_series_metric_time ON time_series(metric_id, timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_metric ON anomalies(metric_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")

    conn.commit()
    conn.close()


app = FastAPI(title="DMS API", version="1.0.0")

# 初始化数据库
init_db()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return JSONResponse(status_code=200, content={"status": "ok"})


# 注册路由
from app.routers import upload
app.include_router(upload.router, prefix="/api/v1/data", tags=["data"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
