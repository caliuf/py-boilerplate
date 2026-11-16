import { z } from "zod";

const webEnvSchema = z.object({
  VITE_API_BASE_URL: z
    .string()
    .trim()
    .refine(
      (value) => value === "" || /^https?:\/\//u.test(value),
      "VITE_API_BASE_URL must be empty for same-origin requests or an absolute http(s) URL",
    )
    .default(""),
});

export type WebEnv = z.infer<typeof webEnvSchema>;

/** Validates build-time configuration at startup instead of trusting strings. */
export function parseWebEnv(source: Record<string, unknown>): WebEnv {
  return webEnvSchema.parse(source);
}

export const env = parseWebEnv(import.meta.env);
