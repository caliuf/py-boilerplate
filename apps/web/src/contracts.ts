import { z } from "zod";

/**
 * Contratti client-side del caso d'uso `hello-world`.
 *
 * La fonte canonica resta il modello Pydantic in `src/py_boilerplate/contracts/`.
 * Questo modulo è il mirror TypeScript usato dal client per validare a runtime
 * le risposte esterne: i tipi non vengono mai `cast`ati. Il contract test
 * `tests/contract/test_web_contract.py` verifica che OpenAPI e questi vincoli
 * restino coerenti.
 */

export const ERROR_CODES = [
  "INTERNAL",
  "VALIDATION",
  "UNAUTHORIZED",
  "NOT_FOUND",
  "CONFLICT",
] as const;

export type ErrorCode = (typeof ERROR_CODES)[number];

export type AppError = {
  readonly code: ErrorCode;
  readonly message: string;
};

export type Result<T, E = AppError> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export const helloWorldInputSchema = z.object({
  name: z.string().trim().min(1).max(100).default("world"),
});

export type HelloWorldInput = z.infer<typeof helloWorldInputSchema>;

export const helloWorldOutputSchema = z.object({
  message: z.string().min(1),
});

export type HelloWorldOutput = z.infer<typeof helloWorldOutputSchema>;

export const httpErrorStatusSchema = z.union([
  z.literal(400),
  z.literal(401),
  z.literal(404),
  z.literal(409),
  z.literal(500),
]);

export const problemDetailsSchema = z.object({
  code: z.enum(ERROR_CODES),
  type: z.string(),
  title: z.string(),
  status: httpErrorStatusSchema,
  detail: z.string(),
});

export type ProblemDetailsDto = z.infer<typeof problemDetailsSchema>;
