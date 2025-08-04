import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/styles/index.css'; // 更新引入路径

console.log('🚀 Main.js loading... Timestamp:', new Date().toISOString());
console.log('Vue:', { createApp });
console.log('App component:', App);
console.log('Router:', router);

const app = createApp(App);
console.log('App created:', app);

app.use(router);
console.log('Router added to app');

app.mount('#app');
console.log('App mounted to #app');