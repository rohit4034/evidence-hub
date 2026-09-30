import React, { useEffect, useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  FileSearch,
  FileText,
  Gauge,
  Layers3,
  Loader2,
  MessageSquareText,
  Play,
  Search,
  ShieldCheck,
  UploadCloud
} from "lucide-react";
import { Button } from "./components/ui/button";
import "./styles.css";

type Workspace = { workspace_id: string; name: string; data_use_policy: string };
type DocumentSummary = {
  document_id: string;
  workspace_id: string;
  latest_version_id: string;
  filename: string;
  content_type: string;
  status: string;
  created_at: string;
};
type Chunk = {
  chunk_id: string;
  document_id: string;
  document_version_id: string;
  workspace_id: string;
  content_hash: string;
  section_path: string[];
  page_number?: number;
  text: string;
};
type IndexPlan = {
  workspace_id: string;
  document_id: string;
  document_version_id: string;
  new_chunk_ids: string[];
  reused_chunk_ids: string[];
  chunks: Chunk[];
};
type RetrievalResult = { chunk_id: string; document_id: string; score: number; citation_label: string; text: string };
type RulePack = { id: string; name: string; jurisdiction: string; domain: string; obligations: { id: string; title: string }[] };
type Review = { review_id: string; workspace_id: string; rule_pack_id: string; applicable_obligation_ids: string[]; status: string };
type Finding = { finding_id: string; obligation_id: string; status: string; summary: string; citation_chunk_ids: string[] };
type RouteDecision = {
  selected_route: string;
  model_provider: string;
  model_name: string;
  model_config_version: string;
  prompt_version: string;
  reason: string;
};
type SupportResult = { ticket_id: string; category: string; priority: string; summary: string; draft_response: string };
type Job = { job_id: string; queue: string; status: string; workspace_id: string };
type AIChatResponse = { answer: string; confidence: number; evidence_chunk_ids: string[]; model: string; model_route: string; model_config_version: string; prompt_version: string };

type RunLog = { label: string; status: "done" | "error"; detail: string };

const exampleEvidence = `Security governance is owned by the CISO and reviewed quarterly by the risk committee.

Access to production systems requires SSO, MFA, and manager approval. Access reviews are performed every quarter.

Application and infrastructure logs are retained in the SIEM for 180 days and reviewed during security incidents.

The incident response process requires legal, security, and communications review for reportable security events.`;

const api = async <T,>(path: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(options?.headers ?? {})
    }
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
};

