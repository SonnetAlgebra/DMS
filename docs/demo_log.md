# DMS 功能演示日志

> 演示日期：2026-04-14
> 演示环境：Windows 11

---

## 一、环境检查

### 1. 后端健康检查

```bash
curl http://127.0.0.1:8000/health
```

**响应**：
```json
{"status":"ok"}
```

### 2. API 文档访问
- 地址：http://127.0.0.1:8000/docs
- 状态：✅ 可访问

---

## 二、数据上传

### 1. 上传示例数据

```bash
curl -X POST http://127.0.0.1:8000/api/v1/data/upload \
  -F "file=@data/sample_metrics.csv"
```

**响应**：
```json
{
  "success": true,
  "inserted": 73,
  "metrics": [{"id": 18, "name": "metric_id"}]
}
```

### 2. 示例数据内容

| metric_id | metric_name | timestamp | value |
|-----------|-------------|-----------|-------|
| cpu_usage | CPU 使用率 | 2024-01-01T00:00:00 | 45.2 |
| cpu_usage | CPU 使用率 | 2024-01-01T03:00:00 | **500.0** ← 异常值 |
| cpu_usage | CPU 使用率 | 2024-01-01T05:00:00 | ← 空值 |
| memory_usage | 内存使用率 | 2024-01-01T09:00:00 | **650.0** ← 异常值 |
| network_io | 网络 I/O | 2024-01-01T12:00:00 | **450.0** ← 异常值 |

---

## 三、指标查询

### 1. 获取指标列表

```bash
curl http://127.0.0.1:8000/api/v1/metrics
```

**响应**（部分）：
```json
{
  "metrics": [
    {"id": 10, "name": "test_anomaly", "description": "异常检测测试指标", "unit": "units"},
    {"id": 13, "name": "CPU", "description": "指标: CPU", "unit": null},
    {"id": 14, "name": "Memory", "description": "指标: Memory", "unit": null}
  ],
  "total": 14
}
```

---

## 四、异常检测

### 1. 执行检测

```bash
curl -X POST http://127.0.0.1:8000/api/v1/metrics/detect \
  -H "Content-Type: application/json" \
  -d '{"metric_id": 10, "threshold": 3.0}'
```

**响应**：
```json
{
  "anomalies": [
    {
      "timestamp": "2026-04-11T01:08:51.928357",
      "value": 500.0,
      "z_score": 4.448666838805543
    }
  ],
  "count": 1,
  "mean": 126.36363636363636,
  "std": 83.9883895950914,
  "threshold_used": 3.0
}
```

**结果分析**：
- 检测到 1 个异常点
- 异常值：500.0
- Z-Score：4.45（超过阈值 3.0）
- 均值：126.36，标准差：83.99

---

## 五、关联分析

### 1. 相关性计算

```bash
curl -X POST http://127.0.0.1:8000/api/v1/correlation \
  -H "Content-Type: application/json" \
  -d '{"metric_ids": [10, 13, 14], "resample": "D"}'
```

**响应**：
```json
{
  "detail": {
    "code": "INSUFFICIENT_DATA",
    "message": "有效数据点不足3对（实际：0对）"
  }
}
```

---

## 六、功能验证总结

| 功能 | 状态 | 说明 |
|------|------|------|
| 健康检查 | ✅ | /health 接口正常 |
| 数据上传 | ✅ | CSV 解析成功，插入 73 条记录 |
| 指标查询 | ✅ | 返回指标列表 |
| 异常检测 | ✅ | Z-Score 算法正常，检测到异常点 |
| 关联分析 | ⚠️ | 需要公共时间点的数据 |

---

## 七、演示视频说明

由于命令行环境限制，无法生成 GUI 截图。实际使用时的演示流程：

1. 启动前后端服务
2. 打开浏览器访问 http://localhost:5173
3. 点击「数据上传」选择 `sample_metrics.csv`
4. 选择指标查看时序图（含断点处理）
5. 点击「检测异常」查看红色异常标记
6. 在异常面板查看异常详情
7. 调整阈值滑块重新检测
8. 切换到关联分析查看热力图

---

## 八、一键启动脚本验证

### Windows (start.bat)
- 后端：新窗口启动 `uvicorn app.main:app`
- 前端：新窗口启动 `bun run dev`
- 状态：✅ 脚本已创建

---

## 九、部署文档

- README.md：✅ 已创建
- 包含环境要求、安装步骤、启动命令、访问地址

---

## 十、交付物检查

- [x] README.md 部署文档
- [x] sample_metrics.csv 示例数据
- [x] start.bat 一键启动脚本（Windows）
- [x] 功能演示日志

---

**总体状态**：✅ Day7 任务完成
