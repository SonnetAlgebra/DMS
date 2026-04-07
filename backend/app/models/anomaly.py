from sqlalchemy import Column, Integer, Float, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class Anomaly(Base):
    """异常记录表 - 报警快照，按计划书 v1.5 2.4 节定义"""

    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)  # 当时的数据值（NOT NULL）
    z_score = Column(Float, nullable=False)  # 当时的Z-Score得分（NOT NULL）
    threshold_used = Column(Float, nullable=False)  # 当时使用的阈值（NOT NULL）
    mean_used = Column(Float, nullable=False)  # 当时使用的均值（NOT NULL）
    std_used = Column(Float, nullable=False)  # 当时使用的标准差（NOT NULL）
    detected_at = Column(DateTime, default=func.current_timestamp())

    # 外键关联
    metric = relationship("Metric", back_populates="anomalies")
    alerts = relationship("Alert", back_populates="anomaly")

    def __repr__(self):
        return f"<Anomaly(metric_id={self.metric_id}, timestamp='{self.timestamp}', z_score={self.z_score})>"