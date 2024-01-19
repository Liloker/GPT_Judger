// import { ElementPlusResolver } from 'unplugin-vue-components/resolvers' //cjs文件不支持直接导入的方法
// import pkg from 'unplugin-vue-components/resolvers';
// const { ElementPlusResolver } = pkg;
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // AutoImport({
    //   resolvers: [ElementPlusResolver()],
    // }),
    // Components({
    //   resolvers: [ElementPlusResolver()],
    // }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
