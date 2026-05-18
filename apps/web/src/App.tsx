import './App.css'

const pillars = [
  {
    title: 'Authority',
    description:
      'Executive-grade positioning, decisive messaging, and a visual system built to signal control.',
  },
  {
    title: 'Modernity',
    description:
      'A refined dark-tech interface with motion, spacing, and hierarchy tuned for premium perception.',
  },
  {
    title: 'Clarity',
    description:
      'A narrative that explains what OGX Systems does, who it serves, and why it wins without noise.',
  },
  {
    title: 'Depth',
    description:
      'Signals of real operations: modules, workflows, monitoring, governance, and implementation layers.',
  },
  {
    title: 'Scalability',
    description:
      'A foundation ready to expand into portals, agents, internal tools, and future systems.',
  },
]

const platformLayers = [
  {
    name: 'Brand Surface',
    summary: 'Landing, company narrative, offers, and executive trust signals.',
  },
  {
    name: 'Control Layer',
    summary: 'Dashboards, workflow consoles, operator views, and system health summaries.',
  },
  {
    name: 'Automation Layer',
    summary: 'Agent orchestration, process chains, event triggers, and execution pathways.',
  },
  {
    name: 'Trust Layer',
    summary: 'Security posture, observability, release discipline, and operational standards.',
  },
]

const operatingModel = [
  'Define the OGX promise, narrative, and visual operating language.',
  'Launch a premium web presence with credible system architecture.',
  'Extend into internal operations, dashboards, and autonomous workflows.',
  'Scale into a multi-surface platform without breaking brand consistency.',
]

const roadmap = [
  {
    phase: 'Phase 01',
    title: 'Signal the brand',
    detail:
      'Deploy a homepage that feels deliberate, premium, and enterprise-ready from the first screen.',
  },
  {
    phase: 'Phase 02',
    title: 'Document the machine',
    detail:
      'Add architecture, governance, and roadmap documentation so the repository looks operational.',
  },
  {
    phase: 'Phase 03',
    title: 'Scale the surfaces',
    detail:
      'Introduce admin, client, and automation modules without diluting the OGX identity.',
  },
]

function App() {
  return (
    <div className="page-shell">
      <header className="topbar">
        <a className="brand" href="#hero" aria-label="OGX Systems home">
          <span className="brand-mark" aria-hidden="true">
            OGX
          </span>
          <span className="brand-copy">
            <strong>OGX Systems</strong>
            <span>Core infrastructure for the OGX empire.</span>
          </span>
        </a>

        <nav className="nav" aria-label="Primary">
          <a href="#pillars">Pillars</a>
          <a href="#platform">Platform</a>
          <a href="#architecture">Architecture</a>
          <a href="#roadmap">Roadmap</a>
        </nav>
      </header>

      <main>
        <section className="hero section" id="hero">
          <div className="hero-copy">
            <p className="eyebrow">Designed to look like a machine, not a template.</p>
            <h1>OGX Systems now has a premium digital foundation instead of an empty shell.</h1>
            <p className="lede">
              This implementation turns the repository into a credible launchpad for a branded web
              experience, future operations tooling, and the documentation needed to support both.
            </p>

            <div className="hero-actions">
              <a className="button button-primary" href="#platform">
                Explore the platform
              </a>
              <a className="button button-secondary" href="#documentation">
                Review the documentation
              </a>
            </div>
          </div>

          <div className="hero-panel" aria-label="OGX Systems overview">
            <div className="panel-grid">
              <article>
                <span>Presence</span>
                <strong>Corporate landing</strong>
                <p>High-authority messaging and premium visual language.</p>
              </article>
              <article>
                <span>Systems</span>
                <strong>Operational layers</strong>
                <p>Workflows, monitoring, governance, and execution-ready scaffolding.</p>
              </article>
              <article>
                <span>Trust</span>
                <strong>Documentation</strong>
                <p>Architecture and roadmap assets that make the repo feel intentional.</p>
              </article>
              <article>
                <span>Scale</span>
                <strong>Extensible base</strong>
                <p>Built to grow into internal tools, portals, and automation surfaces.</p>
              </article>
            </div>
          </div>
        </section>

        <section className="section" id="pillars">
          <div className="section-heading">
            <p className="eyebrow">Perception strategy</p>
            <h2>The five pillars behind the OGX Systems image.</h2>
          </div>
          <div className="card-grid pillars-grid">
            {pillars.map((pillar) => (
              <article className="card" key={pillar.title}>
                <p className="card-kicker">{pillar.title}</p>
                <p>{pillar.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section" id="platform">
          <div className="section-heading">
            <p className="eyebrow">Platform structure</p>
            <h2>One repository, organized to support brand, control, automation, and trust.</h2>
          </div>
          <div className="card-grid">
            {platformLayers.map((layer) => (
              <article className="card" key={layer.name}>
                <p className="card-kicker">{layer.name}</p>
                <p>{layer.summary}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section architecture" id="architecture">
          <div className="section-heading">
            <p className="eyebrow">Operating model</p>
            <h2>How OGX Systems grows from identity to platform.</h2>
          </div>
          <div className="architecture-layout">
            <div className="architecture-steps">
              {operatingModel.map((step) => (
                <article className="timeline-step" key={step}>
                  <span className="timeline-marker" aria-hidden="true" />
                  <p>{step}</p>
                </article>
              ))}
            </div>

            <aside className="architecture-note">
              <p className="card-kicker">Current implementation</p>
              <p>
                This repository now includes a premium frontend foundation, project documentation,
                and root-level workflow commands so future OGX systems can plug into a coherent
                structure.
              </p>
            </aside>
          </div>
        </section>

        <section className="section" id="roadmap">
          <div className="section-heading">
            <p className="eyebrow">Execution roadmap</p>
            <h2>The next moves are already framed for expansion.</h2>
          </div>
          <div className="roadmap-grid">
            {roadmap.map((item) => (
              <article className="roadmap-card" key={item.phase}>
                <p className="card-kicker">{item.phase}</p>
                <h3>{item.title}</h3>
                <p>{item.detail}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section documentation" id="documentation">
          <div className="section-heading">
            <p className="eyebrow">Repository support</p>
            <h2>Documentation has been added so the codebase feels built, not imagined.</h2>
          </div>
          <div className="card-grid docs-grid">
            <article className="card">
              <p className="card-kicker">README</p>
              <p>Repository narrative, structure, and commands for local development.</p>
            </article>
            <article className="card">
              <p className="card-kicker">Architecture</p>
              <p>Target structure for brand surfaces, systems, and governance layers.</p>
            </article>
            <article className="card">
              <p className="card-kicker">Roadmap</p>
              <p>Delivery priorities for expanding this foundation into a full OGX platform.</p>
            </article>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
