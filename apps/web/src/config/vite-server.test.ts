import { afterEach, describe, expect, it, vi } from "vitest";

async function loadViteConfig() {
  vi.resetModules();
  const module = await import("../../vite.config.ts");
  return module.default;
}

describe("vite server port", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("searches for a free port when WEB_PORT is occupied", async () => {
    vi.stubEnv("WEB_PORT", "5100");
    vi.stubEnv("WEB_STRICT_PORT", "");

    await expect(loadViteConfig()).resolves.toMatchObject({
      server: { port: 5100, strictPort: false },
    });
  });

  it("stays strict when WEB_STRICT_PORT is true", async () => {
    vi.stubEnv("WEB_PORT", "15100");
    vi.stubEnv("WEB_STRICT_PORT", "true");

    await expect(loadViteConfig()).resolves.toMatchObject({
      server: { port: 15100, strictPort: true },
    });
  });
});
