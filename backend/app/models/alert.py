from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Alert(Base):
    """报警记录表 - 按计划书 v1.5 2.4 节定义"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anomaly_id = Column(Integer, nullable=False)
    metric_id = Column(Integer, nullable=False)
    message = Column(String(20))  # 报警消息
    status = Column(String(20), default='pending')  # 状态：pending, acknowledged, resolved
    created_at = Column(DateTime, default=func.current_timestamp())

    # 外键关联
    anomaly = relationship("Anomaly", back_populates="alerts")
    metric = relationship("Metric", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, status='{self.status}', created_at='{self.created_at}')>"