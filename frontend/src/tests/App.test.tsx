import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "../App";

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

test("workflow runs page placeholder renders", () => {
  renderApp("/workflow-runs");

  expect(
    screen.getByRole("heading", { name: "Workflow Runs" }),
  ).not.toBeNull();
  expect(screen.getByText("No workflow runs loaded yet.")).not.toBeNull();
});

test("user can navigate to workflow runs", async () => {
  const user = userEvent.setup();
  renderApp();

  await user.click(screen.getByRole("link", { name: "Workflow Runs" }));

  expect(
    screen.getByRole("heading", { name: "Workflow Runs" }),
  ).not.toBeNull();
});
