// 数据点类型
export interface DataPoint {
  timestamp: string
  value: number | null
  is_anomaly: boolean
  z_score: number
}

// 指标类型
export interface Metric {
  id: number
  name: string
  description?: string
  unit?: string
}

// API响应类型
export interface DataResponse {
  data: DataPoint[]
  mean: number
  std: number
  limit: number
  offset: number
  total: number
}

// 指标列表响应类型
export interface MetricsListResponse {
  metrics: Metric[]
  total: number
}

// CSV上传响应类型
export interface UploadResponse {
  success: boolean
  inserted: number
  metrics: Metric[]
}

// 异常点类型
export interface AnomalyPoint {
  timestamp: string
  value: number
  z_score: number
}

// 异常检测响应类型
export interface DetectResponse {
  anomalies: AnomalyPoint[]
  count: number
  mean: number
  std: number
  threshold_used: number
}
