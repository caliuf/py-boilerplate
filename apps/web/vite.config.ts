import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiPort = process.env["API_PORT"] ?? "8100";
const webPort = Number(process.env["WEB_PORT"] ?? "5100");

export default defineConfig({
  plugins: [react()],
  server: {
    port: webPort,
    strictPort: true,
    proxy: {
      "/api": `http://localhost:${apiPort}`,
    },
  },
});
