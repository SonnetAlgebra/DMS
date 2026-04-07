#!/usr/bin/env python3
"""
简化的数据库初始化脚本
"""

import sqlite3
import os
import sys

# 设置编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def init_database():
    """直接使用 SQLite 创建数据库表"""
    db_path = "dms.db"

    # 删除已存在的数据库文件
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== 开始创建数据库表 ===")

    # 1. 创建指标定义表
    print("\n[1/4] 创建 metrics 表...")
    cursor.execute('''
        CREATE TABLE metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(200),
            unit VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("SUCCESS: metrics 表创建成功")

    # 2. 创建时序数据表
    print("\n[2/4] 创建 time_series 表...")
    cursor.execute('''
        CREATE TABLE time_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            value REAL,                          -- 原始值（NULL表示缺失）
            FOREIGN KEY (metric_id) REFERENCES metrics(id),
            UNIQUE(metric_id, timestamp)
        )
    ''')
    # 添加复合索引
    cursor.execute('''
        CREATE INDEX idx_time_series_metric_time ON time_series(metric_id, timestamp)
    ''')
    print("SUCCESS: time_series 表创建成功")

    # 3. 创建异常记录表
    print("\n[3/4] 创建 anomalies 表...")
    cursor.execute('''
        CREATE TABLE anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            value REAL NOT NULL,
            z_score REAL NOT NULL,               -- 当时的Z-Score得分
            threshold_used REAL NOT NULL,        -- 当时使用的阈值
            mean_used REAL NOT NULL,             -- 当时使用的均值
            std_used REAL NOT NULL,              -- 当时使用的标准差
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (metric_id) REFERENCES metrics(id)
        )
    ''')
    # 添加索引
    cursor.execute('''
        CREATE INDEX idx_anomalies_metric ON anomalies(metric_id)
    ''')
    print("SUCCESS: anomalies 表创建成功")

    # 4. 创建报警记录表
    print("\n[4/4] 创建 alerts 表...")
    cursor.execute('''
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anomaly_id INTEGER NOT NULL,
            metric_id INTEGER NOT NULL,
            message TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (metric_id) REFERENCES metrics(id)
        )
    ''')
    # 添加索引
    cursor.execute('''
        CREATE INDEX idx_alerts_status ON alerts(status)
    ''')
    print("SUCCESS: alerts 表创建成功")

    # 5. 验证表结构
    print("\n[5/5] 验证表结构...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    expected_tables = ['metrics', 'time_series', 'anomalies', 'alerts']
    for table in tables:
        table_name = table[0]
        if table_name in expected_tables:
            print(f"OK: 表 '{table_name}' 存在")
        else:
            print(f"WARN: 表 '{table_name}' 不在预期列表中")

    # 6. 插入测试数据
    print("\n[6/6] 插入测试数据...")
    cursor.execute('''
        INSERT INTO metrics (name, description, unit)
        VALUES ('test_metric', '测试指标', '°C')
    ''')
    metric_id = cursor.lastrowid

    cursor.execute('''
        INSERT INTO time_series (metric_id, timestamp, value)
        VALUES (?, datetime('now'), ?)
    ''', (metric_id, 25.5))
    print("SUCCESS: 测试数据插入成功")

    conn.commit()
    conn.close()

    print("\n=== 数据库创建成功！===")
    print("\n表结构摘要：")
    print("- metrics: 指标定义表")
    print("- time_series: 时序数据表（带唯一约束和复合索引）")
    print("- anomalies: 异常快照表（记录上下文）")
    print("- alerts: 报警记录表")

    return True

if __name__ == "__main__":
    init_database()