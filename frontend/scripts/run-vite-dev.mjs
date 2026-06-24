import react from "@vitejs/plugin-react";
import { createServer, loadEnv } from "vite";

import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();

applyLoadedEnv("development");

const host = process.env.VITE_HOST ?? "127.0.0.1";
const port = Number(process.env.VITE_PORT ?? "5173");

const server = await createServer({
  configFile: false,
  esbuild: {
    exclude: /.*/,
    include: /\.agentops-no-esbuild$/,
  },
  optimizeDeps: {
    noDiscovery: true,
  },
  plugins: [typescriptTransformPlugin(), react()],
  root: process.cwd(),
  server: {
    host,
    port,
  },
});

await server.listen();
server.printUrls();

async function shutdown() {
  await server.close();
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

function applyLoadedEnv(mode) {
  const loadedEnv = loadEnv(mode, process.cwd(), "");

  for (const [key, value] of Object.entries(loadedEnv)) {
    process.env[key] ??= value;
  }
}
