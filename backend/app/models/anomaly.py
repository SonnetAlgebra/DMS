"""异常记录表模型 - 报警快照"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from ..database import Base


class Anomaly(Base):
    """异常记录表 - 每次检测时删除旧快照，保存新快照"""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False)  # 当时的Z-Score得分
    threshold_used = Column(Float, nullable=False)  # 当时使用的阈值
    mean_used = Column(Float, nullable=False)  # 当时使用的均值
    std_used = Column(Float, nullable=False)  # 当时使用的标准差
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_anomalies_metric", "metric_id"),
    )

    def __repr__(self):
        return f"<Anomaly(id={self.id}, metric_id={self.metric_id}, timestamp={self.timestamp}, z_score={self.z_score})>"
