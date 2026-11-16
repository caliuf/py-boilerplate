import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { ThemeProvider, useTheme } from "./theme-provider.tsx";

const wrapper = ({ children }: { readonly children: ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe("ThemeProvider", () => {
  it("defaults to light when the system does not prefer dark", () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe("system");
    expect(result.current.resolvedTheme).toBe("light");
    expect(document.documentElement).toHaveClass("light");
  });

  it("toggles the dark theme and persists the choice", () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe("dark");
    expect(result.current.resolvedTheme).toBe("dark");
    expect(document.documentElement).toHaveClass("dark");
    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(window.localStorage.getItem("py-boilerplate-theme")).toBe("dark");
  });

  it("restores a stored theme on mount", () => {
    window.localStorage.setItem("py-boilerplate-theme", "dark");

    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe("dark");
    expect(result.current.resolvedTheme).toBe("dark");
    expect(document.documentElement).toHaveClass("dark");
  });
});
