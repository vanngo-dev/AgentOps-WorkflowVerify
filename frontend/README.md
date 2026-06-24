# Frontend

This folder contains the Phase 07 React and TypeScript frontend shell.

Phase 07 creates the app foundation: Vite, React, TypeScript, routing, layout, navigation, placeholder pages, an API client placeholder, and frontend tests. It does not connect to backend data, build the workflow dashboard, build the trace viewer, add approval UI, or add Docker.

## Structure

```text
frontend/
  src/
    api/
      client.ts
    components/
      Layout.tsx
      Navigation.tsx
    pages/
      HomePage.tsx
      WorkflowRunsPage.tsx
    test/
      setup.ts
    tests/
      App.test.tsx
    App.tsx
    main.tsx
    styles.css
  index.html
  package.json
  tsconfig.json
  vite.config.ts
```

## Run

```sh
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Test

```sh
npm test
```
