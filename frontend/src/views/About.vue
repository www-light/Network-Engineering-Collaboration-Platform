<template>
  <div class="about">
    <h1>关于项目</h1>
    <div class="info-card">
      <h2>技术栈</h2>
      <ul>
        <li><strong>后端:</strong> Django 4.2 + Django REST Framework</li>
        <li><strong>前端:</strong> Vue 3 + Vite + Vue Router + Pinia</li>
        <li><strong>HTTP客户端:</strong> Axios</li>
      </ul>
    </div>
    
    <div class="info-card">
      <h2>项目特性</h2>
      <ul>
        <li>前后端分离架构</li>
        <li>RESTful API设计</li>
        <li>CORS跨域支持</li>
        <li>现代化UI设计</li>
        <li>响应式布局</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// About组件
</script>

<style scoped>
.about {
  max-width: 800px;
  margin: 0 auto;
}

.about h1 {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
}

.info-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.info-card h2 {
  color: #667eea;
  margin-top: 0;
}

.info-card ul {
  list-style: none;
  padding: 0;
}

.info-card li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.info-card li:last-child {
  border-bottom: none;
}

.info-card strong {
  color: #333;
}
</style>

