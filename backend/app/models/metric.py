from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base


class Metric(Base):
    """指标定义表 - 按计划书 v1.5 2.4 节定义"""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200))
    unit = Column(String(20))
    created_at = Column(DateTime, default=func.current_timestamp())

    # 关联关系
    time_series_data = relationship("TimeSeries", back_populates="metric")
    anomalies = relationship("Anomaly", back_populates="metric")
    alerts = relationship("Alert", back_populates="metric")

    def __repr__(self):
        return f"<Metric(name='{self.name}', unit='{self.unit}')>"