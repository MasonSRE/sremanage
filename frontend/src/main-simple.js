// 最简单的Vue应用测试
import { createApp } from 'vue';

console.log('Simple main.js started');

try {
  const app = createApp({
    template: '<h1 style="color: red; background: yellow; padding: 20px;">✅ SIMPLE VUE WORKING!</h1>',
    mounted() {
      console.log('Simple Vue app mounted successfully!');
    }
  });
  
  console.log('About to mount simple app...');
  app.mount('#app');
  console.log('Simple app mounted');
} catch (error) {
  console.error('Error in simple main:', error);
  document.getElementById('app').innerHTML = '<h1 style="color: red;">ERROR: ' + error.message + '</h1>';
}