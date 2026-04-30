import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";
import VueInspector from 'vite-plugin-vue-inspector'

export default defineConfig({
  plugins: [
    vue(),
    VueInspector({
      // @ts-ignore - toggleKeyCombo is not in the type definition but is supported
      toggleKeyCombo: 'ctrl-shift',
      editor: 'code',
    }),
  ],
  resolve: {
    alias: { "@": resolve(__dirname, "src") },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8008",
    },
  },
});
