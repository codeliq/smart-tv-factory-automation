<template>
  <div id="app">
    <nav class="navbar">
      <div class="logo">
        <span class="icon">🤖</span>
        <span class="text">DoboLive</span>
      </div>
      <ul class="nav-links">
        <li><router-link to="/">🏠 홈</router-link></li>
        <li><router-link to="/">📊 대시보드</router-link></li>
        <li><router-link to="/settings">⚙️ 설정</router-link></li>
      </ul>
    </nav>

    <!-- ✅ 올바른 router-view + transition -->
    <router-view v-slot="{ Component }">
      <transition name="fade">
        <component :is="Component" />
      </transition>
    </router-view>

    <footer class="footer">
      <p>© 2025 Robot Monitoring System</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style scoped>
@font-face {
  font-family: 'Paperlogy-8ExtraBold';
  src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/2408-3@1.0/Paperlogy-8ExtraBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
}
@font-face {
    font-family: 'GongGothicMedium';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-10@1.0/GongGothicMedium.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}
@font-face {
    font-family: 'GmarketSansMedium';
    src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff');
    font-weight: normal;
    font-style: normal;
}
#app {
  font-family: "GmarketSansMedium", sans-serif;
  color: #1e293b;
  background-color: #f0f9ff;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  font-family: 'GongGothicMedium', sans-serif;
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.6rem;
  font-weight: bold;
}

.logo .icon {
  font-size: 1.8rem;
  margin-right: 0.5rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 1.5rem;
}

.nav-links li a {
  color: #e0f2fe;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
  font-size: 1.05rem;
}

.nav-links li a:hover {
  color: #ffffff;
}

.footer {
  text-align: center;
  padding: 1rem;
  background-color: #dbeafe;
  color: #1e3a8a;
  font-size: 0.85rem;
  border-top: 2px solid #60a5fa;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
