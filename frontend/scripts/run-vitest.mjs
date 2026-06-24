import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();
const { startVitest } = await import("vitest/node");
await startVitest(
  "test",
  [],
  {
    config: false,
    globals: true,
    environment: "jsdom",
    include: ["src/tests/**/*.test.tsx"],
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
