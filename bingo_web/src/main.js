import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue';
import 'xterm/css/xterm.css'
import 'xterm/lib/xterm'

createApp(App).use(router).use(Antd).mount('#app01')
