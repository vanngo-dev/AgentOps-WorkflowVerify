import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();
const { startVitest } = await import("vitest/node");
await startVitest(
  "test",
  ["src/tests/App.test.tsx"],
  {
    config: false,
    globals: true,
    environment: "jsdom",
    pool: "vmThreads",
    server: {
      deps: {
        inline: true,
      },
    },
    setupFiles: ["src/test/setup.ts"],
    watch: false,
  },
  {
    esbuild: false,
    plugins: [typescriptTransformPlugin()],
    ssr: {
      noExternal: true,
    },
  },
);
