import { SparklesIcon } from "lucide-react";

import { Toaster } from "@/design-system/primitives/sonner";
import { TooltipProvider } from "@/design-system/primitives/tooltip";
import { GreetingPage } from "@/features/greeting/GreetingPage";
import { useTheme } from "./providers/theme-provider.tsx";
import { ThemeToggle } from "./theme-toggle.tsx";

/** Application shell: landmarks, skip link, theme switch and toast surface. */
export function App() {
  const { resolvedTheme } = useTheme();

  return (
    <TooltipProvider>
      <div className="flex min-h-dvh flex-col">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:inset-inline-start-4 focus:top-3 focus:z-50 focus:rounded-md focus:bg-background focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:shadow-md focus:ring-3 focus:ring-ring/50"
        >
          Skip to content
        </a>

        <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
          <div className="mx-auto flex w-full max-w-4xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <div className="flex min-w-0 items-center gap-2">
              <SparklesIcon aria-hidden="true" className="size-4 text-primary" />
              <span className="font-heading truncate text-sm font-semibold">py-boilerplate</span>
            </div>
            <ThemeToggle />
          </div>
        </header>

        <GreetingPage />

        <footer className="mt-auto border-t">
          <div className="mx-auto flex w-full max-w-4xl flex-col gap-1 px-4 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
            <p>React, Vite, Tailwind CSS, shadcn/ui and Base UI.</p>
            <p>One use case, four surfaces.</p>
          </div>
        </footer>

        <Toaster theme={resolvedTheme} />
      </div>
    </TooltipProvider>
  );
}
