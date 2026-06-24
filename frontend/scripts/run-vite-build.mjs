import fs from "node:fs/promises";
import path from "node:path";

import commonjs from "@rollup/plugin-commonjs";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import { rollup } from "rollup";

import {
  patchWindowsNetworkDriveProbe,
  typescriptTransformPlugin,
} from "./vite-sandbox-support.mjs";

patchWindowsNetworkDriveProbe();

const root = process.cwd();
const outDir = path.join(root, "dist");
const assetsDir = path.join(outDir, "assets");
const nodeEnv = process.env.NODE_ENV ?? "production";
const apiBaseUrl = process.env.VITE_API_BASE_URL ?? "http://localhost:8000";

await fs.rm(outDir, { force: true, recursive: true });
await fs.mkdir(assetsDir, { recursive: true });

const bundle = await rollup({
  input: path.join(root, "src/main.tsx"),
  plugins: [
    environmentReplacePlugin(),
    typescriptTransformPlugin(),
    cssAssetPlugin(),
    nodeResolve({
      browser: true,
      extensions: [".mjs", ".js", ".json", ".ts", ".tsx"],
    }),
    commonjs({
      transformMixedEsModules: true,
    }),
  ],
});

await bundle.write({
  chunkFileNames: "[name]-[hash].js",
  dir: assetsDir,
  entryFileNames: "main.js",
  format: "esm",
});
await bundle.close();

const html = await fs.readFile(path.join(root, "index.html"), "utf8");
const builtHtml = html.replace(
  '    <script type="module" src="/src/main.tsx"></script>',
  [
    '    <link rel="stylesheet" href="/assets/styles.css" />',
    '    <script type="module" src="/assets/main.js"></script>',
  ].join("\n"),
);

await fs.writeFile(path.join(outDir, "index.html"), builtHtml);

function cssAssetPlugin() {
  const cssAssets = new Map();

  return {
    name: "agentops-css-asset",
    async load(id) {
      if (!id.endsWith(".css")) {
        return null;
      }

      cssAssets.set(path.basename(id), await fs.readFile(id, "utf8"));
      return "";
    },
    generateBundle() {
      for (const [fileName, source] of cssAssets) {
        this.emitFile({
          fileName,
          source,
          type: "asset",
        });
      }
    },
  };
}

function environmentReplacePlugin() {
  return {
    name: "agentops-environment-replace",
    transform(code, id) {
      if (!/\.[cm]?[jt]sx?$/.test(id)) {
        return null;
      }

      const nextCode = code
        .replaceAll("process.env.NODE_ENV", JSON.stringify(nodeEnv))
        .replaceAll(
          "import.meta.env.VITE_API_BASE_URL",
          JSON.stringify(apiBaseUrl),
        );

      if (nextCode === code) {
        return null;
      }

      return {
        code: nextCode,
        map: null,
      };
    },
  };
}
