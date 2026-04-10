<template>
  <div class="data-upload">
    <div class="upload-header">
      <h3>📤 数据上传</h3>
      <p class="hint">选择 CSV 文件导入时序数据</p>
    </div>

    <div class="upload-area" :class="{ 'drag-over': isDragOver }" @dragover.prevent @drop.prevent="handleDrop">
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
        @change="handleFileSelect"
        style="display: none"
      />
      <button @click="selectFile" :disabled="isUploading">
        {{ isUploading ? '上传中...' : selectedFile ? selectedFile.name : '选择 CSV 文件' }}
      </button>
      <div class="file-info" v-if="selectedFile">
        <span>{{ formatFileSize(selectedFile.size) }}</span>
        <button @click="clearFile" class="clear-btn" :disabled="isUploading">✕</button>
      </div>
    </div>

    <button
      class="upload-btn"
      @click="upload"
      :disabled="!selectedFile || isUploading"
    >
      {{ isUploading ? '上传中...' : '上传' }}
    </button>

    <div v-if="result" class="result" :class="{ 'success': result.success, 'error': !result.success }">
      <p v-if="result.success">
        ✅ 导入成功！插入 {{ result.inserted }} 条数据
      </p>
      <p v-if="!result.success">
        ❌ 导入失败：{{ result.message }}
      </p>
      <div v-if="result.metrics && result.metrics.length > 0" class="metrics-list">
        <p>导入的指标：</p>
        <ul>
          <li v-for="m in result.metrics" :key="m.id">{{ m.name }}</li>
        </ul>
      </div>
    </div>

    <div v-if="error" class="error">
      <p>❌ {{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { UploadResponse } from '@/types'
import client from '@/api/client'

const emit = defineEmits<{
  uploadSuccess: []
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const isDragOver = ref(false)
const result = ref<UploadResponse | null>(null)
const error = ref<string | null>(null)

const selectFile = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
    result.value = null
    error.value = null
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    const file = event.dataTransfer.files[0]
    if (file.name.endsWith('.csv')) {
      selectedFile.value = file
      result.value = null
      error.value = null
    } else {
      error.value = '请选择 CSV 文件'
    }
  }
}

const clearFile = () => {
  selectedFile.value = null
  result.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const upload = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  error.value = null
  result.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const res = await client.post<UploadResponse>('/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    result.value = res.data

    if (res.data.success) {
      emit('uploadSuccess')
      clearFile()
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '上传失败，请重试'
  } finally {
    isUploading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.data-upload {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.upload-header h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.upload-header .hint {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin: 1rem 0;
  transition: all 0.2s;
}

.upload-area.drag-over {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-area button {
  padding: 0.75rem 1.5rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: #333;
  transition: all 0.2s;
}

.upload-area button:hover:not(:disabled) {
  background: #e0e0e0;
}

.upload-area button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.file-info {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.clear-btn {
  padding: 0.2rem 0.5rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.clear-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.upload-btn {
  width: 100%;
  padding: 0.75rem;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
}

.upload-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.upload-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.result {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.result.success {
  background: #f0f9ff;
  color: #0c9;
  border: 1px solid #b3e0ff;
}

.result.error {
  background: #fff0f0;
  color: #f00;
  border: 1px solid #ffb3b3;
}

.metrics-list {
  margin-top: 0.5rem;
}

.metrics-list p {
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.metrics-list ul {
  margin: 0;
  padding-left: 1.5rem;
}

.metrics-list li {
  margin: 0.25rem 0;
}

.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #fff0f0;
  color: #f00;
  border: 1px solid #ffb3b3;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style>
