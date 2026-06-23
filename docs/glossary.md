# Glossary

This glossary explains the project language in plain terms. Treat it like the vocabulary section of a tutorial: these are the words we will keep using as the platform grows.

## Agent

An agent is software that can decide what step to take next. In this project, an agent may eventually inspect a workflow, call tools, produce outputs, and ask for approval.

In the first implementation phases, the agent will be simulated and deterministic. That means it will behave the same way every time for the same input.

## AgentOps

AgentOps is the practice of operating AI agents safely.

It includes the habits and systems needed to test agents, monitor agent runs, validate decisions, review failures, and decide where humans must stay in control.

## Approval Checkpoint

An approval checkpoint is a required pause in a workflow where a human must review something before the workflow continues.

For example, an agent might draft a customer response, but a person must approve it before it is sent.

## Deterministic Simulated Agent

A deterministic simulated agent is a fake agent that follows predictable rules.

It is useful at the beginning because it lets us build the platform without debugging LLM randomness at the same time.

## Human Approval

Human approval means a person must explicitly allow a workflow step to continue.

This matters when a step could affect customers, money, data, permissions, or external systems.

## Observability

Observability means recording enough information to understand what happened during a workflow run.

For this project, that may include step history, tool calls, validation results, timestamps, approvals, failures, and final outcomes.

## Phase Gate

A phase gate is a stopping point between build phases.

Each phase must be implemented, tested, documented, committed, and stopped before the next phase starts.

## Testing

Testing checks whether the system behaves the way we expect before we trust it.

In this project, tests will eventually cover platform behavior, workflow rules, simulated agent runs, and user-facing review flows.

## Validation

Validation checks whether a specific workflow run satisfies the rules.

Testing is often about the software. Validation is often about one run of a workflow.

## Workflow

A workflow is a sequence of steps that should happen in a controlled order.

For example: receive request, classify request, draft action, request approval, complete action, record result.

## Workflow Verification

Workflow verification means checking that a workflow run followed the required steps, rules, approvals, and safety boundaries.

The platform is being built to make those checks visible, repeatable, and easy to inspect.
