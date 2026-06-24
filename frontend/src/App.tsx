import { useCallback, useEffect, useState } from "react";

import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import WorkflowRunDetailPage from "./pages/WorkflowRunDetailPage";
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

  const workflowRunDetailMatch = currentPath.match(/^\/workflow-runs\/(\d+)$/);
  const page = workflowRunDetailMatch ? (
    <WorkflowRunDetailPage
      workflowRunId={Number(workflowRunDetailMatch[1])}
      onNavigate={handleNavigate}
    />
  ) : currentPath === "/workflow-runs" ? (
    <WorkflowRunsPage onNavigate={handleNavigate} />
  ) : (
    <HomePage />
  );

  return (
    <Layout currentPath={currentPath} onNavigate={handleNavigate}>
      {page}
    </Layout>
  );
}
