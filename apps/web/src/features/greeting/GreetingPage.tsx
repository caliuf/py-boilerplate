import { CircleCheckIcon, Loader2Icon, MessageSquareIcon, TriangleAlertIcon } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Page } from "@/design-system/patterns/page";
import { Alert, AlertDescription, AlertTitle } from "@/design-system/primitives/alert";
import { Button } from "@/design-system/primitives/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/design-system/primitives/card";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/design-system/primitives/empty";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/design-system/primitives/field";
import { Input } from "@/design-system/primitives/input";
import { useHelloWorld } from "./use-hello-world.ts";

/**
 * Greeting feature screen. It composes the design system only and stays
 * keyboard-first: the form submits natively on Enter and the button is a real
 * submit control.
 */
export function GreetingPage() {
  const [name, setName] = useState("");
  const { state, run } = useHelloWorld();
  const isLoading = state.status === "loading";

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void run(name === "" ? undefined : name);
  };

  return (
    <Page
      title="Hello world"
      description="One use case, four surfaces. Ask the API for a greeting through the same contract used by the CLI, HTTP API and MCP server."
    >
      <Card>
        <CardHeader>
          <CardTitle>Say hello</CardTitle>
          <CardDescription>Leave the name empty to greet the world.</CardDescription>
        </CardHeader>
        <form onSubmit={submit}>
          <CardContent>
            <FieldGroup>
              <Field data-invalid={state.status === "error" ? "true" : undefined}>
                <FieldLabel htmlFor="name">Name</FieldLabel>
                <Input
                  id="name"
                  name="name"
                  autoComplete="off"
                  placeholder="world"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  aria-describedby="name-description"
                  aria-invalid={state.status === "error"}
                  disabled={isLoading}
                />
                <FieldDescription id="name-description">
                  Press Enter or use the button. The API validates the name.
                </FieldDescription>
              </Field>
            </FieldGroup>
          </CardContent>
          <CardFooter>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2Icon
                    aria-hidden="true"
                    className="animate-spin"
                    data-icon="inline-start"
                  />
                  Loading…
                </>
              ) : (
                "Greet"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>

      <section aria-label="Greeting result" className="min-h-24">
        {state.status === "idle" && (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <MessageSquareIcon aria-hidden="true" />
              </EmptyMedia>
              <EmptyTitle>No greeting yet</EmptyTitle>
              <EmptyDescription>
                Submit the form to call the API and show its validated response here.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        )}

        {state.status === "success" && (
          // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role -- Alert owns its composite markup; the status role keeps success announcements polite.
          <Alert role="status">
            <CircleCheckIcon aria-hidden="true" />
            <AlertTitle>Greeting</AlertTitle>
            <AlertDescription>{state.data.message}</AlertDescription>
          </Alert>
        )}

        {state.status === "error" && (
          <Alert variant="destructive" role="alert">
            <TriangleAlertIcon aria-hidden="true" />
            <AlertTitle>Request failed</AlertTitle>
            <AlertDescription>{state.error.message}</AlertDescription>
          </Alert>
        )}
      </section>
    </Page>
  );
}
