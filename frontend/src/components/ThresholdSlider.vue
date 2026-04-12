<template>
  <div class="threshold-slider">
    <div class="label">
      <span class="label-text">检测阈值</span>
      <span class="value-display">{{ threshold.toFixed(1) }}σ</span>
    </div>
    <input
      type="range"
      min="1"
      max="5"
      step="0.5"
      v-model="internalValue"
      class="slider"
      @input="handleInput"
    >
    <div class="slider-labels">
      <span class="label-low">1σ</span>
      <span class="label-mid">3σ</span>
      <span class="label-high">5σ</span>
    </div>
    <div class="hint">
      <small>阈值越小，检测越严格</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

const internalValue = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  internalValue.value = newValue
})

const handleInput = () => {
  emit('update:modelValue', Number(internalValue.value))
}
</script>

<style scoped>
.threshold-slider {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label-text {
  color: #606266;
  font-size: 0.9rem;
  font-weight: 500;
}

.value-display {
  color: #409eff;
  font-size: 1rem;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e4e7ed;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #409eff;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  background: #66b1ff;
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #409eff;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.1);
  background: #66b1ff;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 2px;
}

.slider-labels span {
  font-size: 0.75rem;
  color: #909399;
}

.hint {
  text-align: center;
  color: #c0c4cc;
  font-size: 0.8rem;
}

.hint small {
  font-size: inherit;
}
</style>
