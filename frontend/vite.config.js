import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { visualizer } from 'rollup-plugin-visualizer'
import { sveltePreprocess } from 'svelte-preprocess/dist/autoProcess'
import { checker } from 'vite-plugin-checker'

export default defineConfig(({ mode }) => ({
  plugins: [
    svelte({
      preprocess: sveltePreprocess({
        scss: {
          prependData: `@import './src/styles/variables.scss';`
        }
      }),
      compilerOptions: {
        dev: mode === 'development'
      }
    }),
    checker({
      typescript: true,
      eslint: {
        lintCommand: 'eslint "./src/**/*.{ts,js,svelte}"'
      }
    }),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    open: true,
    historyApiFallback: true
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: mode === 'development',
    minify: mode === 'production' ? 'terser' : false,
    cssCodeSplit: true,
    rollupOptions: {
      input: {
        main: './index.html'
      },
      output: {
        entryFileNames: `assets/[name].[hash].js`,
        chunkFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor'
          }
        }
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "./src/styles/variables.scss";`
      }
    }
  },
  base: '/',
  appType: 'spa',
  optimizeDeps: {
    include: ['svelte', 'svelte-routing']
  }
}))
