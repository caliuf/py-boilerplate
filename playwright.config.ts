import { defineConfig, devices } from "@playwright/test";

const e2eApiPort = Number(process.env["E2E_API_PORT"] ?? "18100");
const e2eWebPort = Number(process.env["E2E_WEB_PORT"] ?? "15100");

/**
 * E2E configuration: few high-value flows (Vademecum §6). Traces, screenshots
 * and videos are kept ONLY on failure. Interactions prefer the keyboard.
 *
 * Dedicated ports keep the browser suite isolated from any local dev server,
 * including other checkouts of the boilerplate.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/*.spec.ts",
  timeout: 30_000,
  fullyParallel: true,
  forbidOnly: process.env["CI"] !== undefined,
  retries: process.env["CI"] !== undefined ? 1 : 0,
  reporter: process.env["CI"] !== undefined ? [["github"], ["html"]] : [["list"]],
  use: {
    baseURL: `http://localhost:${e2eWebPort}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "uv run py-boilerplate-api",
      port: e2eApiPort,
      reuseExistingServer: false,
      env: {
        LOG_LEVEL: "error",
        APP_ENV: "test",
        API_PORT: String(e2eApiPort),
      },
    },
    {
      command: "npm run web:dev",
      port: e2eWebPort,
      reuseExistingServer: false,
      env: {
        API_PORT: String(e2eApiPort),
        WEB_PORT: String(e2eWebPort),
        WEB_STRICT_PORT: "true",
      },
    },
  ],
});
