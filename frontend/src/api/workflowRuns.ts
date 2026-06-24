import { requestJson } from "./client";

export type WorkflowRun = {
  id: number;
  name: string;
  status: string;
  risk_level: string;
  input_payload: Record<string, unknown> | null;
  output_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  trace_id?: string | null;
};

export type AgentStep = {
  id: number;
  step_index: number;
  step_name: string;
  input_snapshot: Record<string, unknown> | null;
  output_snapshot: Record<string, unknown> | null;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
};

export type ValidationResult = {
  id: number;
  rule_name: string;
  passed: boolean;
  severity: string;
  message: string | null;
  created_at: string;
};

export type ApprovalDecision = {
  id: number;
  decision: string;
  reviewer_name: string | null;
  comment: string | null;
  created_at: string;
};

export type WorkflowRunDetail = WorkflowRun & {
  agent_steps: AgentStep[];
  validation_results: ValidationResult[];
  approval_decisions: ApprovalDecision[];
};

export type CreateWorkflowRunInput = {
  name: string;
  input_payload: {
    vendor: string;
    amount: number;
    invoice_id: string;
  };
};

export type ApprovalDecisionInput = {
  reviewer_name: string;
  comment: string;
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

export function getWorkflowRun(workflowRunId: number) {
  return requestJson<WorkflowRunDetail>(`/api/workflow-runs/${workflowRunId}`);
}

export function approveWorkflowRun(
  workflowRunId: number,
  approvalDecision: ApprovalDecisionInput,
) {
  return requestJson<WorkflowRun>(`/api/workflow-runs/${workflowRunId}/approve`, {
    body: JSON.stringify(approvalDecision),
    method: "POST",
  });
}

export function rejectWorkflowRun(
  workflowRunId: number,
  approvalDecision: ApprovalDecisionInput,
) {
  return requestJson<WorkflowRun>(`/api/workflow-runs/${workflowRunId}/reject`, {
    body: JSON.stringify(approvalDecision),
    method: "POST",
  });
}
