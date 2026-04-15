"""数据库连接配置"""
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLite 数据库连接
DATABASE_URL = f"sqlite:///{settings.database_path}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # 设为 True 可查看 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础类
Base = declarative_base()

# 元数据（延迟创建）
metadata = None


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    global metadata
    metadata = MetaData()
    Base.metadata.create_all(bind=engine)


# ============================================================================
# 原生 SQLite 连接池（用于路由层）
# ============================================================================
DB_PATH = settings.database_path


@contextmanager
def get_db():
    """
    获取原生 SQLite 数据库连接（上下文管理器）

    用法:
        with get_db() as conn:
            cursor = conn.cursor()
            # ... 执行 SQL 操作
            conn.commit()
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()
