import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, test } from "@playwright/test";

/**
 * The critical user journey of the boilerplate: the web UI shows the
 * hello-world greeting through the real API. Keyboard-first (Vademecum §6).
 */
async function expectNoAccessibilityViolations(page: Page) {
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
}

test("the greeting flow works from the keyboard", async ({ page }) => {
  await page.goto("/");

  const input = page.getByLabel("Name");
  await input.fill("Ada");
  await input.press("Enter");

  await expect(page.getByText("Hello, Ada!")).toBeVisible();
  await expectNoAccessibilityViolations(page);
});

test("the button path shows the default greeting", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Greet" }).click();

  await expect(page.getByText("Hello, world!")).toBeVisible();
  await expectNoAccessibilityViolations(page);
});

test("the home page has no automated accessibility violations", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Hello world" })).toBeVisible();
  await expectNoAccessibilityViolations(page);
});

test("the theme toggle switches to dark and persists across reloads", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: /switch to dark theme/i }).click();
  await expect(page.locator("html")).toHaveClass(/dark/);

  await page.reload();
  await expect(page.locator("html")).toHaveClass(/dark/);
  await expectNoAccessibilityViolations(page);
});

test("the layout works at a narrow viewport without horizontal scrolling", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await page.goto("/");

  await expect(page.getByLabel("Name")).toBeVisible();
  await page.getByRole("button", { name: "Greet" }).click();
  await expect(page.getByText("Hello, world!")).toBeVisible();

  const overflows = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(overflows).toBe(false);
});
