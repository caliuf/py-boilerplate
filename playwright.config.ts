import { defineConfig, devices } from "@playwright/test";

/**
 * E2E configuration: few high-value flows (Vademecum §6). Traces, screenshots
 * and videos are kept ONLY on failure. Interactions prefer the keyboard.
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
    baseURL: "http://localhost:5100",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "uv run py-boilerplate-api",
      port: 8100,
      reuseExistingServer: process.env["CI"] === undefined,
      env: { LOG_LEVEL: "error", APP_ENV: "test" },
    },
    {
      command: "npm run web:dev",
      port: 5100,
      reuseExistingServer: process.env["CI"] === undefined,
      env: { API_PORT: "8100" },
    },
  ],
});
