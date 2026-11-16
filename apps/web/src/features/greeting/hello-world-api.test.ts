import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchHelloWorld } from "./hello-world-api.ts";

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    status: 200,
    ...init,
  });
}

describe("fetchHelloWorld", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls the same-origin API and validates the output", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValue(jsonResponse({ message: "Hello, Ada!" }));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchHelloWorld("Ada Ada");

    expect(fetchMock).toHaveBeenCalledWith("/api/hello-world?name=Ada%20Ada");
    expect(result).toEqual({ ok: true, value: { message: "Hello, Ada!" } });
  });

  it("maps a Problem Details response to the shared error code", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      jsonResponse(
        {
          code: "VALIDATION",
          type: "urn:py-boilerplate:error:validation",
          title: "Validation failed",
          status: 400,
          detail: "name is invalid",
        },
        { status: 400 },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchHelloWorld("");

    expect(result).toEqual({
      ok: false,
      error: { code: "VALIDATION", message: "name is invalid" },
    });
  });

  it("reports a network error and an unexpected response shape", async () => {
    const networkError = vi.fn<typeof fetch>().mockRejectedValue(new Error("offline"));
    vi.stubGlobal("fetch", networkError);
    expect(await fetchHelloWorld()).toEqual({
      ok: false,
      error: { code: "INTERNAL", message: "network error" },
    });

    const unexpected = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({ message: "" }));
    vi.stubGlobal("fetch", unexpected);
    expect(await fetchHelloWorld()).toEqual({
      ok: false,
      error: { code: "INTERNAL", message: "unexpected response shape" },
    });
  });
});
