import { expect, type Locator, type Page, test } from "@playwright/test";

test("low-risk workflow completes and detail shows trace evidence", async ({
  page,
}) => {
  const workflow = makeWorkflowInput("low", 500);

  await openDashboard(page);
  await createWorkflowRun(page, workflow);

  const row = workflowRow(page, workflow.name);
  await expect(row.getByText("created", { exact: true })).toBeVisible();
  await expect(row.getByText("unknown", { exact: true })).toBeVisible();

  await row.getByRole("button", { name: `Execute ${workflow.name}` }).click();
  await expect(row.getByText("completed", { exact: true })).toBeVisible();
  await expect(row.getByText("low", { exact: true })).toBeVisible();

  await row.getByRole("link", { name: workflow.name, exact: true }).click();
  await expect(
    page.getByRole("heading", { name: workflow.name, exact: true }),
  ).toBeVisible();
  await expect(
    page.getByLabel("Input Payload").getByText(workflow.invoiceId),
  ).toBeVisible();
  await expect(
    page.getByLabel("Output Payload").getByText('"decision": "approve"'),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Agent Step Timeline" }),
  ).toBeVisible();
  await expect(page.getByText("inspect_input", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Validation Results" }),
  ).toBeVisible();
  await expect(page.getByText("required_vendor_present")).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Reject" })).toHaveCount(0);
});

test("high-risk workflow can be approved from detail page", async ({ page }) => {
  const workflow = makeWorkflowInput("high", 7500);

  await openDashboard(page);
  await createWorkflowRun(page, workflow);

  const row = workflowRow(page, workflow.name);
  await row.getByRole("button", { name: `Execute ${workflow.name}` }).click();
  await expect(row.getByText("approval_required", { exact: true })).toBeVisible();
  await expect(row.getByText("high", { exact: true })).toBeVisible();

  await row.getByRole("link", { name: workflow.name, exact: true }).click();
  await expect(
    page.getByRole("heading", { name: workflow.name, exact: true }),
  ).toBeVisible();
  await expect(page.getByText("high_amount_requires_review")).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Reject" })).toBeVisible();

  await page.getByLabel("Reviewer Name").fill("Phase 10 Reviewer");
  await page.getByLabel("Comment").fill("Approved by Phase 10 E2E test.");
  await page.getByRole("button", { name: "Approve" }).click();

  await expect(
    page.getByRole("definition").filter({ hasText: "approved" }),
  ).toBeVisible();
  const approvalHistory = page.getByRole("region", {
    name: "Approval History",
  });
  await expect(
    approvalHistory.getByRole("cell", { name: "approved", exact: true }),
  ).toBeVisible();
  await expect(
    approvalHistory.getByRole("cell", { name: "Phase 10 Reviewer" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Reject" })).toHaveCount(0);
});

async function openDashboard(page: Page) {
  await page.goto("/workflow-runs");
  await expect(page.getByRole("heading", { name: "Workflow Runs" })).toBeVisible();
}

async function createWorkflowRun(
  page: Page,
  workflow: ReturnType<typeof makeWorkflowInput>,
) {
  await page.getByLabel("Name").fill(workflow.name);
  await page.getByLabel("Vendor").fill("Acme");
  await page.getByLabel("Amount").fill(String(workflow.amount));
  await page.getByLabel("Invoice ID").fill(workflow.invoiceId);
  await page.getByRole("button", { name: "Create Run" }).click();

  await expect(workflowRow(page, workflow.name)).toBeVisible();
}

function workflowRow(page: Page, name: string): Locator {
  return page
    .getByRole("row")
    .filter({ has: page.getByRole("link", { name, exact: true }) });
}

function makeWorkflowInput(kind: "high" | "low", amount: number) {
  const uniqueId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  return {
    amount,
    invoiceId: `INV-P10-${kind.toUpperCase()}-${uniqueId}`,
    name: `phase 10 ${kind} workflow ${uniqueId}`,
  };
}
