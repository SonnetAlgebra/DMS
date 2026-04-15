# DMS 数据监控系统

> Data Monitoring System - 轻量级数据异常检测与可视化平台

## 功能特性

- 📊 **数据上传**：支持 CSV 格式数据导入
- 📈 **时序可视化**：多指标时序图表展示
- 🚨 **异常检测**：基于 Z-Score 算法的动态异常判定
- 🔍 **异常面板**：异常点列表与操作管理
- 🌡️ **关联分析**：指标间 Pearson 相关系数热力图
- ⚙️ **可调阈值**：实时调整 Z-Score 检测阈值

## 环境要求

- Python 3.10+
- Bun 1.0+
- SQLite 3

## 安装

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 前端

```bash
cd frontend
bun install
```

## 启动

### 方式1：一键启动

```bash
start.bat
```

### 方式2：手动启动

```bash
# 终端1：启动后端
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# 终端2：启动前端
cd frontend
bun run dev
```

## 访问

- **前端界面**: http://localhost:5173
- **API 文档**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health

## 数据格式

### CSV 上传格式

| 字段 | 类型 | 说明 |
|------|------|------|
| metric_id | string | 指标唯一标识 |
| metric_name | string | 指标名称 |
| timestamp | datetime | 时间戳（ISO 8601 格式） |
| value | float | 数值（可为空） |

### 示例数据

```csv
metric_id,metric_name,timestamp,value
cpu_usage,CPU 使用率,2024-01-01T00:00:00,45.2
cpu_usage,CPU 使用率,2024-01-01T01:00:00,52.1
cpu_usage,CPU 使用率,2024-01-01T02:00:00,
```

## API 接口

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/data/upload` | POST | 上传 CSV 数据 |
| `/api/v1/metrics` | GET | 获取指标列表 |
| `/api/v1/data/{metric_id}` | GET | 获取时序数据 |
| `/api/v1/detect` | POST | 异常检测 |
| `/api/v1/correlation` | GET | 关联分析 |

完整 API 文档请访问 http://127.0.0.1:8000/docs

## 目录结构

```
DMS/
├── backend/              # 后端代码
│   ├── app/              # FastAPI 应用
│   └── venv/             # Python 虚拟环境
├── frontend/             # 前端代码
│   ├── src/              # Vue 源码
│   └── node_modules/     # 依赖
├── data/                 # 示例数据
├── logs/                 # 日志目录
└── README.md            # 本文件
```

## 技术栈

- **后端**: FastAPI + SQLite
- **前端**: Vue 3 + TypeScript + Vite + ECharts
- **构建**: Bun

## 许可

MIT License
