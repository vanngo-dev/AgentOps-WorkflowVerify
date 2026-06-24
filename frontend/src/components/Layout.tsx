import type { ReactNode } from "react";

import Navigation from "./Navigation";

type LayoutProps = {
  children: ReactNode;
  currentPath: string;
  onNavigate: (path: string) => void;
};

export default function Layout({
  children,
  currentPath,
  onNavigate,
}: LayoutProps) {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <p className="eyebrow">AgentOps</p>
          <h1>Workflow Verification</h1>
        </div>
        <Navigation currentPath={currentPath} onNavigate={onNavigate} />
      </header>
      <main className="content">{children}</main>
    </div>
  );
}
