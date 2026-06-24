import {
  type FormEvent,
  type MouseEvent,
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createWorkflowRun,
  executeWorkflowRun,
  listWorkflowRuns,
  type WorkflowRun,
} from "../api/workflowRuns";

type WorkflowRunsApi = {
  createWorkflowRun: typeof createWorkflowRun;
  executeWorkflowRun: typeof executeWorkflowRun;
  listWorkflowRuns: typeof listWorkflowRuns;
};

type WorkflowRunsPageProps = {
  api?: WorkflowRunsApi;
  onNavigate?: (path: string) => void;
};

type FormState = {
  amount: string;
  invoiceId: string;
  name: string;
  vendor: string;
};

const initialFormState: FormState = {
  amount: "",
  invoiceId: "",
  name: "",
  vendor: "",
};

const defaultApi: WorkflowRunsApi = {
  createWorkflowRun,
  executeWorkflowRun,
  listWorkflowRuns,
};

export default function WorkflowRunsPage({
  api = defaultApi,
  onNavigate,
}: WorkflowRunsPageProps) {
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [executingId, setExecutingId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshWorkflowRuns = useCallback(async () => {
    const nextWorkflowRuns = await api.listWorkflowRuns();
    setWorkflowRuns(nextWorkflowRuns);
  }, [api]);

  useEffect(() => {
    let isMounted = true;

    async function loadWorkflowRuns() {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const nextWorkflowRuns = await api.listWorkflowRuns();

        if (isMounted) {
          setWorkflowRuns(nextWorkflowRuns);
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

    void loadWorkflowRuns();

    return () => {
      isMounted = false;
    };
  }, [api]);

  async function handleCreateWorkflowRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const amount = Number(formState.amount);

    if (Number.isNaN(amount)) {
      setErrorMessage("Amount must be a number.");
      return;
    }

    setIsCreating(true);
    setErrorMessage(null);

    try {
      await api.createWorkflowRun({
        name: formState.name,
        input_payload: {
          vendor: formState.vendor,
          amount,
          invoice_id: formState.invoiceId,
        },
      });
      await refreshWorkflowRuns();
      setFormState(initialFormState);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsCreating(false);
    }
  }

  async function handleExecuteWorkflowRun(workflowRunId: number) {
    setExecutingId(workflowRunId);
    setErrorMessage(null);

    try {
      await api.executeWorkflowRun(workflowRunId);
      await refreshWorkflowRuns();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setExecutingId(null);
    }
  }

  return (
    <section className="workflow-dashboard" aria-labelledby="workflow-runs-title">
      <div className="dashboard-header">
        <div className="page-heading">
          <p className="eyebrow">Workflows</p>
          <h2 id="workflow-runs-title">Workflow Runs</h2>
        </div>
        <form className="workflow-form" onSubmit={handleCreateWorkflowRun}>
          <h3>Create Workflow Run</h3>
          <label>
            <span>Name</span>
            <input
              name="name"
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
              required
              type="text"
              value={formState.name}
            />
          </label>
          <label>
            <span>Vendor</span>
            <input
              name="vendor"
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  vendor: event.target.value,
                }))
              }
              type="text"
              value={formState.vendor}
            />
          </label>
          <label>
            <span>Amount</span>
            <input
              name="amount"
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  amount: event.target.value,
                }))
              }
              required
              type="number"
              value={formState.amount}
            />
          </label>
          <label>
            <span>Invoice ID</span>
            <input
              name="invoiceId"
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  invoiceId: event.target.value,
                }))
              }
              required
              type="text"
              value={formState.invoiceId}
            />
          </label>
          <button disabled={isCreating} type="submit">
            {isCreating ? "Creating..." : "Create Run"}
          </button>
        </form>
      </div>

      {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}

      <div className="workflow-list-panel">
        {isLoading ? <p className="state-message">Loading workflow runs...</p> : null}

        {!isLoading && workflowRuns.length === 0 ? (
          <p className="state-message">No workflow runs yet.</p>
        ) : null}

        {!isLoading && workflowRuns.length > 0 ? (
          <WorkflowRunTable
            executingId={executingId}
            onExecute={handleExecuteWorkflowRun}
            onNavigate={onNavigate}
            workflowRuns={workflowRuns}
          />
        ) : null}
      </div>
    </section>
  );
}

type WorkflowRunTableProps = {
  executingId: number | null;
  onExecute: (workflowRunId: number) => void;
  onNavigate?: (path: string) => void;
  workflowRuns: WorkflowRun[];
};

function WorkflowRunTable({
  executingId,
  onExecute,
  onNavigate,
  workflowRuns,
}: WorkflowRunTableProps) {
  function handleDetailClick(
    event: MouseEvent<HTMLAnchorElement>,
    workflowRunId: number,
  ) {
    if (!onNavigate || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }

    event.preventDefault();
    onNavigate(`/workflow-runs/${workflowRunId}`);
  }

  return (
    <div className="workflow-table-wrap">
      <table className="workflow-table">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Status</th>
            <th scope="col">Risk Level</th>
            <th scope="col">Created</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          {workflowRuns.map((workflowRun) => (
            <tr key={workflowRun.id}>
              <td>
                <a
                  className="table-link"
                  href={`/workflow-runs/${workflowRun.id}`}
                  onClick={(event) => handleDetailClick(event, workflowRun.id)}
                >
                  {workflowRun.name}
                </a>
              </td>
              <td>
                <span className="status-pill">{workflowRun.status}</span>
              </td>
              <td>{workflowRun.risk_level}</td>
              <td>
                <time dateTime={workflowRun.created_at}>
                  {formatTimestamp(workflowRun.created_at)}
                </time>
              </td>
              <td>
                {workflowRun.status === "created" ? (
                  <button
                    aria-label={`Execute ${workflowRun.name}`}
                    disabled={executingId === workflowRun.id}
                    onClick={() => onExecute(workflowRun.id)}
                    type="button"
                  >
                    {executingId === workflowRun.id ? "Executing..." : "Execute"}
                  </button>
                ) : (
                  <span className="muted">-</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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
