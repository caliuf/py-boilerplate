import { describe, expect, it } from "vitest";

import { parseWebEnv } from "./env.ts";

describe("parseWebEnv", () => {
  it("defaults the API base URL to same-origin", () => {
    expect(parseWebEnv({}).VITE_API_BASE_URL).toBe("");
  });

  it("accepts an absolute http(s) API base URL", () => {
    expect(parseWebEnv({ VITE_API_BASE_URL: "https://api.example.test" }).VITE_API_BASE_URL).toBe(
      "https://api.example.test",
    );
  });

  it("rejects an invalid API base URL", () => {
    expect(() => parseWebEnv({ VITE_API_BASE_URL: "api.example.test" })).toThrow(
      "VITE_API_BASE_URL",
    );
  });
});
