import React from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  Archive,
  Boxes,
  BrainCircuit,
  ClipboardCheck,
  FileText,
  Gauge,
  Library,
  MessageSquareText,
  Settings,
  ShieldCheck,
  UploadCloud
} from "lucide-react";
import { Button } from "./components/ui/button";
import "./styles.css";

type ServiceState = "ready" | "planned" | "attention";

type ServiceCard = {
  name: string;
  port: string;
  status: ServiceState;
  description: string;
};

type NavItem = {
  label: string;
  icon: React.ElementType;
};

const navItems: NavItem[] = [
  { label: "Dashboard", icon: Gauge },
  { label: "Evidence Desk", icon: Archive },
  { label: "Documents", icon: FileText },
  { label: "Compliance Desk", icon: ShieldCheck },
  { label: "Rule Packs", icon: Library },
  { label: "Review Detail", icon: ClipboardCheck },
  { label: "Findings", icon: Activity },
  { label: "Reports", icon: Boxes },
  { label: "Support Triage", icon: MessageSquareText },
  { label: "Settings", icon: Settings }
];

const services: ServiceCard[] = [
  {
    name: "API Gateway",
    port: "8000",
    status: "ready",
    description: "North-south boundary for the web app and service directory."
  },
  {
    name: "AI Service",
    port: "8001",
    status: "ready",
    description: "Runtime model routing, safe admin schema, and provider boundary."
  },
  {
    name: "Evidence Service",
    port: "8002",
    status: "ready",
    description: "Document and evidence ingestion boundary for Phase 2."
  },
  {
    name: "Compliance Service",
    port: "8003",
    status: "ready",
    description: "Rule packs, reviews, findings, and report workflow boundary."
  },
  {
    name: "Support Service",
    port: "8004",
    status: "planned",
    description: "Ticket import, classification, clustering, and draft replies."
  },
  {
    name: "Worker Service",
    port: "8005",
    status: "ready",
    description: "Background jobs for ingestion, embeddings, rerank, and exports."
  }
];

const workflow = [
  "Create workspace",
  "Select rule pack",
  "Answer applicability",
  "Upload evidence",
  "Index incrementally",
  "Map evidence",
  "Validate citations",
  "Human review",
  "Generate report"
];

function App() {
  return (
    <div className="app-shell bg-slate-50 text-slate-900">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <BrainCircuit size={22} />
          </div>
          <div>
            <strong>Evidence Hub</strong>
            <span>Phase 1 Foundation</span>
          </div>
        </div>
        <nav aria-label="Primary">
          {navItems.map((item) => (
            <button className="nav-button" key={item.label} title={item.label}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operational workspace</p>
            <h1>Evidence-backed compliance and document intelligence</h1>
          </div>
          <Button icon={<UploadCloud size={18} />}>Upload Evidence</Button>
        </header>

        <section className="metrics-grid" aria-label="Foundation metrics">
          <Metric label="Services" value="6" detail="FastAPI templates" />
          <Metric label="Health checks" value="100%" detail="Compose wired" />
          <Metric label="Model routes" value="9" detail="Admin-safe schema" />
          <Metric label="Data policy" value="Private" detail="Opt-in by design" />
        </section>

        <section className="workspace-grid">
          <div className="panel evidence-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Evidence Desk</p>
                <h2>Document foundation</h2>
              </div>
              <span className="status ready">Ready</span>
            </div>
            <div className="dropzone">
              <UploadCloud size={26} />
              <div>
                <strong>Upload surface reserved</strong>
                <span>PDF, text, markdown, CSV, images, and scanned evidence enter here in Phase 2.</span>
              </div>
            </div>
            <div className="evidence-list">
              <EvidenceRow name="Security policy.pdf" type="Policy" state="Waiting for parser" />
              <EvidenceRow name="Vendor inventory.csv" type="CSV" state="Schema ready" />
              <EvidenceRow name="Incident screenshot.png" type="Image" state="Vision route ready" />
            </div>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Compliance Desk</p>
                <h2>Review workflow</h2>
              </div>
              <span className="status ready">Schema</span>
            </div>
            <ol className="workflow">
              {workflow.map((step, index) => (
                <li key={step}>
                  <span>{index + 1}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="service-band">
          <div className="section-title">
            <p className="eyebrow">Runtime architecture</p>
            <h2>Service boundaries</h2>
          </div>
          <div className="service-grid">
            {services.map((service) => (
              <article className="service-card" key={service.name}>
                <div className="service-card-title">
                  <strong>{service.name}</strong>
                  <span className={`status ${service.status}`}>{service.status}</span>
                </div>
                <p>{service.description}</p>
                <code>localhost:{service.port}</code>
              </article>
            ))}
          </div>
        </section>

        <section className="model-panel">
          <div className="section-title">
            <p className="eyebrow">AI Service</p>
            <h2>Configurable model routes</h2>
          </div>
          <div className="route-grid">
            {[
              "small_reasoning",
              "large_reasoning",
              "embedding",
              "rerank",
              "vision_language",
              "vision_detection",
              "classification",
              "extraction",
              "reporting"
            ].map((route) => (
              <span key={route}>{route}</span>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function EvidenceRow({ name, type, state }: { name: string; type: string; state: string }) {
  return (
    <div className="evidence-row">
      <FileText size={18} />
      <div>
        <strong>{name}</strong>
        <span>{type}</span>
      </div>
      <small>{state}</small>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

