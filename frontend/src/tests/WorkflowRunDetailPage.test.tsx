import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import type {
  ApprovalDecisionInput,
  WorkflowRun,
  WorkflowRunDetail,
} from "../api/workflowRuns";
import WorkflowRunDetailPage from "../pages/WorkflowRunDetailPage";

let api: ReturnType<typeof makeMockApi>;

beforeEach(() => {
  api = makeMockApi();
});

afterEach(() => {
  cleanup();
});

test("detail page renders loading state", () => {
  api.getWorkflowRun.mockReturnValue(new Promise(() => {}));

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(screen.getByText("Loading workflow detail...")).not.toBeNull();
});

test("detail page renders error state", async () => {
  api.getWorkflowRun.mockRejectedValue(new Error("Workflow not found"));

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText("Workflow not found")).not.toBeNull();
});

test("detail page renders workflow summary", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByRole("heading", { name: "low risk invoice" }))
    .not.toBeNull();
  expect(screen.getAllByText("completed").length).toBeGreaterThan(0);
  expect(screen.getByText("low")).not.toBeNull();
});

test("detail page renders trace id when provided", async () => {
  api.getWorkflowRun.mockResolvedValue(
    makeWorkflowRunDetail({ trace_id: "trace-phase-13" }),
  );

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText("Trace ID")).not.toBeNull();
  expect(screen.getByText("trace-phase-13")).not.toBeNull();
});

test("detail page renders formatted input payload", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  await screen.findByRole("heading", { name: "Input Payload" });
  const inputPanel = screen
    .getByRole("heading", { name: "Input Payload" })
    .closest("section");

  expect(inputPanel?.textContent).toContain('"vendor": "Acme"');
  expect(inputPanel?.textContent).toContain('"invoice_id": "INV-LOW-1"');
});

test("detail page renders formatted output payload", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText(textIncludes('"decision": "approve"')))
    .not.toBeNull();
});

test("detail page renders agent steps", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText("inspect_input")).not.toBeNull();
  expect(screen.getByText("Step 1")).not.toBeNull();
});

test("detail page renders validation results", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText("required_vendor_present")).not.toBeNull();
  expect(screen.getByText("Vendor is present.")).not.toBeNull();
});

test("detail page renders approval history", async () => {
  api.getWorkflowRun.mockResolvedValue(
    makeWorkflowRunDetail({
      approval_decisions: [
        {
          id: 1,
          decision: "approved",
          reviewer_name: "local reviewer",
          comment: "Approved after review.",
          created_at: "2026-06-24T12:05:00Z",
        },
      ],
    }),
  );

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByText("approved")).not.toBeNull();
  expect(screen.getByText("local reviewer")).not.toBeNull();
  expect(screen.getByText("Approved after review.")).not.toBeNull();
});

test("approval buttons render only when status is approval_required", async () => {
  api.getWorkflowRun.mockResolvedValue(
    makeWorkflowRunDetail({ risk_level: "high", status: "approval_required" }),
  );

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  expect(await screen.findByRole("button", { name: "Approve" })).not.toBeNull();
  expect(screen.getByRole("button", { name: "Reject" })).not.toBeNull();
});

