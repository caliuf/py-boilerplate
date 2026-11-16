import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { GreetingPage } from "./GreetingPage.tsx";
import { fetchHelloWorld } from "./hello-world-api.ts";

vi.mock("./hello-world-api.ts", () => ({ fetchHelloWorld: vi.fn<typeof fetchHelloWorld>() }));

const fetchMock = vi.mocked(fetchHelloWorld);

describe("GreetingPage", () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("shows the idle state before any request", () => {
    render(<GreetingPage />);

    expect(screen.getByRole("heading", { name: "Hello world" })).toBeInTheDocument();
    expect(screen.getByText("No greeting yet")).toBeInTheDocument();
  });

  it("submits from the keyboard and renders the validated greeting", async () => {
    fetchMock.mockResolvedValue({ ok: true, value: { message: "Hello, Ada!" } });
    const user = userEvent.setup();

    render(<GreetingPage />);
    await user.type(screen.getByLabelText("Name"), "Ada{Enter}");

    expect(await screen.findByText("Hello, Ada!")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("Ada");
  });

  it("submits the default greeting from the button", async () => {
    fetchMock.mockResolvedValue({ ok: true, value: { message: "Hello, world!" } });
    const user = userEvent.setup();

    render(<GreetingPage />);
    await user.click(screen.getByRole("button", { name: "Greet" }));

    expect(await screen.findByText("Hello, world!")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(undefined);
  });

  it("renders a problem detail as an error alert", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      error: { code: "VALIDATION", message: "name is invalid" },
    });
    const user = userEvent.setup();

    render(<GreetingPage />);
    await user.click(screen.getByRole("button", { name: "Greet" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("name is invalid");
    expect(screen.getByLabelText("Name")).toHaveAttribute("aria-invalid", "true");
  });

  it("disables the form while the request is in flight", async () => {
    fetchMock.mockImplementation(() => new Promise(() => undefined));
    const user = userEvent.setup();

    render(<GreetingPage />);
    await user.click(screen.getByRole("button", { name: "Greet" }));

    expect(screen.getByRole("button", { name: /loading/i })).toBeDisabled();
    expect(screen.getByLabelText("Name")).toBeDisabled();
  });
});
