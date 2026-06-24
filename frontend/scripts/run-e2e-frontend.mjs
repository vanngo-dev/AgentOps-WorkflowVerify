import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";

process.env.VITE_API_BASE_URL =
  process.env.VITE_API_BASE_URL ?? "http://localhost:8000";

await import("./run-vite-build.mjs");

const root = process.cwd();
const distRoot = path.join(root, "dist");
const server = http.createServer(async (request, response) => {
  try {
    const filePath = await resolveFilePath(request.url ?? "/");
    const content = await fs.readFile(filePath);

    response.writeHead(200, {
      "Content-Type": getContentType(filePath),
    });
    response.end(content);
  } catch {
    response.writeHead(404, {
      "Content-Type": "text/plain; charset=utf-8",
    });
    response.end("Not found");
  }
});

server.listen(5173, () => {
  console.log("E2E frontend running at http://localhost:5173/");
});

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

function shutdown() {
  server.close(() => process.exit(0));
}

async function resolveFilePath(url) {
  const pathname = new URL(url, "http://localhost:5173").pathname;
  const normalizedPath = path.normalize(decodeURIComponent(pathname));

  if (normalizedPath.startsWith("..")) {
    throw new Error("Invalid path.");
  }

  const assetPath = path.join(distRoot, normalizedPath);

  try {
    const stat = await fs.stat(assetPath);

    if (stat.isFile()) {
      return assetPath;
    }
  } catch {
    // Fall through to the app shell for client-side routes.
  }

  return path.join(distRoot, "index.html");
}

function getContentType(filePath) {
  if (filePath.endsWith(".css")) {
    return "text/css; charset=utf-8";
  }
  if (filePath.endsWith(".js")) {
    return "text/javascript; charset=utf-8";
  }
  if (filePath.endsWith(".html")) {
    return "text/html; charset=utf-8";
  }

  return "application/octet-stream";
}
