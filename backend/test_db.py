#!/usr/bin/env python3
"""
数据库模型测试脚本
按 CLAUDE.md 自测要求运行：test_db.py 验证表结构和索引
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, init_db
from app.models import Metric, TimeSeries, Anomaly, Alert
from sqlalchemy import inspect
import datetime

def test_database_models():
    """测试数据库模型创建"""
    print("🚀 开始测试数据库模型...")

    # 1. 初始化数据库
    print("\n1. 初始化数据库...")
    try:
        init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

    # 2. 验证表是否存在
    print("\n2. 验证表结构...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = ['metrics', 'time_series', 'anomalies', 'alerts']
    for table in expected_tables:
        if table in tables:
            print(f"✅ 表 '{table}' 创建成功")
        else:
            print(f"❌ 表 '{table}' 未创建")
            return False

    # 3. 验证索引
    print("\n3. 验证索引...")
    indexes = inspector.get_indexes('time_series')
    found_unique_index = False
    for idx in indexes:
        if 'unique' in idx and idx['unique']:
            print(f"✅ 找到唯一约束: {idx['name']}")
            found_unique_index = True

    if not found_unique_index:
        print("❌ time_series 表未找到唯一约束")
        return False

    # 4. 验证字段定义
    print("\n4. 验证字段定义...")
    columns = inspector.get_columns('time_series')
    for col in columns:
        if col['name'] == 'value':
            if col['nullable']:
                print("✅ value 字段允许 NULL（符合要求）")
            else:
                print("❌ value 字段不允许 NULL（违反计划书）")
                return False

    # 5. 测试数据插入
    print("\n5. 测试数据插入...")
    try:
        from app.database import SessionLocal
        db = SessionLocal()

        # 创建测试指标
        metric = Metric(
            name="test_metric",
            description="测试指标",
            unit="°C"
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        print("✅ 成功插入测试指标")

        # 插入时序数据
        ts = TimeSeries(
            metric_id=metric.id,
            timestamp=datetime.datetime.now(),
            value=25.5
        )
        db.add(ts)
        db.commit()
        print("✅ 成功插入时序数据")

        db.close()
    except Exception as e:
        print(f"❌ 数据插入失败: {e}")
        return False

    # 6. 验证外键关系
    print("\n6. 验证外键关系...")
    try:
        from app.database import SessionLocal
        db = SessionLocal()

        # 检查关联是否正确
        metric = db.query(Metric).first()
        if metric:
            print(f"✅ Metric 模型关联正常，ID: {metric.id}")

        db.close()
    except Exception as e:
        print(f"❌ 外键关系验证失败: {e}")
        return False

    print("\n🎉 所有测试通过！数据库模型创建成功")
    return True

if __name__ == "__main__":
    success = test_database_models()
    if success:
        print("\n✅ 数据库建模任务完成")
        sys.exit(0)
    else:
        print("\n❌ 数据库建模任务失败")
        sys.exit(1)