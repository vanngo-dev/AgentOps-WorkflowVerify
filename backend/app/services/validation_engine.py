import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.request_context import get_trace_id
from app.models.validation_result import ValidationResult
from app.models.workflow_run import WorkflowRun

logger = logging.getLogger(__name__)

ALLOWED_DECISIONS = {"approve", "review", "reject"}
ALLOWED_SEVERITIES = {"info", "warning", "error"}
TERMINAL_STATUSES = {"completed", "validation_failed"}


@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    passed: bool
    severity: str
    message: str


def utc_now() -> datetime:
    return datetime.now(UTC)


def validate_workflow_run(db: Session, workflow_run: WorkflowRun) -> str:
    output_payload = workflow_run.output_payload or {}
    extracted = get_extracted_payload(output_payload)
    amount = extracted.get("amount")

    workflow_run.risk_level = determine_risk_level(amount)
    rule_results = evaluate_rules(output_payload, extracted, workflow_run.risk_level)
    failed_count = sum(not rule_result.passed for rule_result in rule_results)
    warning_count = sum(
        not rule_result.passed and rule_result.severity == "warning"
        for rule_result in rule_results
    )
    error_count = sum(
        not rule_result.passed and rule_result.severity == "error"
        for rule_result in rule_results
    )

    logger.info(
        "event=validation_summary trace_id=%s workflow_run_id=%s "
        "risk_level=%s passed=%s failed=%s warnings=%s errors=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.risk_level,
        len(rule_results) - failed_count,
        failed_count,
        warning_count,
        error_count,
    )

    for rule_result in rule_results:
        db.add(
            ValidationResult(
                workflow_run_id=workflow_run.id,
                rule_name=rule_result.rule_name,
                passed=rule_result.passed,
                severity=rule_result.severity,
                message=rule_result.message,
            ),
        )

    workflow_run.status = determine_workflow_status(
        rule_results,
        workflow_run.risk_level,
    )
    workflow_run.updated_at = utc_now()

    logger.info(
        "event=validation_status trace_id=%s workflow_run_id=%s status=%s "
        "risk_level=%s",
        get_trace_id(),
        workflow_run.id,
        workflow_run.status,
        workflow_run.risk_level,
    )

    return workflow_run.status


def get_extracted_payload(output_payload: dict[str, Any]) -> dict[str, Any]:
    extracted = output_payload.get("extracted")

    if isinstance(extracted, dict):
        return extracted

    return {}


def evaluate_rules(
    output_payload: dict[str, Any],
    extracted: dict[str, Any],
    risk_level: str,
) -> list[RuleResult]:
    return [
        validate_required_vendor_present(extracted),
        validate_required_invoice_id_present(extracted),
        validate_amount_is_positive(extracted),
        validate_decision_is_valid(output_payload),
        validate_high_amount_requires_review(risk_level),
    ]


def validate_required_vendor_present(extracted: dict[str, Any]) -> RuleResult:
    vendor = extracted.get("vendor")
    passed = bool(str(vendor).strip()) if vendor is not None else False

    if passed:
        return RuleResult(
            rule_name="required_vendor_present",
            passed=True,
            severity="info",
            message="Vendor is present.",
        )

    return RuleResult(
        rule_name="required_vendor_present",
        passed=False,
        severity="error",
        message="Vendor is required.",
    )


def validate_required_invoice_id_present(extracted: dict[str, Any]) -> RuleResult:
    invoice_id = extracted.get("invoice_id")
    passed = bool(str(invoice_id).strip()) if invoice_id is not None else False

    if passed:
        return RuleResult(
            rule_name="required_invoice_id_present",
            passed=True,
            severity="info",
            message="Invoice ID is present.",
        )

    return RuleResult(
        rule_name="required_invoice_id_present",
        passed=False,
        severity="error",
        message="Invoice ID is required.",
    )


def validate_amount_is_positive(extracted: dict[str, Any]) -> RuleResult:
    amount = extracted.get("amount")
    passed = is_number(amount) and amount > 0

    if passed:
        return RuleResult(
            rule_name="amount_is_positive",
            passed=True,
            severity="info",
            message="Amount is positive.",
        )

    return RuleResult(
        rule_name="amount_is_positive",
        passed=False,
        severity="error",
        message="Amount must be a positive number.",
    )


def validate_decision_is_valid(output_payload: dict[str, Any]) -> RuleResult:
    decision = output_payload.get("decision")
    passed = decision in ALLOWED_DECISIONS

    if passed:
        return RuleResult(
            rule_name="decision_is_valid",
            passed=True,
            severity="info",
            message="Decision is valid.",
        )

    return RuleResult(
        rule_name="decision_is_valid",
        passed=False,
        severity="error",
        message="Decision must be approve, review, or reject.",
    )


def validate_high_amount_requires_review(risk_level: str) -> RuleResult:
    if risk_level == "high":
        return RuleResult(
            rule_name="high_amount_requires_review",
            passed=False,
            severity="warning",
            message="High amount requires human review.",
        )

    return RuleResult(
        rule_name="high_amount_requires_review",
        passed=True,
        severity="info",
        message="Amount does not require human review.",
    )


def determine_risk_level(amount: Any) -> str:
    if not is_number(amount) or amount <= 0:
        return "unknown"
    if amount < 1000:
        return "low"
    if amount < 5000:
        return "medium"

    return "high"


def determine_workflow_status(
    rule_results: list[RuleResult],
    risk_level: str,
) -> str:
    has_error_failure = any(
        not rule_result.passed and rule_result.severity == "error"
        for rule_result in rule_results
    )

    if has_error_failure:
        return "validation_failed"
    if risk_level == "high":
        return "approval_required"

    return "completed"


def is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)
