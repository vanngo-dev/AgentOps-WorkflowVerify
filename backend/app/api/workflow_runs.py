from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.approval_decision import ApprovalDecision
from app.models.workflow_run import WorkflowRun
from app.schemas.approval_decision import ApprovalDecisionCreate
from app.schemas.workflow_run import (
    WorkflowRunCreate,
    WorkflowRunDetailRead,
    WorkflowRunRead,
)
from app.services.agent_simulator import execute_workflow_run

router = APIRouter(prefix="/api/workflow-runs", tags=["workflow runs"])

APPROVAL_REQUIRED_STATUS = "approval_required"


def utc_now() -> datetime:
    return datetime.now(UTC)


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


@router.post("/{workflow_run_id}/execute", response_model=WorkflowRunRead)
def execute_workflow_run_endpoint(
    workflow_run_id: int,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    workflow_run = db.get(WorkflowRun, workflow_run_id)

    if workflow_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    if workflow_run.status != "created":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workflow run cannot be executed unless status is created.",
        )

    return execute_workflow_run(db, workflow_run)


@router.post("/{workflow_run_id}/approve", response_model=WorkflowRunRead)
def approve_workflow_run(
    workflow_run_id: int,
    approval_create: ApprovalDecisionCreate,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    return record_approval_decision(
        db=db,
        workflow_run_id=workflow_run_id,
        approval_create=approval_create,
        decision="approved",
    )


@router.post("/{workflow_run_id}/reject", response_model=WorkflowRunRead)
def reject_workflow_run(
    workflow_run_id: int,
    approval_create: ApprovalDecisionCreate,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    return record_approval_decision(
        db=db,
        workflow_run_id=workflow_run_id,
        approval_create=approval_create,
        decision="rejected",
    )


@router.get("/{workflow_run_id}", response_model=WorkflowRunDetailRead)
def read_workflow_run(
    workflow_run_id: int,
    db: Session = Depends(get_db),
) -> WorkflowRun:
    statement = (
        select(WorkflowRun)
        .where(WorkflowRun.id == workflow_run_id)
        .options(
            selectinload(WorkflowRun.agent_steps),
            selectinload(WorkflowRun.validation_results),
            selectinload(WorkflowRun.approval_decisions),
        )
    )
    workflow_run = db.scalars(statement).one_or_none()

    if workflow_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    return workflow_run


def record_approval_decision(
    db: Session,
    workflow_run_id: int,
    approval_create: ApprovalDecisionCreate,
    decision: str,
) -> WorkflowRun:
    workflow_run = db.get(WorkflowRun, workflow_run_id)

    if workflow_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    if workflow_run.status != APPROVAL_REQUIRED_STATUS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workflow run is not waiting for human approval.",
        )

    now = utc_now()
    db.add(
        ApprovalDecision(
            workflow_run_id=workflow_run.id,
            decision=decision,
            reviewer_name=approval_create.reviewer_name,
            comment=approval_create.comment,
            created_at=now,
        ),
    )
    workflow_run.status = decision
    workflow_run.completed_at = now
    workflow_run.updated_at = now

    db.commit()
    db.refresh(workflow_run)

    return workflow_run
