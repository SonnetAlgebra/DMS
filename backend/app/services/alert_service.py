"""报警引擎服务"""
import logging
import os

# 日志配置：同时输出到文件和控制台
log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
log_file = os.path.join(log_dir, "alerts.log")

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('alert')


def alert(metric_name: str, anomaly: dict):
    """
    触发报警日志

    Args:
        metric_name: 指标名称
        anomaly: 异常点数据字典，包含 timestamp, value, z_score 等字段
    """
    logger.warning(
        f"[ALERT] {metric_name} 异常: "
        f"时间={anomaly.get('timestamp')}, "
        f"值={anomaly.get('value')}, "
        f"Z-Score={anomaly.get('z_score'):.2f}"
    )
