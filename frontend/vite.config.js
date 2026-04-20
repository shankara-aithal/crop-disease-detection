import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // All /api calls forwarded to Flask backend
      '/api': {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        secure: false
      }
    }
  }
})
