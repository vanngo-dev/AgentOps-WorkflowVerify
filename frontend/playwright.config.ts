import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  reporter: [["list"], ["html", { open: "never" }]],
  timeout: 45_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "node scripts/run-e2e-backend.mjs",
      url: "http://localhost:8000/ready",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "node scripts/run-e2e-frontend.mjs",
      url: "http://localhost:5173/workflow-runs",
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
