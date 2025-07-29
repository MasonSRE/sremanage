import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/styles/index.css'; // 更新引入路径

const app = createApp(App);
app.use(router);
app.mount('#app');