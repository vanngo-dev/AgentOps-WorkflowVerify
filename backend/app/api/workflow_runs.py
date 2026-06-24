import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.request_context import get_trace_id
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workflow-runs", tags=["workflow runs"])

APPROVAL_REQUIRED_STATUS = "approval_required"


def utc_now() -> datetime:
    return datetime.now(UTC)


def attach_trace_id(workflow_run: WorkflowRun) -> WorkflowRun:
    workflow_run.trace_id = get_trace_id()
    return workflow_run


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

    logger.info(
        "event=workflow_created trace_id=%s workflow_run_id=%s status=%s "
        "risk_level=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.status,
        workflow_run.risk_level,
    )

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
        logger.warning(
            "event=api_error trace_id=%s workflow_run_id=%s action=execute "
            "status_code=404 reason=workflow_not_found",
            get_trace_id(),
            workflow_run_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    if workflow_run.status != "created":
        logger.warning(
            "event=api_error trace_id=%s workflow_run_id=%s action=execute "
            "status_code=409 reason=invalid_status current_status=%s",
            get_trace_id(),
            workflow_run_id,
            workflow_run.status,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workflow run cannot be executed unless status is created.",
        )

    logger.info(
        "event=workflow_execution_requested trace_id=%s workflow_run_id=%s "
        "status=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.status,
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
        logger.warning(
            "event=api_error trace_id=%s workflow_run_id=%s action=read_detail "
            "status_code=404 reason=workflow_not_found",
            get_trace_id(),
            workflow_run_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    return attach_trace_id(workflow_run)


def record_approval_decision(
    db: Session,
    workflow_run_id: int,
    approval_create: ApprovalDecisionCreate,
    decision: str,
) -> WorkflowRun:
    workflow_run = db.get(WorkflowRun, workflow_run_id)

    if workflow_run is None:
        logger.warning(
            "event=api_error trace_id=%s workflow_run_id=%s action=%s "
            "status_code=404 reason=workflow_not_found",
            get_trace_id(),
            workflow_run_id,
            decision,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found.",
        )

    if workflow_run.status != APPROVAL_REQUIRED_STATUS:
        logger.warning(
            "event=api_error trace_id=%s workflow_run_id=%s action=%s "
            "status_code=409 reason=invalid_status current_status=%s",
            get_trace_id(),
            workflow_run_id,
            decision,
            workflow_run.status,
        )
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

    logger.info(
        "event=approval_decision_recorded trace_id=%s workflow_run_id=%s "
        "decision=%s status=%s",
        get_trace_id(),
        workflow_run.id,
        decision,
        workflow_run.status,
    )

    return workflow_run
