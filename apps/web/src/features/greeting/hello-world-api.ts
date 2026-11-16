import { env } from "@/config/env";
import type { HelloWorldOutput, Result } from "../../contracts.ts";
import { helloWorldOutputSchema, problemDetailsSchema } from "../../contracts.ts";

const API_BASE_URL = env.VITE_API_BASE_URL.replace(/\/$/u, "");

/**
 * Typed API client for the greeting feature. Responses are validated against
 * the shared schemas: external data is never trusted (Vademecum §3,
 * "Contratti e dati esterni").
 */
export async function fetchHelloWorld(name?: string): Promise<Result<HelloWorldOutput>> {
  const query = name === undefined || name === "" ? "" : `?name=${encodeURIComponent(name)}`;
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/hello-world${query}`);
  } catch {
    return { ok: false, error: { code: "INTERNAL", message: "network error" } };
  }

  const raw: unknown = await response.json();
  if (!response.ok) {
    const problem = problemDetailsSchema.safeParse(raw);
    return {
      ok: false,
      error: {
        code: problem.success ? problem.data.code : "INTERNAL",
        message: problem.success ? problem.data.detail : "request failed",
      },
    };
  }

  const parsed = helloWorldOutputSchema.safeParse(raw);
  if (!parsed.success) {
    return { ok: false, error: { code: "INTERNAL", message: "unexpected response shape" } };
  }
  return { ok: true, value: parsed.data };
}