test("approval buttons do not render for completed workflow", async () => {
  api.getWorkflowRun.mockResolvedValue(makeWorkflowRunDetail());

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  await screen.findByRole("heading", { name: "low risk invoice" });
  expect(screen.queryByRole("button", { name: "Approve" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Reject" })).toBeNull();
});

test("approve action calls API client and refreshes detail", async () => {
  const user = userEvent.setup();

  api.getWorkflowRun
    .mockResolvedValueOnce(
      makeWorkflowRunDetail({ risk_level: "high", status: "approval_required" }),
    )
    .mockResolvedValueOnce(
      makeWorkflowRunDetail({ risk_level: "high", status: "approved" }),
    );
  api.approveWorkflowRun.mockResolvedValue(
    makeWorkflowRunSummary({ risk_level: "high", status: "approved" }),
  );

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  await user.type(await screen.findByLabelText("Reviewer Name"), "Sam Reviewer");
  await user.type(screen.getByLabelText("Comment"), "Approved.");
  await user.click(screen.getByRole("button", { name: "Approve" }));

  await waitFor(() => {
    expect(api.approveWorkflowRun).toHaveBeenCalledWith(1, {
      reviewer_name: "Sam Reviewer",
      comment: "Approved.",
    });
  });
  await waitFor(() => {
    expect(api.getWorkflowRun).toHaveBeenCalledTimes(2);
  });
});

test("reject action calls API client and refreshes detail", async () => {
  const user = userEvent.setup();

  api.getWorkflowRun
    .mockResolvedValueOnce(
      makeWorkflowRunDetail({ risk_level: "high", status: "approval_required" }),
    )
    .mockResolvedValueOnce(
      makeWorkflowRunDetail({ risk_level: "high", status: "rejected" }),
    );
  api.rejectWorkflowRun.mockResolvedValue(
    makeWorkflowRunSummary({ risk_level: "high", status: "rejected" }),
  );

  render(<WorkflowRunDetailPage api={api} workflowRunId={1} />);

  await user.type(await screen.findByLabelText("Reviewer Name"), "Sam Reviewer");
  await user.type(screen.getByLabelText("Comment"), "Rejected.");
  await user.click(screen.getByRole("button", { name: "Reject" }));

  await waitFor(() => {
    expect(api.rejectWorkflowRun).toHaveBeenCalledWith(1, {
      reviewer_name: "Sam Reviewer",
      comment: "Rejected.",
    });
  });
  await waitFor(() => {
    expect(api.getWorkflowRun).toHaveBeenCalledTimes(2);
  });
});

function makeMockApi() {
  return {
    approveWorkflowRun:
      vi.fn<
        (workflowRunId: number, payload: ApprovalDecisionInput) => Promise<WorkflowRun>
      >(),
    getWorkflowRun: vi.fn<(workflowRunId: number) => Promise<WorkflowRunDetail>>(),
    rejectWorkflowRun:
      vi.fn<
        (workflowRunId: number, payload: ApprovalDecisionInput) => Promise<WorkflowRun>
      >(),
  };
}

function makeWorkflowRunSummary(
  overrides: Partial<WorkflowRun> = {},
): WorkflowRun {
  return {
    id: 1,
    name: "low risk invoice",
    status: "completed",
    risk_level: "low",
    input_payload: {
      amount: 500,
      invoice_id: "INV-LOW-1",
      vendor: "Acme",
    },
    output_payload: {
      decision: "approve",
    },
    created_at: "2026-06-24T12:00:00Z",
    updated_at: "2026-06-24T12:01:00Z",
    completed_at: "2026-06-24T12:02:00Z",
    ...overrides,
  };
}

function makeWorkflowRunDetail(
  overrides: Partial<WorkflowRunDetail> = {},
): WorkflowRunDetail {
  return {
    ...makeWorkflowRunSummary(),
    output_payload: {
      decision: "approve",
      extracted: {
        amount: 500,
        invoice_id: "INV-LOW-1",
        vendor: "Acme",
      },
    },
    agent_steps: [
      {
        id: 1,
        step_index: 1,
        step_name: "inspect_input",
        input_snapshot: {
          input_payload: {
            amount: 500,
            invoice_id: "INV-LOW-1",
            vendor: "Acme",
          },
        },
        output_snapshot: {
          missing_fields: [],
        },
        status: "completed",
        started_at: "2026-06-24T12:00:10Z",
        completed_at: "2026-06-24T12:00:11Z",
        error_message: null,
      },
    ],
    validation_results: [
      {
        id: 1,
        rule_name: "required_vendor_present",
        passed: true,
        severity: "info",
        message: "Vendor is present.",
        created_at: "2026-06-24T12:00:12Z",
      },
    ],
    approval_decisions: [],
    ...overrides,
  };
}

function textIncludes(fragment: string) {
  return (content: string) => content.includes(fragment);
}
