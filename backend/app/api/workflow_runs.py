from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workflow_run import WorkflowRun
from app.schemas.workflow_run import WorkflowRunCreate, WorkflowRunRead

router = APIRouter(prefix="/api/workflow-runs", tags=["workflow runs"])


@router.post(
    "",
    response_model=WorkflowRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow_run(
    workflow_run_create: WorkflowRunCreate,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    workflow_run = WorkflowRun(
        name=workflow_run_create.name,
        input_payload=workflow_run_create.input_payload,
    )

    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    return workflow_run


@router.get("", response_model=list[WorkflowRunRead])
def list_workflow_runs(db: Session = Depends(get_db)) -> list[WorkflowRun]:
    statement = select(WorkflowRun).order_by(WorkflowRun.id)

    return list(db.scalars(statement).all())


@router.get("/{workflow_run_id}", response_model=WorkflowRunRead)
def read_workflow_run(
    workflow_run_id: int,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    workflow_run = db.get(WorkflowRun, workflow_run_id)

    if workflow_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    return workflow_run
