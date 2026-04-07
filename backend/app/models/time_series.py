from sqlalchemy import Column, Integer, Float, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class TimeSeries(Base):
    """时序数据表 - 按计划书 v1.5 2.4 节定义"""

    __tablename__ = "time_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float)  # 原始值（NULL表示缺失）

    # 外键关联
    metric = relationship("Metric", back_populates="time_series_data")

    # 唯一约束：同一指标同一时间戳只能有一个数据点
    __table_args__ = (
        UniqueConstraint('metric_id', 'timestamp', name='uq_metric_timestamp'),
    )

    def __repr__(self):
        return f"<TimeSeries(metric_id={self.metric_id}, timestamp='{self.timestamp}', value={self.value})>"