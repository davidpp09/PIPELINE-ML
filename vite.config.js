import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
  // Permite que Railway (dominio *.up.railway.app) sirva el preview sin bloquearlo.
  preview: {
    allowedHosts: true,
  },
})
