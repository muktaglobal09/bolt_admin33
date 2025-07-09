import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: './frontend', // 📁 Tell Vite your frontend root folder
  plugins: [react()],
  build: {
    outDir: '../backend/static/dist', // 📁 Output to Django's static directory
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
