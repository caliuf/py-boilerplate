import { useCallback, useEffect, useRef, useState } from "react";

import type { AppError, HelloWorldOutput } from "../../contracts.ts";
import { fetchHelloWorld } from "./hello-world-api.ts";

export type HelloWorldState =
  | { readonly status: "idle" }
  | { readonly status: "loading" }
  | { readonly status: "success"; readonly data: HelloWorldOutput }
  | { readonly status: "error"; readonly error: AppError };

/**
 * Server state for the greeting feature, kept separate from UI state
 * (Vademecum §3, UI web). The naming mirrors the use case on every surface:
 * `hello-world` (CLI/API), `hello_world` (MCP), `useHelloWorld` (UI).
 *
 * A request sequence guard prevents a slower, older response from overwriting
 * the result of a newer one.
 */
export function useHelloWorld() {
  const [state, setState] = useState<HelloWorldState>({ status: "idle" });
  const requestId = useRef(0);

  const run = useCallback(async (name?: string) => {
    requestId.current += 1;
    const currentRequest = requestId.current;
    setState({ status: "loading" });

    const result = await fetchHelloWorld(name);
    if (currentRequest !== requestId.current) {
      return;
    }

    setState(
      result.ok
        ? { status: "success", data: result.value }
        : { status: "error", error: result.error },
    );
  }, []);

  useEffect(() => {
    return () => {
      requestId.current += 1;
    };
  }, []);

  return { state, run } as const;
}
