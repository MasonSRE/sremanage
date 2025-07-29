<template>
  <div class="header">
    <div class="logo-container">
      <img src="@/assets/logo.png" alt="Logo" class="logo" />
      <!-- 如果没有logo图片，可以使用文字logo -->
      <span class="logo-text">AI Chat</span>
    </div>
    <router-link :to="{ name: 'dashboard' }" class="nav-item">控制台</router-link>
  </div>
</template>

<style scoped>
.header {
  padding: 1rem 2rem;
  background-color: #fff;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  margin-right: 2rem;
}

.logo {
  height: 32px;
  margin-right: 0.5rem;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(45deg, #409EFF, #2c3e50);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.nav-item {
  cursor: pointer;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.nav-item:hover {
  background-color: #f5f7fa;
}
</style>