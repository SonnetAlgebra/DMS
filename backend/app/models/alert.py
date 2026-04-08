"""报警记录表模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from ..database import Base


class Alert(Base):
    """报警记录表"""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, resolved, dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_alerts_status", "status"),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, status='{self.status}', metric_id={self.metric_id})>"
