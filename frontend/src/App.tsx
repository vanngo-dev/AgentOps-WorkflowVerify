import { useCallback, useEffect, useState } from "react";

import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import WorkflowRunsPage from "./pages/WorkflowRunsPage";

function getCurrentPath() {
  if (typeof window === "undefined") {
    return "/";
  }

  return window.location.pathname || "/";
}

export default function App() {
  const [currentPath, setCurrentPath] = useState(getCurrentPath);

  useEffect(() => {
    function handlePopState() {
      setCurrentPath(getCurrentPath());
    }

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  const handleNavigate = useCallback(
    (nextPath: string) => {
      if (nextPath !== currentPath) {
        window.history.pushState({}, "", nextPath);
      }

      setCurrentPath(nextPath);
    },
    [currentPath],
  );

  const page =
    currentPath === "/workflow-runs" ? <WorkflowRunsPage /> : <HomePage />;

  return (
    <Layout currentPath={currentPath} onNavigate={handleNavigate}>
      {page}
    </Layout>
  );
}
