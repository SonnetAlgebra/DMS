# CLAUDE.md

This file is the **Core Discipline (核心戒律)** for Claude Code when working in this repository.

## 核心戒律 (Core Discipline)

### 1. 会话启动必报

每次会话开始，必须主动报告：

> "已读取《项目情况说明.md》、《CLAUDE.md》与《PROJECT_STATE.md》，当前任务节点为 [任务名]，准备就绪。"

### 2. 熔断机制 (Circuit Breaker)

同一报错重试 **3 次**失败必须停止，执行以下操作：

1. **停止当前任务**
2. **输出请求协助信息**，格式如下：

```
【请求协助】
错误堆栈：<完整错误信息>
涉及代码变更：<已修改的文件和代码段>
尝试次数：3次均已失败
```

3. 等待技术负责人指示后再继续

### 3. 自测要求 (Self-Testing)

所有功能必须通过本地验证方可提交：

| 功能类型 | 验证方式 |
|----------|----------|
| /health 接口 | `curl http://127.0.0.1:8000/health` |
| 数据库建模 | 运行 `test_db.py` 验证表结构和索引 |
| API 接口 | 使用 curl 或 Postman 验证返回结果 |
| 业务逻辑 | 编写单元测试或集成测试 |

**原则**：不测不交，任何代码提交前必须经过本地验证。

### 4. Git 规范 (Git Standards)

功能闭环后必须执行 `git commit`，**代替原有的 md 日志**：

```bash
git add .
git commit -m "<详细的技术实现描述>"
```

**Commit Message 要求**：
- 详细描述技术实现逻辑
- 说明修改的文件和原因
- 记录关键参数变更（如阈值调整）
- 包含自测结果验证

**示例**：
```
feat: 实现 time_series 表创建

- 创建 SQLAlchemy ORM 模型 TimeSeries
- 添加复合索引 (metric_id, timestamp)
- 字段完全按计划书 2.4 节定义
- value 字段允许 NULL 值

自测：运行 test_db.py 验证通过，表结构正确
```

**版本控制过滤红线**：
- 提交前必须运行 `git status` 确认工作区干净
- 发现已提交的敏感文件必须立即从 Git 历史中清除

**.gitignore 架构规范（前后端分离策略）**：

| 位置 | 用途 | 必须忽略的内容 |
|------|------|----------------|
| `DMS/.gitignore` | 项目根（全局） | IDE 配置、操作系统缓存、临时文件 |
| `DMS/backend/.gitignore` | 后端专用 | Python 缓存、venv、环境变量、数据库文件、测试覆盖率 |
| `DMS/frontend/.gitignore` | 前端专用 | node_modules、构建产物、环境变量、日志、缓存 |

**根目录 .gitignore（全局规则）**：
```
# IDE 配置
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统文件
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.temp
```

**backend/.gitignore（后端规则）**：
```
# Python 编译和缓存文件
__pycache__/
*.py[cod]
*.pyo
*$py.class

# Python 打包和分发
build/
dist/
*.egg-info/

# 虚拟环境
venv/
env/
ENV/

# 环境变量和敏感配置
.env
.env.local
.env.*.local

# 数据库文件（仅用于开发）
*.db
*.sqlite
*.sqlite3

# 日志文件
*.log
logs/

# 测试覆盖率
.coverage
.pytest_cache/
htmlcov/
.cache/
coverage.xml
```

**frontend/.gitignore（前端规则）**：
```
# Node.js 依赖
node_modules/

# 构建产物
dist/
build/

# 环境变量
.env
.env.local
.env.*.local

# 日志文件
*.log
logs/

# 缓存
.cache/
.vite/
```

**维护原则**：
- 新增子目录时，立即检查是否需要添加对应的 .gitignore
- 修改技术栈时，同步更新对应的 .gitignore 规则
- 与 PROJECT_STATE.md 保持同步，项目结构变化时同步维护

### 5. 技术红线 (Technical Red Lines)

以下为不可逾越的技术底线：

| 红线项 | 要求 |
|--------|------|
| **架构** | FastAPI + SQLite 架构，禁止更换技术栈 |
| **除零保护** | Z-Score 计算必须除零保护（std=0 时返回 NULL） |
| **缺失值处理** | 数据库中缺失值必须返回 NULL，不私自填充默认值 |
| **字段一致性** | 数据模型必须与计划书字段完全一致，不私自增减 |

