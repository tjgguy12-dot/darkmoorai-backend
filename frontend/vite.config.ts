import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  server: {
    port: 3000,
    host: true,
    open: true,
    cors: true,
    
    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/docs': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    },
    
    // Hot Module Replacement
    hmr: {
      overlay: true,
      protocol: 'ws',
      host: 'localhost',
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    target: 'es2020',
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['framer-motion', 'react-hot-toast', 'clsx'],
          'markdown-vendor': ['react-markdown', 'react-syntax-highlighter'],
          'axios-vendor': ['axios', 'socket.io-client'],
        },
      },
    },
  },
  
  // Development optimizations
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'framer-motion',
      'react-markdown',
      'react-syntax-highlighter',
      'react-hot-toast',
      'clsx',
      'date-fns',
      'socket.io-client',
    ],
  },
  
  // CSS options
  css: {
    modules: {
      localsConvention: 'camelCaseOnly',
    },
    devSourcemap: true,
  },
  
  // Resolve aliases
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@hooks': '/src/hooks',
      '@services': '/src/services',
      '@types': '/src/types',
      '@utils': '/src/utils',
      '@assets': '/src/assets',
      '@contexts': '/src/contexts',
    },
  },
  
  // Define env variables
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
  },
  
  // Log level
  logLevel: 'info',
  clearScreen: true,
});