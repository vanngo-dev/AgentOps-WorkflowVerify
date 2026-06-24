import { requestJson } from "./client";

export type WorkflowRun = {
  id: number;
  name: string;
  status: string;
  risk_level: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type CreateWorkflowRunInput = {
  name: string;
  input_payload: {
    vendor: string;
    amount: number;
    invoice_id: string;
  };
};

export function listWorkflowRuns() {
  return requestJson<WorkflowRun[]>("/api/workflow-runs");
}

export function createWorkflowRun(workflowRun: CreateWorkflowRunInput) {
  return requestJson<WorkflowRun>("/api/workflow-runs", {
    body: JSON.stringify(workflowRun),
    method: "POST",
  });
}

export function executeWorkflowRun(workflowRunId: number) {
  return requestJson<WorkflowRun>(`/api/workflow-runs/${workflowRunId}/execute`, {
    method: "POST",
  });
}
