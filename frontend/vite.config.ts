import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path';

// https://vite.dev/config/
export default defineConfig({
  base: "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  // build: {
  //   // outDir: resolve(__dirname, '../backend/static'),
  //   outDir: 'dist',
  //   emptyOutDir: true, 
  // },

  preview: {
    port: 5173,
    strictPort: true,
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    origin: "http://0.0.0.0:5173",
   },
  css: {
    postcss: './postcss.config.js', 
  },
})
