import react from "@vitejs/plugin-react";
import { build } from "vite";

import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();

await build({
  build: {
    emptyOutDir: true,
    minify: false,
    outDir: "dist",
  },
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
});
