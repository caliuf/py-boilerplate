import { MoonIcon, SunIcon } from "lucide-react";

import { Button } from "@/design-system/primitives/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/design-system/primitives/tooltip";
import { useTheme } from "./providers/theme-provider.tsx";

/** Keyboard-accessible light/dark switch persisted by the ThemeProvider. */
export function ThemeToggle() {
  const { resolvedTheme, toggleTheme } = useTheme();
  const isDark = resolvedTheme === "dark";
  const label = isDark ? "Switch to light theme" : "Switch to dark theme";

  return (
    <Tooltip>
      <TooltipTrigger
        render={<Button variant="ghost" size="icon" aria-label={label} />}
        onClick={toggleTheme}
      >
        {isDark ? <MoonIcon aria-hidden="true" /> : <SunIcon aria-hidden="true" />}
      </TooltipTrigger>
      <TooltipContent>{isDark ? "Light theme" : "Dark theme"}</TooltipContent>
    </Tooltip>
  );
}
