import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.request_context import get_trace_id
from app.models.agent_step import AgentStep
from app.models.workflow_run import WorkflowRun
from app.services.validation_engine import TERMINAL_STATUSES, validate_workflow_run

logger = logging.getLogger(__name__)

SIMULATED_STEP_NAMES = (
    "inspect_input",
    "classify_document",
    "extract_fields",
    "calculate_risk",
    "produce_decision",
)

REQUIRED_FIELDS = ("vendor", "amount", "invoice_id")


def utc_now() -> datetime:
    return datetime.now(UTC)


def execute_workflow_run(db: Session, workflow_run: WorkflowRun) -> WorkflowRun:
    input_payload = workflow_run.input_payload or {}
    context: dict[str, Any] = {"input_payload": input_payload}

    workflow_run.status = "running"
    workflow_run.updated_at = utc_now()
    db.flush()

    logger.info(
        "event=workflow_execution_start trace_id=%s workflow_run_id=%s status=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.status,
    )

    for step_index, step_name in enumerate(SIMULATED_STEP_NAMES, start=1):
        logger.info(
            "event=agent_step_created trace_id=%s workflow_run_id=%s "
            "step_index=%s step_name=%s",
            get_trace_id(),
            workflow_run.id,
            step_index,
            step_name,
        )
        started_at = utc_now()
        input_snapshot = dict(context)
        output_snapshot = run_simulated_step(step_name, context)
        context[step_name] = output_snapshot

        db.add(
            AgentStep(
                workflow_run_id=workflow_run.id,
                step_index=step_index,
                step_name=step_name,
                input_snapshot=input_snapshot,
                output_snapshot=output_snapshot,
                status="completed",
                started_at=started_at,
                completed_at=utc_now(),
                error_message=None,
            ),
        )
        logger.info(
            "event=agent_step_completed trace_id=%s workflow_run_id=%s "
            "step_index=%s step_name=%s status=completed",
            get_trace_id(),
            workflow_run.id,
            step_index,
            step_name,
        )

    final_output = context["produce_decision"]
    finished_at = utc_now()
    workflow_run.output_payload = final_output
    workflow_run.updated_at = finished_at

    final_status = validate_workflow_run(db, workflow_run)
    if final_status in TERMINAL_STATUSES:
        workflow_run.completed_at = utc_now()
    else:
        workflow_run.completed_at = None
    workflow_run.updated_at = utc_now()

    db.commit()
    db.refresh(workflow_run)

    logger.info(
        "event=workflow_execution_finished trace_id=%s workflow_run_id=%s "
        "status=%s risk_level=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.status,
        workflow_run.risk_level,
    )

    return workflow_run


def run_simulated_step(
    step_name: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    input_payload = context["input_payload"]

    if step_name == "inspect_input":
        return inspect_input(input_payload)
    if step_name == "classify_document":
        return classify_document()
    if step_name == "extract_fields":
        return extract_fields(input_payload)
    if step_name == "calculate_risk":
        return calculate_risk()
    if step_name == "produce_decision":
        return produce_decision(context)

    raise ValueError(f"Unknown simulated step: {step_name}")


def inspect_input(input_payload: dict[str, Any]) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_FIELDS if input_payload.get(field) is None
    ]

    return {
        "present_fields": sorted(input_payload.keys()),
        "missing_fields": missing_fields,
    }


def classify_document() -> dict[str, Any]:
    return {
        "document_type": "vendor_invoice",
        "confidence": 1.0,
    }


def extract_fields(input_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "vendor": input_payload.get("vendor"),
        "amount": input_payload.get("amount"),
        "invoice_id": input_payload.get("invoice_id"),
    }


def calculate_risk() -> dict[str, Any]:
    return {
        "risk_level": "unknown",
        "reason": "Risk scoring is deferred to the validation phase.",
    }


def produce_decision(context: dict[str, Any]) -> dict[str, Any]:
    extracted = context["extract_fields"]

    return {
        "decision": "approve",
        "reason": (
            "Amount is within standard threshold and required fields are present."
        ),
        "extracted": extracted,
    }
