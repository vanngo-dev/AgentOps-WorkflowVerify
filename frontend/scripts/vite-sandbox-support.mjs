import childProcess from "node:child_process";
import { syncBuiltinESMExports } from "node:module";
import ts from "typescript";

let patched = false;

export function patchWindowsNetworkDriveProbe() {
  if (patched) {
    return;
  }

  const originalExec = childProcess.exec;

  childProcess.exec = (command, options, callback) => {
    if (command === "net use") {
      const handler = typeof options === "function" ? options : callback;
      queueMicrotask(() => handler?.(null, "", ""));

      return {
        on() {
          return this;
        },
      };
    }

    return originalExec(command, options, callback);
  };

  syncBuiltinESMExports();
  patched = true;
}

export function typescriptTransformPlugin() {
  return {
    name: "agentops-typescript-transform",
    enforce: "pre",
    transform(code, id) {
      if (!/\.[cm]?[tj]sx?$/.test(id) || id.includes("node_modules")) {
        return null;
      }

      const result = ts.transpileModule(code, {
        compilerOptions: {
          jsx: ts.JsxEmit.ReactJSX,
          module: ts.ModuleKind.ESNext,
          target: ts.ScriptTarget.ES2020,
          useDefineForClassFields: true,
        },
        fileName: id,
      });

      return {
        code: replaceViteEnv(result.outputText),
        map: null,
      };
    },
  };
}

function replaceViteEnv(code) {
  const apiBaseUrl = process.env.VITE_API_BASE_URL ?? "http://localhost:8000";

  return code.replaceAll(
    "import.meta.env.VITE_API_BASE_URL",
    JSON.stringify(apiBaseUrl),
  );
}
