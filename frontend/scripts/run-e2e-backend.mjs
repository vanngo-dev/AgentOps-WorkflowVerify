import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const backendRoot = path.resolve(scriptDir, "../../backend");
const env = {
  ...process.env,
  DATABASE_URL: "sqlite:///./tmp/phase10_e2e.sqlite3",
};

await fs.mkdir(path.join(backendRoot, "tmp"), { recursive: true });
await run("python", ["-m", "alembic", "upgrade", "head"], {
  cwd: backendRoot,
  env,
});

const server = spawn(
  "python",
  ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
  {
    cwd: backendRoot,
    env,
    stdio: "inherit",
  },
);

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
server.on("exit", (code) => {
  process.exit(code ?? 0);
});

function shutdown() {
  server.kill();
}

function run(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      ...options,
      stdio: "inherit",
    });

    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${command} ${args.join(" ")} exited with ${code}`));
    });
  });
}
