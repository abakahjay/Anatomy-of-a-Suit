import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// relative base so the build works from any folder (Render, GitHub Pages, a subpath)
export default defineConfig({
  base: './',
  plugins: [react()],
});
