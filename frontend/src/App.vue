<template>
  <div class="app">
    <header class="app-header">
      <h1>📊 DMS 数据监控系统</h1>
    </header>
    <main>
      <Dashboard />
    </main>
  </div>
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

.app {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: #1a1a2e;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 1.5rem;
  margin: 0;
}

main {
  padding: 1rem;
}
</style>
