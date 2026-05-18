import './App.css'

const allInOneModules = [
  'Identity & Access Fabric',
  'AI Agent Orchestration',
  'Secure Data Graph',
  'Observability Command Center',
  'Policy & Compliance Guardrails',
  'Edge-to-Cloud Deploy Pipelines',
]

const miniOsModules = [
  'Boot Capsule',
  'Field Operations Panel',
  'Tactical Telemetry Stream',
  'Offline Sync Engine',
  'Encrypted Mission Vault',
  'Autonomous Recovery Layer',
]

const roadmapMilestones = [
  'Q2 2026 — OGX PRIME core platform launch',
  'Q3 2026 — THARA mission workspace and MiniOS kits',
  'Q4 2026 — multi-tenant ecosystem marketplace',
  'Q1 2027 — self-healing autonomous operations',
]

function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">OGX SYSTEMS</p>
        <h1>All-In-One.OS + MiniOS for THARA & OGX PRIME</h1>
        <p className="hero-copy">
          A diamond-crafted command platform engineered for sovereign operations, AI-native
          execution, and resilient scale.
        </p>
        <div className="hero-badges">
          <span>Premium Dark-Tech Interface</span>
          <span>Autonomous Operations</span>
          <span>Mission-Ready Security</span>
        </div>
      </section>

      <section className="section">
        <h2>Pillars</h2>
        <div className="grid grid-3">
          <article className="card">
            <h3>Intelligence</h3>
            <p>Decision systems with predictive insight and real-time situational awareness.</p>
          </article>
          <article className="card">
            <h3>Resilience</h3>
            <p>Zero-trust by default with encrypted pathways and graceful recovery patterns.</p>
          </article>
          <article className="card">
            <h3>Velocity</h3>
            <p>Composable pipelines that move from concept to deployment without friction.</p>
          </article>
        </div>
      </section>

      <section className="section">
        <h2>Platform Layers</h2>
        <div className="grid grid-2">
          <article className="card">
            <h3>Experience Layer</h3>
            <p>Unified portal, mission boards, and premium dashboard controls.</p>
          </article>
          <article className="card">
            <h3>Intelligence Layer</h3>
            <p>Agent meshes, policy engines, and forecasting intelligence loops.</p>
          </article>
          <article className="card">
            <h3>Core Systems Layer</h3>
            <p>Identity, data plane, event bus, and secure service orchestration.</p>
          </article>
          <article className="card">
            <h3>Infrastructure Layer</h3>
            <p>Edge nodes, cloud clusters, observability, and release automation.</p>
          </article>
        </div>
      </section>

      <section className="section">
        <h2>Operating Model</h2>
        <div className="grid grid-2">
          <article className="card">
            <h3>Strategic Command</h3>
            <p>Portfolio governance, compliance alignment, and executive intelligence.</p>
          </article>
          <article className="card">
            <h3>Autonomous Delivery</h3>
            <p>Agent-enabled operations with continuous verification and rollout controls.</p>
          </article>
        </div>
      </section>

      <section className="section">
        <h2>ALL-IN-ONE.OS Modules</h2>
        <ul className="module-list">
          {allInOneModules.map((module) => (
            <li key={module}>{module}</li>
          ))}
        </ul>
      </section>

      <section className="section">
        <h2>MiniOS Modules — THARA Edition</h2>
        <ul className="module-list">
          {miniOsModules.map((module) => (
            <li key={module}>{module}</li>
          ))}
        </ul>
      </section>

      <section className="section">
        <h2>Roadmap</h2>
        <ul className="roadmap">
          {roadmapMilestones.map((milestone) => (
            <li key={milestone}>{milestone}</li>
          ))}
        </ul>
      </section>

      <section className="section">
        <h2>Documentation Support</h2>
        <div className="grid grid-2">
          <article className="card">
            <h3>Architecture</h3>
            <p>See <code>docs/architecture.md</code> for platform topology and system contracts.</p>
          </article>
          <article className="card">
            <h3>Roadmap</h3>
            <p>See <code>docs/roadmap.md</code> for phased releases and module expansion goals.</p>
          </article>
        </div>
      </section>
    </main>
  )
}

export default App
