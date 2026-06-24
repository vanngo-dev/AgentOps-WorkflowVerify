export default function HomePage() {
  return (
    <section className="page-grid" aria-labelledby="home-title">
      <div className="page-heading">
        <p className="eyebrow">Phase 07</p>
        <h2 id="home-title">Frontend Shell</h2>
        <p>
          A quiet starting point for the operator screens that will arrive in
          later phases.
        </p>
      </div>
      <div className="status-list" aria-label="Frontend shell status">
        <article>
          <span>Routing</span>
          <strong>Ready</strong>
        </article>
        <article>
          <span>Backend Data</span>
          <strong>Pending</strong>
        </article>
        <article>
          <span>Review UI</span>
          <strong>Pending</strong>
        </article>
      </div>
    </section>
  );
}
