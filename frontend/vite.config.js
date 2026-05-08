import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/features': 'http://localhost:8000',
      '/trades':   'http://localhost:8000',
      '/health':   'http://localhost:8000',
    },
  },
})