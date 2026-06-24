import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type {
  CreateWorkflowRunInput,
  WorkflowRun,
} from "../api/workflowRuns";
import WorkflowRunsPage from "../pages/WorkflowRunsPage";

let api: ReturnType<typeof makeMockApi>;

beforeEach(() => {
  api = makeMockApi();
});

afterEach(() => {
  cleanup();
});

test("loading state renders", () => {
  api.listWorkflowRuns.mockReturnValue(new Promise(() => {}));

  render(<WorkflowRunsPage api={api} />);

  expect(screen.getByText("Loading workflow runs...")).not.toBeNull();
});

test("empty state renders", async () => {
  api.listWorkflowRuns.mockResolvedValue([]);

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByText("No workflow runs yet.")).not.toBeNull();
});

test("error state renders", async () => {
  api.listWorkflowRuns.mockRejectedValue(new Error("API unavailable"));

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByText("API unavailable")).not.toBeNull();
});

test("workflow list renders", async () => {
  api.listWorkflowRuns.mockResolvedValue([makeWorkflowRun()]);

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByText("low risk invoice")).not.toBeNull();
});

test("workflow status and risk level render", async () => {
  api.listWorkflowRuns.mockResolvedValue([
    makeWorkflowRun({ risk_level: "low", status: "completed" }),
  ]);

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByText("completed")).not.toBeNull();
  expect(screen.getByText("low")).not.toBeNull();
});

test("create form renders", async () => {
  api.listWorkflowRuns.mockResolvedValue([]);

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByRole("heading", { name: "Create Workflow Run" }))
    .not.toBeNull();
  expect(screen.getByLabelText("Name")).not.toBeNull();
  expect(screen.getByLabelText("Vendor")).not.toBeNull();
  expect(screen.getByLabelText("Amount")).not.toBeNull();
  expect(screen.getByLabelText("Invoice ID")).not.toBeNull();
});

test("create form submits expected payload", async () => {
  const createdRun = makeWorkflowRun({ name: "sample invoice review" });
  const user = userEvent.setup();

  api.listWorkflowRuns.mockResolvedValueOnce([]).mockResolvedValueOnce([createdRun]);
  api.createWorkflowRun.mockResolvedValue(createdRun);

  render(<WorkflowRunsPage api={api} />);

  await screen.findByText("No workflow runs yet.");
  await user.type(screen.getByLabelText("Name"), "sample invoice review");
  await user.type(screen.getByLabelText("Vendor"), "Acme");
  await user.type(screen.getByLabelText("Amount"), "1250");
  await user.type(screen.getByLabelText("Invoice ID"), "INV-1001");
  await user.click(screen.getByRole("button", { name: "Create Run" }));

  await waitFor(() => {
    expect(api.createWorkflowRun).toHaveBeenCalledWith({
      name: "sample invoice review",
      input_payload: {
        vendor: "Acme",
        amount: 1250,
        invoice_id: "INV-1001",
      },
    });
  });

  await waitFor(() => {
    expect(api.listWorkflowRuns).toHaveBeenCalledTimes(2);
  });

  expect((screen.getByLabelText("Name") as HTMLInputElement).value).toBe("");
});

test("execute button renders only for created workflows", async () => {
  api.listWorkflowRuns.mockResolvedValue([
    makeWorkflowRun({ id: 1, name: "created invoice", status: "created" }),
    makeWorkflowRun({ id: 2, name: "completed invoice", status: "completed" }),
  ]);

  render(<WorkflowRunsPage api={api} />);

  expect(await screen.findByRole("button", { name: "Execute created invoice" }))
    .not.toBeNull();
  expect(screen.queryByRole("button", { name: "Execute completed invoice" }))
    .toBeNull();
});

test("execute button calls API client", async () => {
  const user = userEvent.setup();
  const createdRun = makeWorkflowRun({ id: 7, name: "created invoice" });

  api.listWorkflowRuns
    .mockResolvedValueOnce([createdRun])
    .mockResolvedValueOnce([
      makeWorkflowRun({
        id: 7,
        name: "created invoice",
        risk_level: "low",
        status: "completed",
      }),
    ]);
  api.executeWorkflowRun.mockResolvedValue(
    makeWorkflowRun({ id: 7, name: "created invoice", status: "completed" }),
  );

  render(<WorkflowRunsPage api={api} />);

  await user.click(
    await screen.findByRole("button", { name: "Execute created invoice" }),
  );

  await waitFor(() => {
    expect(api.executeWorkflowRun).toHaveBeenCalledWith(7);
  });
  await waitFor(() => {
    expect(api.listWorkflowRuns).toHaveBeenCalledTimes(2);
  });
});

function makeWorkflowRun(overrides: Partial<WorkflowRun> = {}): WorkflowRun {
  return {
    id: 1,
    name: "low risk invoice",
    status: "created",
    risk_level: "unknown",
    input_payload: {
      amount: 500,
      invoice_id: "INV-LOW-1",
      vendor: "Acme",
    },
    output_payload: null,
    created_at: "2026-06-24T12:00:00Z",
    updated_at: "2026-06-24T12:00:00Z",
    completed_at: null,
    ...overrides,
  };
}

function makeMockApi() {
  return {
    createWorkflowRun:
      vi.fn<(workflowRun: CreateWorkflowRunInput) => Promise<WorkflowRun>>(),
    executeWorkflowRun: vi.fn<(workflowRunId: number) => Promise<WorkflowRun>>(),
    listWorkflowRuns: vi.fn<() => Promise<WorkflowRun[]>>(),
  };
}
