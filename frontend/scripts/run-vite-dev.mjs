import react from "@vitejs/plugin-react";
import { createServer } from "vite";

import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();

const server = await createServer({
  configFile: false,
  esbuild: false,
  optimizeDeps: {
    noDiscovery: true,
  },
  plugins: [typescriptTransformPlugin(), react()],
  root: process.cwd(),
  server: {
    host: "127.0.0.1",
    port: 5173,
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
