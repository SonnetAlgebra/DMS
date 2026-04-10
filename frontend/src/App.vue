<template>
  <header class="app-header">
    <h1>📊 DMS 数据监控系统</h1>
  </header>
  <main>
    <Dashboard />
  </main>
</template>

<script setup lang="ts">
import Dashboard from './components/Dashboard.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-header {
  background: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
}

main {
  padding: 1rem;
}
</style>
