import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const servedDistDir = resolve(__dirname, '../national_oil/public/frontend/dist')

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/method': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'esnext',
    outDir: servedDistDir,
    emptyOutDir: true,
    sourcemap: false,
  },
})
