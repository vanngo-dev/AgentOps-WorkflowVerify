# Phase 07 - Frontend Shell

## What We Build In This Phase

In Phase 07, we create the React and TypeScript frontend foundation.

We add:

- Vite
- React
- TypeScript
- routing
- a layout component
- navigation
- a Home page
- a Workflow Runs placeholder page
- an API client placeholder
- Vitest and React Testing Library tests

We do not connect to backend data yet. We do not build the workflow dashboard, trace viewer, approval UI, Docker setup, or Phase 08 features.

## Why This Phase Matters

The backend can now create, execute, validate, approve, and reject workflow runs. The next layer is the operator experience.

This phase gives the project a frontend home without rushing into dashboard behavior. The goal is to make the application shell stable before adding data fetching and workflow screens.

## Mental Model

Think of the frontend shell as the building frame.

The layout is the frame. Navigation is the hallway. Routes are the rooms. Pages are the first blank surfaces where real workflow information will appear later.

In this phase, the rooms exist, but they are not connected to live backend data.

## Files Added Or Changed

Added:

- `frontend/index.html`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/styles.css`
- `frontend/src/api/client.ts`
- `frontend/src/components/Layout.tsx`
- `frontend/src/components/Navigation.tsx`
- `frontend/src/pages/HomePage.tsx`
- `frontend/src/pages/WorkflowRunsPage.tsx`
- `frontend/src/test/setup.ts`
- `frontend/src/tests/App.test.tsx`
- `docs/07-frontend-shell.md`

Changed:

- `Makefile`
- `README.md`
- `frontend/README.md`

## Step-By-Step Walkthrough

First, we add Vite. Vite gives the frontend a fast development server and a standard build pipeline.

Next, we add React and TypeScript. React gives us components. TypeScript gives us type checking as the app grows.

Then, we add routing with a small browser-history route switch. The app has two routes:

- `/`
- `/workflow-runs`

After that, we create the layout and navigation components. The layout gives every page the same shell. Navigation lets users move between the Home page and the Workflow Runs placeholder.

Then, we add an API client placeholder. It does not call the backend yet. It simply marks where backend access will live in a later phase.

Finally, we add Vitest and React Testing Library tests for rendering and navigation.

## Key Code Concepts

React routes map URLs to platform screens. `/` maps to the Home page. `/workflow-runs` maps to the Workflow Runs placeholder.

A layout component wraps shared page structure around each route. In this phase, the layout owns the header, app title, navigation, and main content area.

Navigation gives users stable movement between routes. It also shows which route is active.

The API client is only a placeholder because Phase 07 is about the shell. Connecting backend data belongs to Phase 08.

Frontend tests verify the shell by rendering the app, finding navigation links, checking each page, and clicking from Home to Workflow Runs.

## How To Run It

From the frontend folder:

```sh
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## How To Test It

From the frontend folder:

```sh
npm test
```

From the backend folder:

```sh
python -m pytest
python -m ruff check .
```

## Manual Verification

Run:

```sh
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Verify:

- Home page loads
- Navigation is visible
- Workflow Runs link works
- `/workflow-runs` displays the placeholder page

Also verify the backend still passes:

```sh
cd backend
python -m pytest
python -m ruff check .
```

## Common Errors And Fixes

If `npm install` fails, confirm Node.js and npm are installed.

If the dev server port is busy, Vite may offer another port. Use the URL shown in the terminal.

If tests cannot find DOM matchers, check that `src/test/setup.ts` imports `@testing-library/jest-dom/vitest`.

If `/workflow-runs` shows a blank page, check that the route exists in `src/App.tsx` and that `src/main.tsx` renders the app into the root element.

If you expect backend data to appear, pause there. Backend data connection starts in a later phase.

## What We Now Understand

We now understand how the frontend shell is organized.

Routes define screens. Layout gives the app a consistent frame. Navigation moves between screens. Tests prove the shell renders and route navigation works.

## Next Phase Preview

Phase 08 can connect the Workflow Runs screen to backend data and start turning the placeholder into a real dashboard.

Phase 07 stops here. No backend data connection, workflow dashboard, trace viewer, approval UI, Docker, or Phase 08 work belongs in this phase.