违反任何红线必须立即停止并上报。

### 6. 范围控制 (Scope Control)

- 严格按《数据监控系统 - 计划书.md》执行
- 禁止擅自扩大项目范围
- 需求超出范围时，先向老板/KIMI 确认后再执行

### 7. 文件修改权限 (File Modification Authority)

**有权修改的文件（执行阶段产出）**：
- `项目情况说明.md` - 执行阶段“当前”项目全貌
- `CLAUDE.md` - 执行阶段核心戒律
- `PROJECT_STATE.md` - 执行阶段进度跟踪
- `Git Commit 记录` - 执行阶段技术档案
- `backend/` 目录下的所有代码文件
- `frontend/` 目录下的所有代码文件
- `.gitignore` - 与 `PROJECT_STATE.md` 同步更新

**无权修改的文件（计划阶段产出）**：
- `项目/IT 项目管理流程.md` - 项目管理规范，指导性内容
- `项目/数据监控系统-需求文档.md` - 需求定义，指导性内容
- `项目/数据监控系统 - 计划书.md` - 技术规范，指导性内容

**原则**：作为执行AI，只修改和创建执行阶段的产出物，确保代码实现符合已批准的计划书和需求文档。

---

## Architecture

### Directory Structure

```
DMS/
├── 项目/                        # 项目全生命周期文档
│   ├── IT 项目管理流程.md        # 核心管理流程
│   ├── 数据监控系统-需求文档.md    # 设想阶段产出
│   └── 数据监控系统 - 计划书.md    # 规划阶段产出（v1.5）
├── backend/                    # 执行阶段产出
│   ├── app/                   # FastAPI 应用代码
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── services/          # 业务逻辑层
│   │   ├── adapters/          # 适配器抽象层
│   │   └── routers/           # API 路由模块
│   ├── requirements.txt
│   └── .env
├── frontend/                  # 待实现
├── tests/                    # 测试代码
├── 项目情况说明.md          # 执行阶段项目全貌（含技术债务）
├── PROJECT_STATE.md          # 执行阶段进度跟踪
└── CLAUDE.md                 # 执行阶段核心戒律（本文件）
```

### 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.104.1 |
| ASGI 服务器 | Uvicorn | 0.24.0 |
| ORM | SQLAlchemy | 2.0.23 |
| 数据处理 | Pandas | 2.2.3 |
| 数值计算 | NumPy | 2.2.4 |
| 数据库 | SQLite | 单文件 |

### 数据模型（4张表）

| 表名 | 用途 | 关键说明 |
|------|------|----------|
| `metrics` | 指标定义 | id, name, description, unit |
| `time_series` | 时序原始数据 | metric_id, timestamp, **value可为NULL** |
| `anomalies` | 异常快照 | 记录检测时的阈值上下文 |
| `alerts` | 报警记录 | anomaly_id, status |

### 核心设计原则

1. **time_series 仅存储原始数据**：不存储 is_anomaly 或 z_score，查询时动态计算
2. **anomalies 是快照表**：每次 `/detect` 调用时，删除该指标所有旧快照
3. **Z-Score 除零保护**：std=0 时返回 NULL
4. **缺失值返回 NULL**：不私自填充默认值

### API 端点规划

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/upload` | POST | CSV 数据导入 |
| `/data` | GET | 时序数据查询（动态计算 is_anomaly，limit=5000） |
| `/detect` | POST | 异常检测并保存快照 |
| `/anomalies` | GET | 获取历史异常快照列表 |
| `/correlation` | GET | Pearson 关联分析（有效点<3返回错误） |

---

## Commands

### Backend Development

```bash
# 进入后端目录
cd backend

# 启动开发服务器
./venv/Scripts/python -m app.main

# 健康检查
curl http://127.0.0.1:8000/health

# Git 提交（功能闭环后）
git add .
git commit -m "<详细的技术实现描述>"
```

---

## Team

- **技术负责人**：KIMI（架构方向）
- **项目经理**：DeepSeek（进度监督）
- **执行**：Claude Code

---

## Reference Documents

- `数据监控系统 - 计划书.md`（v1.5 定稿版）- 权威技术规范
- `数据监控系统-需求文档.md` - 功能需求
- `PROJECT_STATE.md` - 项目进度跟踪（动态）
- `项目情况说明.md` - 项目全貌（静态）
