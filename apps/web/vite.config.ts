/// <reference types="vitest/config" />
import { resolve } from "node:path";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const apiHost = process.env["API_HOST"] ?? "127.0.0.1";
const apiPort = process.env["API_PORT"] ?? "8100";
const webPort = Number(process.env["WEB_PORT"] ?? "5100");

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": resolve(import.meta.dirname, "./src"),
    },
  },
  server: {
    port: webPort,
    strictPort: true,
    proxy: {
      "/api": `http://${apiHost}:${apiPort}`,
    },
  },
  test: {
    projects: [
      {
        extends: true,
        test: {
          name: "unit",
          environment: "node",
          include: ["src/**/*.test.ts"],
        },
      },
      {
        extends: true,
        test: {
          name: "dom",
          environment: "jsdom",
          include: ["src/**/*.test.tsx"],
          setupFiles: ["./src/test/setup.ts"],
          css: false,
        },
      },
    ],
  },
});
