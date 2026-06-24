import type { MouseEvent } from "react";

type NavigationProps = {
  currentPath: string;
  onNavigate: (path: string) => void;
};

const links = [
  { label: "Home", path: "/" },
  { label: "Workflow Runs", path: "/workflow-runs" },
];

export default function Navigation({
  currentPath,
  onNavigate,
}: NavigationProps) {
  function handleClick(event: MouseEvent<HTMLAnchorElement>, path: string) {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }

    event.preventDefault();
    onNavigate(path);
  }

  return (
    <nav aria-label="Primary navigation" className="navigation">
      {links.map((link) => {
        const isActive = currentPath === link.path;

        return (
          <a
            aria-current={isActive ? "page" : undefined}
            className={isActive ? "active" : undefined}
            href={link.path}
            key={link.path}
            onClick={(event) => handleClick(event, link.path)}
          >
            {link.label}
          </a>
        );
      })}
    </nav>
  );
}
