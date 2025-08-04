import { createApp } from 'vue'

console.log('Debug main.js starting...')

const app = createApp({
  template: `
    <div style="padding: 20px; background: #f0f0f0; margin: 20px;">
      <h1 style="color: red;">🔍 DEBUG APP WORKING</h1>
      <p>Current time: {{ time }}</p>
      <button @click="updateTime" style="padding: 10px; background: blue; color: white; border: none; border-radius: 4px;">Update Time</button>
    </div>
  `,
  data() {
    return {
      time: new Date().toLocaleString()
    }
  },
  methods: {
    updateTime() {
      this.time = new Date().toLocaleString()
    }
  },
  mounted() {
    console.log('Debug app mounted successfully!')
  }
})

console.log('About to mount app...')
app.mount('#app')
console.log('App mount attempted')