import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "../App";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async (url: string) => ({
      json: async () => {
        if (url.endsWith("/api/workflow-runs/42")) {
          return makeWorkflowRunDetail();
        }

        return [];
      },
      ok: true,
    })),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderApp(initialPath = "/") {
  window.history.pushState({}, "", initialPath);

  return render(<App />);
}

test("app renders", () => {
  renderApp();

  expect(screen.getByText("Workflow Verification")).not.toBeNull();
});

test("navigation renders", () => {
  renderApp();

  expect(screen.getByRole("navigation")).not.toBeNull();
  expect(screen.getByRole("link", { name: "Home" })).not.toBeNull();
  expect(screen.getByRole("link", { name: "Workflow Runs" })).not.toBeNull();
});

test("home page renders", () => {
  renderApp();

  expect(
    screen.getByRole("heading", { name: "Frontend Shell" }),
  ).not.toBeNull();
});

test("workflow runs page placeholder renders", async () => {
  renderApp("/workflow-runs");

  expect(
    screen.getByRole("heading", { name: "Workflow Runs" }),
  ).not.toBeNull();
  expect(await screen.findByText("No workflow runs yet.")).not.toBeNull();
});

test("user can navigate to workflow runs", async () => {
  const user = userEvent.setup();
  renderApp();

  await user.click(screen.getByRole("link", { name: "Workflow Runs" }));

  expect(
    screen.getByRole("heading", { name: "Workflow Runs" }),
  ).not.toBeNull();
  expect(await screen.findByText("No workflow runs yet.")).not.toBeNull();
});

test("app routes workflow run detail pages", async () => {
  renderApp("/workflow-runs/42");

  expect(
    await screen.findByRole("heading", { name: "detail invoice" }),
  ).not.toBeNull();
  expect(screen.getByText("Agent Step Timeline")).not.toBeNull();
});

function makeWorkflowRunDetail() {
  return {
    id: 42,
    name: "detail invoice",
    status: "completed",
    risk_level: "low",
    input_payload: {
      amount: 500,
      invoice_id: "INV-DETAIL-1",
      vendor: "Acme",
    },
    output_payload: {
      decision: "approve",
    },
    created_at: "2026-06-24T12:00:00Z",
    updated_at: "2026-06-24T12:01:00Z",
    completed_at: "2026-06-24T12:02:00Z",
    agent_steps: [],
    validation_results: [],
    approval_decisions: [],
  };
}
