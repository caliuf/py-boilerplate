import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { HelloWorldOutput, Result } from "../../contracts.ts";
import { fetchHelloWorld } from "./hello-world-api.ts";
import { useHelloWorld } from "./use-hello-world.ts";

vi.mock("./hello-world-api.ts", () => ({ fetchHelloWorld: vi.fn<typeof fetchHelloWorld>() }));

const fetchMock = vi.mocked(fetchHelloWorld);

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((next) => {
    resolve = next;
  });
  return { promise, resolve };
}

describe("useHelloWorld", () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("keeps the newest response when an older request resolves later", async () => {
    const older = deferred<Result<HelloWorldOutput>>();
    const newer = deferred<Result<HelloWorldOutput>>();
    fetchMock.mockReturnValueOnce(older.promise).mockReturnValueOnce(newer.promise);

    const { result } = renderHook(() => useHelloWorld());

    act(() => {
      void result.current.run("older");
      void result.current.run("newer");
    });
    expect(result.current.state).toEqual({ status: "loading" });

    await act(async () => {
      newer.resolve({ ok: true, value: { message: "newer" } });
      await newer.promise;
    });
    await act(async () => {
      older.resolve({ ok: true, value: { message: "older" } });
      await older.promise;
    });

    expect(result.current.state).toEqual({
      status: "success",
      data: { message: "newer" },
    });
  });
});