function App() {
  const [workspaceName, setWorkspaceName] = useState("Acme Security Review");
  const [filename, setFilename] = useState("security-policy.md");
  const [evidenceText, setEvidenceText] = useState(exampleEvidence);
  const [query, setQuery] = useState("security governance logs retained");
  const [ticketSubject, setTicketSubject] = useState("Customer reports security incident export request");
  const [ticketBody, setTicketBody] = useState("The customer needs incident evidence, export status, and privacy review details.");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<RunLog[]>([]);

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [document, setDocument] = useState<DocumentSummary | null>(null);
  const [indexPlan, setIndexPlan] = useState<IndexPlan | null>(null);
  const [results, setResults] = useState<RetrievalResult[]>([]);
  const [rulePacks, setRulePacks] = useState<RulePack[]>([]);
  const [review, setReview] = useState<Review | null>(null);
  const [finding, setFinding] = useState<Finding | null>(null);
  const [route, setRoute] = useState<RouteDecision | null>(null);
  const [aiSummary, setAiSummary] = useState<AIChatResponse | null>(null);
  const [support, setSupport] = useState<SupportResult | null>(null);
  const [job, setJob] = useState<Job | null>(null);

  const selectedRulePack = useMemo(
    () => rulePacks.find((pack) => pack.id === "general-cybersecurity-baseline") ?? rulePacks[0],
    [rulePacks]
  );
  const firstObligation = selectedRulePack?.obligations[0];

  useEffect(() => {
    api<RulePack[]>("/compliance/rule-packs")
      .then(setRulePacks)
      .catch((err: Error) => setError(err.message));
  }, []);

  const addLog = (entry: RunLog) => setLogs((current) => [entry, ...current].slice(0, 8));

  async function runStep<T>(key: string, label: string, action: () => Promise<T>, detail: (result: T) => string) {
    setBusy(key);
    setError(null);
    try {
      const result = await action();
      addLog({ label, status: "done", detail: detail(result) });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      addLog({ label, status: "error", detail: message });
      throw err;
    } finally {
      setBusy(null);
    }
  }

  const ensureWorkspace = async () => {
    if (workspace) return workspace;
    const created = await api<Workspace>("/evidence/workspaces", {
      method: "POST",
      body: JSON.stringify({ name: workspaceName, data_use_policy: "customer_private" })
    });
    setWorkspace(created);
    return created;
  };

  const ensureDocument = async () => {
    const ws = await ensureWorkspace();
    if (document) return document;
    const created = await api<DocumentSummary>("/evidence/documents", {
      method: "POST",
      body: JSON.stringify({ workspace_id: ws.workspace_id, filename, content_type: "text/markdown", document_type: "policy" })
    });
    setDocument(created);
    return created;
  };

  const createWorkspace = () =>
    runStep("workspace", "Workspace created", ensureWorkspace, (created) => created.workspace_id);

  const registerDocument = () =>
    runStep("document", "Document registered", ensureDocument, (created) => created.document_id);

  const chunkEvidence = () =>
    runStep(
      "chunks",
      "Evidence indexed",
      async () => {
        const ws = await ensureWorkspace();
        const doc = await ensureDocument();
        const plan = await api<IndexPlan>("/evidence/chunks/preview", {
          method: "POST",
          body: JSON.stringify({
            workspace_id: ws.workspace_id,
            document_id: doc.document_id,
            document_version_id: doc.latest_version_id,
            text: evidenceText,
            section_path: ["Security policy"]
          })
        });
        setIndexPlan(plan);
        return plan;
      },
      (plan) => `${plan.new_chunk_ids.length} new, ${plan.reused_chunk_ids.length} reused`
    );

  const searchEvidence = () =>
    runStep(
      "search",
      "Evidence searched",
      async () => {
        const ws = await ensureWorkspace();
        if (!indexPlan) await chunkEvidence();
        const found = await api<RetrievalResult[]>("/evidence/retrieval/search", {
          method: "POST",
          body: JSON.stringify({ workspace_id: ws.workspace_id, query, limit: 5 })
        });
        setResults(found);
        return found;
      },
      (found) => `${found.length} cited chunks`
    );

  const routeAiTask = () =>
    runStep(
      "route",
      "AI task routed",
      async () => {
        const decision = await api<RouteDecision>("/ai/route", {
          method: "POST",
          body: JSON.stringify({ task_type: "compliance_gap_analysis", risk: "high", input_token_estimate: evidenceText.length / 4 })
        });
        setRoute(decision);
        return decision;
      },
      (decision) => `${decision.selected_route} -> ${decision.model_name}`
    );


  const generateAiSummary = () =>
    runStep(
      "ai-chat",
      "AI summary generated",
      async () => {
        const ws = await ensureWorkspace();
        const found = results.length ? results : await searchEvidence();
        const citationText = found.map((item) => `[${item.chunk_id}] ${item.text}`).join("\n\n");
        const summary = await api<AIChatResponse>("/ai/chat", {
          method: "POST",
          body: JSON.stringify({
            workspace_id: ws.workspace_id,
            task_type: "compliance_gap_analysis",
            risk: "high",
            input_token_estimate: Math.ceil((citationText.length + query.length) / 4),
            evidence_chunk_ids: found.map((item) => item.chunk_id),
            prompt: `Draft a concise compliance finding for this question: ${query}\n\nEvidence:\n${citationText}`
          })
        });
        setAiSummary(summary);
        return summary;
      },
      (summary) => `${summary.model_route} / ${Math.round(summary.confidence * 100)}% confidence`
    );

  const createReview = () =>
    runStep(
      "review",
      "Compliance review created",
      async () => {
        const ws = await ensureWorkspace();
        const pack = selectedRulePack;
        if (!pack) throw new Error("Rule packs are still loading");
        const created = await api<Review>("/compliance/reviews", {
          method: "POST",
          body: JSON.stringify({ workspace_id: ws.workspace_id, rule_pack_id: pack.id, answers: { handles_sensitive_data: true } })
        });
        setReview(created);
        return created;
      },
      (created) => `${created.applicable_obligation_ids.length} applicable obligations`
    );

  const draftFinding = () =>
    runStep(
      "finding",
      "Finding drafted",
      async () => {
        const activeReview = review ?? (await createReview());
        const found = results.length ? results : await searchEvidence();
        const obligationId = activeReview.applicable_obligation_ids[0] ?? firstObligation?.id;
        if (!obligationId) throw new Error("No obligation available");
        const drafted = await api<Finding>("/compliance/findings/draft", {
          method: "POST",
          body: JSON.stringify({
            review_id: activeReview.review_id,
            obligation_id: obligationId,
            candidate_chunk_ids: found.map((item) => item.chunk_id)
          })
        });
        setFinding(drafted);
        return drafted;
      },
      (drafted) => `${drafted.status} with ${drafted.citation_chunk_ids.length} citations`
    );

  const triageTicket = () =>
    runStep(
      "support",
      "Support ticket triaged",
      async () => {
        const ws = await ensureWorkspace();
        const triaged = await api<SupportResult>("/support/triage", {
          method: "POST",
          body: JSON.stringify({
            workspace_id: ws.workspace_id,
            external_id: "ticket-1001",
            subject: ticketSubject,
            body: ticketBody,
            source: "manual"
          })
        });
        setSupport(triaged);
        return triaged;
      },
      (triaged) => `${triaged.category}, ${triaged.priority}`
    );

  const enqueueJob = () =>
    runStep(
      "job",
      "Worker job queued",
      async () => {
        const ws = await ensureWorkspace();
        const queued = await api<Job>("/jobs", {
          method: "POST",
          body: JSON.stringify({ queue: "review_generation", workspace_id: ws.workspace_id, payload: { review_id: review?.review_id } })
        });
        setJob(queued);
        return queued;
      },
      (queued) => `${queued.queue}: ${queued.status}`
    );

  const runDemo = async () => {
    await createWorkspace();
    await registerDocument();
    await chunkEvidence();
    await searchEvidence();
    await routeAiTask();
    await generateAiSummary();
    await createReview();
    await draftFinding();
    await triageTicket();
    await enqueueJob();
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><BrainCircuit size={22} /></div>
          <div><strong>Evidence Hub</strong><span>Working review desk</span></div>
        </div>
        <nav aria-label="Primary">
          {[Gauge, UploadCloud, Search, ShieldCheck, BrainCircuit, MessageSquareText, Activity].map((Icon, index) => (
            <button className={index === 0 ? "nav-button active" : "nav-button"} key={index} title="Workbench">
              <Icon size={18} /><span>{["Workbench", "Evidence", "Retrieval", "Compliance", "AI Route", "Support", "Jobs"][index]}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">Live vertical slice</p>
            <h1>Run an evidence-backed compliance review</h1>
          </div>
          <Button icon={busy ? <Loader2 className="spin" size={18} /> : <Play size={18} />} onClick={runDemo}>
            Run Demo
          </Button>
        </header>

        {error && <div className="alert">{error}</div>}

        <section className="metrics-grid" aria-label="Run status">
          <Metric label="Workspace" value={workspace ? "Ready" : "New"} detail={workspace?.workspace_id ?? "not created"} />
          <Metric label="Chunks" value={String(indexPlan?.chunks.length ?? 0)} detail={`${indexPlan?.new_chunk_ids.length ?? 0} new`} />
          <Metric label="Citations" value={String(results.length)} detail={finding?.status ?? "not drafted"} />
          <Metric label="AI Route" value={route?.selected_route ?? aiSummary?.model_route ?? "Pending"} detail={route?.model_provider ?? aiSummary?.model ?? "internal only"} />
        </section>

        <section className="workbench-grid">
          <Panel title="1. Workspace" eyebrow="Evidence Desk" icon={<Layers3 size={18} />} action="Create" busy={busy === "workspace"} onAction={createWorkspace}>
            <label>Workspace name<input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} /></label>
            <ResultLine label="Workspace ID" value={workspace?.workspace_id} />
          </Panel>

          <Panel title="2. Evidence" eyebrow="Document intake" icon={<FileText size={18} />} action="Register + Chunk" busy={busy === "chunks" || busy === "document"} onAction={chunkEvidence}>
            <label>Filename<input value={filename} onChange={(event) => setFilename(event.target.value)} /></label>
            <label>Evidence text<textarea value={evidenceText} onChange={(event) => setEvidenceText(event.target.value)} /></label>
            <ResultLine label="Document" value={document?.document_id} />
          </Panel>

          <Panel title="3. Retrieval" eyebrow="Cited search" icon={<FileSearch size={18} />} action="Search" busy={busy === "search"} onAction={searchEvidence}>
            <label>Query<input value={query} onChange={(event) => setQuery(event.target.value)} /></label>
            <div className="result-list">
              {results.map((item) => <Citation key={item.chunk_id} item={item} />)}
              {!results.length && <EmptyState text="Search results will appear here." />}
            </div>
          </Panel>

          <Panel title="4. AI Summary" eyebrow="NVIDIA NIM via AI service" icon={<BrainCircuit size={18} />} action="Generate" busy={busy === "route" || busy === "ai-chat"} onAction={async () => { await routeAiTask(); await generateAiSummary(); }}>
            <ResultLine label="Selected route" value={route?.selected_route ?? aiSummary?.model_route} />
            <ResultLine label="Model" value={route?.model_name ?? aiSummary?.model} />
            <ResultLine label="Summary" value={aiSummary?.answer} />
          </Panel>

          <Panel title="5. Compliance" eyebrow={selectedRulePack?.name ?? "Rule pack"} icon={<ClipboardCheck size={18} />} action="Review + Finding" busy={busy === "review" || busy === "finding"} onAction={draftFinding}>
            <ResultLine label="Review" value={review?.review_id} />
            <ResultLine label="Obligation" value={review?.applicable_obligation_ids[0] ?? firstObligation?.id} />
            <ResultLine label="Finding" value={finding ? `${finding.status}: ${finding.summary}` : undefined} />
          </Panel>

          <Panel title="6. Support + Worker" eyebrow="Operational loop" icon={<MessageSquareText size={18} />} action="Triage + Queue" busy={busy === "support" || busy === "job"} onAction={async () => { await triageTicket(); await enqueueJob(); }}>
            <label>Ticket subject<input value={ticketSubject} onChange={(event) => setTicketSubject(event.target.value)} /></label>
            <label>Ticket body<textarea value={ticketBody} onChange={(event) => setTicketBody(event.target.value)} /></label>
            <ResultLine label="Triage" value={support ? `${support.category} / ${support.priority}` : undefined} />
            <ResultLine label="Job" value={job ? `${job.job_id} (${job.status})` : undefined} />
          </Panel>
        </section>

        <section className="activity-panel">
          <div className="section-title"><div><p className="eyebrow">Run log</p><h2>Recent actions</h2></div></div>
          <div className="timeline">
            {logs.map((log, index) => (
              <div className="timeline-row" key={`${log.label}-${index}`}>
                {log.status === "done" ? <CheckCircle2 size={17} /> : <Activity size={17} />}
                <strong>{log.label}</strong><span>{log.detail}</span>
              </div>
            ))}
            {!logs.length && <EmptyState text="Run the demo or any individual step." />}
          </div>
        </section>
      </main>
    </div>
  );
}

function Panel({ title, eyebrow, icon, action, busy, onAction, children }: { title: string; eyebrow: string; icon: React.ReactNode; action: string; busy: boolean; onAction: () => unknown | Promise<unknown>; children: React.ReactNode }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div className="panel-title"><span>{icon}</span><div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div></div>
        <button className="icon-action" onClick={() => void onAction()} disabled={busy} title={action}>
          {busy ? <Loader2 className="spin" size={17} /> : <ArrowRight size={17} />}
        </button>
      </div>
      <div className="panel-body">{children}</div>
    </section>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article className="metric"><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function ResultLine({ label, value }: { label: string; value?: string }) {
  return <div className="result-line"><span>{label}</span><strong>{value ?? "Pending"}</strong></div>;
}

function Citation({ item }: { item: RetrievalResult }) {
  return <article className="citation"><strong>{item.citation_label}</strong><p>{item.text}</p><code>{item.chunk_id}</code></article>;
}

function EmptyState({ text }: { text: string }) {
  return <p className="empty-state">{text}</p>;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode><App /></React.StrictMode>
);
