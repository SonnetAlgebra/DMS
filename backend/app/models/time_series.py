"""时序数据表模型 - 仅存储原始数据"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from ..database import Base


class TimeSeries(Base):
    """时序数据表"""

    __tablename__ = "time_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=True)  # NULL 表示缺失值，不填充默认值

    # 复合索引优化查询 (metric_id, timestamp)
    __table_args__ = (
        Index("idx_time_series_metric_time", "metric_id", "timestamp"),
    )

    def __repr__(self):
        return f"<TimeSeries(id={self.id}, metric_id={self.metric_id}, timestamp={self.timestamp}, value={self.value})>"
