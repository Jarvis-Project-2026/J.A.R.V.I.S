import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
  resolve: {
    alias: {
      // Cria o alias apontando para a pasta src de forma absoluta
      '@': new URL('./src', import.meta.url).pathname,
    },
  },
})