import {
  type MouseEvent,
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  approveWorkflowRun,
  getWorkflowRun,
  rejectWorkflowRun,
  type ApprovalDecisionInput,
  type WorkflowRunDetail,
} from "../api/workflowRuns";

type WorkflowRunDetailApi = {
  approveWorkflowRun: typeof approveWorkflowRun;
  getWorkflowRun: typeof getWorkflowRun;
  rejectWorkflowRun: typeof rejectWorkflowRun;
};

type WorkflowRunDetailPageProps = {
  api?: WorkflowRunDetailApi;
  onNavigate?: (path: string) => void;
  workflowRunId: number;
};

type ApprovalFormState = {
  comment: string;
  reviewerName: string;
};

const defaultApi: WorkflowRunDetailApi = {
  approveWorkflowRun,
  getWorkflowRun,
  rejectWorkflowRun,
};

const initialApprovalFormState: ApprovalFormState = {
  comment: "",
  reviewerName: "",
};

export default function WorkflowRunDetailPage({
  api = defaultApi,
  onNavigate,
  workflowRunId,
}: WorkflowRunDetailPageProps) {
  const [workflowRun, setWorkflowRun] = useState<WorkflowRunDetail | null>(null);
  const [approvalForm, setApprovalForm] = useState<ApprovalFormState>(
    initialApprovalFormState,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshWorkflowRun = useCallback(async () => {
    const nextWorkflowRun = await api.getWorkflowRun(workflowRunId);
    setWorkflowRun(nextWorkflowRun);
  }, [api, workflowRunId]);

  useEffect(() => {
    let isMounted = true;

    async function loadWorkflowRun() {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const nextWorkflowRun = await api.getWorkflowRun(workflowRunId);

        if (isMounted) {
          setWorkflowRun(nextWorkflowRun);
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(getErrorMessage(error));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadWorkflowRun();

    return () => {
      isMounted = false;
    };
  }, [api, workflowRunId]);

  function handleBackClick(event: MouseEvent<HTMLAnchorElement>) {
    if (
      !onNavigate ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    event.preventDefault();
    onNavigate("/workflow-runs");
  }

  async function handleApprovalDecision(
    decision: "approve" | "reject",
  ) {
    const payload: ApprovalDecisionInput = {
      reviewer_name: approvalForm.reviewerName,
      comment: approvalForm.comment,
    };

    if (!payload.reviewer_name.trim()) {
      setErrorMessage("Reviewer name is required.");
      return;
    }

    setIsSubmittingDecision(true);
    setErrorMessage(null);

    try {
      if (decision === "approve") {
        await api.approveWorkflowRun(workflowRunId, payload);
      } else {
        await api.rejectWorkflowRun(workflowRunId, payload);
      }

      await refreshWorkflowRun();
      setApprovalForm(initialApprovalFormState);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsSubmittingDecision(false);
    }
  }

  return (
    <section
      className="workflow-detail"
      aria-labelledby="workflow-detail-title"
    >
      <a
        className="back-link"
        href="/workflow-runs"
        onClick={handleBackClick}
      >
        Back to Workflow Runs
      </a>

      {isLoading ? (
        <p className="state-message">Loading workflow detail...</p>
      ) : null}

      {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}

      {!isLoading && workflowRun ? (
        <>
          <WorkflowSummary workflowRun={workflowRun} />
          <JsonPanel
            title="Input Payload"
            value={workflowRun.input_payload}
          />
          <JsonPanel
            emptyMessage="No output payload yet."
            title="Output Payload"
            value={workflowRun.output_payload}
          />
          <AgentStepTimeline workflowRun={workflowRun} />
          <ValidationResults workflowRun={workflowRun} />
          <ApprovalHistory workflowRun={workflowRun} />
          {workflowRun.status === "approval_required" ? (
            <ApprovalActions
              approvalForm={approvalForm}
              isSubmittingDecision={isSubmittingDecision}
              onChange={setApprovalForm}
              onSubmitDecision={handleApprovalDecision}
            />
          ) : null}
        </>
      ) : null}
    </section>
  );
}

function WorkflowSummary({ workflowRun }: { workflowRun: WorkflowRunDetail }) {
  return (
    <div className="detail-panel">
      <div className="page-heading">
        <p className="eyebrow">Workflow Detail</p>
        <h2 id="workflow-detail-title">{workflowRun.name}</h2>
      </div>
      <dl className="summary-grid">
        <div>
          <dt>Status</dt>
          <dd>{workflowRun.status}</dd>
        </div>
        <div>
          <dt>Risk Level</dt>
          <dd>{workflowRun.risk_level}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{formatTimestamp(workflowRun.created_at)}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{formatTimestamp(workflowRun.updated_at)}</dd>
        </div>
        {workflowRun.completed_at ? (
          <div>
            <dt>Completed</dt>
            <dd>{formatTimestamp(workflowRun.completed_at)}</dd>
          </div>
        ) : null}
        {workflowRun.trace_id ? (
          <div>
            <dt>Trace ID</dt>
            <dd className="trace-id-value">{workflowRun.trace_id}</dd>
          </div>
        ) : null}
      </dl>
    </div>
  );
}

function JsonPanel({
  emptyMessage = "No data available.",
  title,
  value,
}: {
  emptyMessage?: string;
  title: string;
  value: Record<string, unknown> | null;
}) {
  return (
    <section className="detail-panel" aria-labelledby={slugify(title)}>
      <h3 id={slugify(title)}>{title}</h3>
      {value ? (
        <pre className="json-block">{JSON.stringify(value, null, 2)}</pre>
      ) : (
        <p className="state-message compact">{emptyMessage}</p>
      )}
    </section>
  );
}

function AgentStepTimeline({
  workflowRun,
}: {
  workflowRun: WorkflowRunDetail;
}) {
  return (
    <section className="detail-panel" aria-labelledby="agent-step-timeline">
      <h3 id="agent-step-timeline">Agent Step Timeline</h3>
      {workflowRun.agent_steps.length === 0 ? (
        <p className="state-message compact">No agent steps yet.</p>
      ) : (
        <div className="timeline">
          {workflowRun.agent_steps.map((step) => (
            <article className="timeline-item" key={step.id}>
              <div className="timeline-heading">
                <span>Step {step.step_index}</span>
                <strong>{step.step_name}</strong>
                <em>{step.status}</em>
              </div>
              {step.error_message ? (
                <p className="error-banner">{step.error_message}</p>
              ) : null}
              <div className="json-grid">
                <JsonBlock
                  title={`Step ${step.step_index} Input`}
                  value={step.input_snapshot}
                />
                <JsonBlock
                  title={`Step ${step.step_index} Output`}
                  value={step.output_snapshot}
                />
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function ValidationResults({
  workflowRun,
}: {
  workflowRun: WorkflowRunDetail;
}) {
  return (
    <section className="detail-panel" aria-labelledby="validation-results">
      <h3 id="validation-results">Validation Results</h3>
      {workflowRun.validation_results.length === 0 ? (
        <p className="state-message compact">No validation results yet.</p>
      ) : (
        <div className="detail-table-wrap">
          <table className="detail-table">
            <thead>
              <tr>
                <th scope="col">Rule</th>
                <th scope="col">Passed</th>
                <th scope="col">Severity</th>
                <th scope="col">Message</th>
                <th scope="col">Created</th>
              </tr>
            </thead>
            <tbody>
              {workflowRun.validation_results.map((result) => (
                <tr key={result.id}>
                  <td>{result.rule_name}</td>
                  <td>{result.passed ? "yes" : "no"}</td>
                  <td>{result.severity}</td>
                  <td>{result.message}</td>
                  <td>{formatTimestamp(result.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function ApprovalHistory({
  workflowRun,
}: {
  workflowRun: WorkflowRunDetail;
}) {
  return (
    <section className="detail-panel" aria-labelledby="approval-history">
      <h3 id="approval-history">Approval History</h3>
      {workflowRun.approval_decisions.length === 0 ? (
        <p className="state-message compact">No approval decisions yet.</p>
      ) : (
        <div className="detail-table-wrap">
          <table className="detail-table">
            <thead>
              <tr>
                <th scope="col">Decision</th>
                <th scope="col">Reviewer</th>
                <th scope="col">Comment</th>
                <th scope="col">Created</th>
              </tr>
            </thead>
            <tbody>
              {workflowRun.approval_decisions.map((decision) => (
                <tr key={decision.id}>
                  <td>{decision.decision}</td>
                  <td>{decision.reviewer_name}</td>
                  <td>{decision.comment}</td>
                  <td>{formatTimestamp(decision.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function ApprovalActions({
  approvalForm,
  isSubmittingDecision,
  onChange,
  onSubmitDecision,
}: {
  approvalForm: ApprovalFormState;
  isSubmittingDecision: boolean;
  onChange: (formState: ApprovalFormState) => void;
  onSubmitDecision: (decision: "approve" | "reject") => void;
}) {
  return (
    <section className="detail-panel" aria-labelledby="approval-actions">
      <h3 id="approval-actions">Approval Actions</h3>
      <form className="approval-form">
        <label>
          <span>Reviewer Name</span>
          <input
            name="reviewerName"
            onChange={(event) =>
              onChange({
                ...approvalForm,
                reviewerName: event.target.value,
              })
            }
            required
            type="text"
            value={approvalForm.reviewerName}
          />
        </label>
        <label>
          <span>Comment</span>
          <input
            name="comment"
            onChange={(event) =>
              onChange({
                ...approvalForm,
                comment: event.target.value,
              })
            }
            type="text"
            value={approvalForm.comment}
          />
        </label>
        <div className="button-row">
          <button
            disabled={isSubmittingDecision}
            onClick={() => onSubmitDecision("approve")}
            type="button"
          >
            Approve
          </button>
          <button
            className="danger-button"
            disabled={isSubmittingDecision}
            onClick={() => onSubmitDecision("reject")}
            type="button"
          >
            Reject
          </button>
        </div>
      </form>
    </section>
  );
}

function formatTimestamp(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong.";
}

function slugify(value: string) {
  return value.toLowerCase().replace(/\s+/g, "-");
}

function JsonBlock({
  emptyMessage = "No data available.",
  title,
  value,
}: {
  emptyMessage?: string;
  title: string;
  value: Record<string, unknown> | null;
}) {
  return (
    <div className="json-panel">
      <h4>{title}</h4>
      {value ? (
        <pre className="json-block">{JSON.stringify(value, null, 2)}</pre>
      ) : (
        <p className="state-message compact">{emptyMessage}</p>
      )}
    </div>
  );
}
