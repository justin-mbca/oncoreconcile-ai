import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import "./style.css";

const configuredApi = import.meta.env.VITE_API_BASE_URL;
const currentHostApi = `${window.location.protocol}//${window.location.hostname || "127.0.0.1"}:8000`;
const API_CANDIDATES = Array.from(new Set([
  configuredApi,
  currentHostApi,
  "http://127.0.0.1:8000",
  "http://localhost:8000",
].filter(Boolean)));

async function apiFetch(path, options = {}) {
  let lastError;
  for (const baseUrl of API_CANDIDATES) {
    try {
      const response = await fetch(`${baseUrl}${path}`, options);
      window.__ONCORECONCILE_API_BASE__ = baseUrl;
      return response;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("Backend API is not reachable.");
}

// ── Colours ──────────────────────────────────────────────────────────────────
const STATUS_COLOR = { AUTO_RECONCILE:"#1a7f37", REVIEW_REQUIRED:"#9a6700", CANNOT_RECONCILE:"#cf222e" };
const CONF_COLOR   = { HIGH:"#1a7f37", MEDIUM:"#9a6700", LOW:"#cf222e" };

// ── Shared components ─────────────────────────────────────────────────────────
function Badge({ label, color }) {
  return <span style={{ background:color, color:"#fff", borderRadius:4, padding:"2px 10px", fontSize:13, fontWeight:"bold" }}>{label}</span>;
}

function ScoreBar({ label, value }) {
  const pct = Math.round((value || 0) * 100);
  const col = pct >= 75 ? "#1a7f37" : pct >= 45 ? "#9a6700" : "#cf222e";
  return (
    <div style={{ marginBottom:6 }}>
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:2 }}>
        <span style={{ color:"#444" }}>{label}</span>
        <span style={{ fontWeight:"bold", color:col }}>{pct}%</span>
      </div>
      <div style={{ background:"#eee", borderRadius:4, height:8 }}>
        <div style={{ background:col, width:`${pct}%`, borderRadius:4, height:8, transition:"width 0.4s" }}/>
      </div>
    </div>
  );
}

function EvidenceList({ evidence }) {
  if (!evidence?.length) return <p style={{ color:"#888" }}>No evidence.</p>;
  return (
    <ul style={{ paddingLeft:16, margin:0 }}>
      {evidence.map((e,i) => (
        <li key={i} style={{ marginBottom:6, fontSize:13 }}>
          <strong>{e.type}</strong> — {e.description}
          <span style={{ color:"#888", fontSize:11 }}> [{e.source}]</span>
          {(e.evidence_type || e.confidence_weight || e.governance_standard) && (
            <div style={{ color:"#777", fontSize:11, marginTop:2 }}>
              {e.evidence_type && <span>{e.evidence_type}</span>}
              {e.confidence_weight && <span> · {e.confidence_weight}</span>}
              {e.governance_standard && <span> · {e.governance_standard}</span>}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}

function ResultCard({ result }) {
  const [expanded, setExpanded] = useState(false);
  if (!result) return null;
  const { canonical, confidence, confidence_score, score_breakdown, review_status, explanation, evidence, alternatives, notes, audit_trail } = result;
  return (
    <div style={{ border:"1px solid #ddd", borderRadius:8, padding:16, background:"#fafafa", marginTop:12 }}>
      <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:10, flexWrap:"wrap" }}>
        <Badge label={review_status} color={STATUS_COLOR[review_status]}/>
        <Badge label={confidence} color={CONF_COLOR[confidence]}/>
        <span style={{ fontSize:13, color:"#555" }}>Score: <strong>{(confidence_score*100).toFixed(0)}%</strong></span>
      </div>

      {/* Canonical */}
      <table style={{ width:"100%", fontSize:13, borderCollapse:"collapse", marginBottom:10 }}>
        <tbody>
          {[["Disease", canonical?.cancer_type],["Gene", canonical?.gene],["Variant", canonical?.variant]].map(([k,v])=>(
            <tr key={k}><td style={{ color:"#888", width:80 }}>{k}</td><td><strong>{v||<em style={{color:"#bbb"}}>—</em>}</strong></td></tr>
          ))}
        </tbody>
      </table>

      {/* Score breakdown */}
      {score_breakdown && Object.keys(score_breakdown).length > 0 && (
        <div style={{ marginBottom:10 }}>
          <p style={{ fontSize:12, fontWeight:"bold", color:"#555", margin:"0 0 6px" }}>Confidence breakdown</p>
          {Object.entries(score_breakdown).map(([k,v])=>(
            <ScoreBar key={k} label={k.replace(/_/g," ")} value={v}/>
          ))}
        </div>
      )}

      {/* Explanation */}
      <div style={{ background:"#f0f4f8", borderRadius:6, padding:10, fontSize:13, marginBottom:10 }}>
        <strong>Explanation:</strong> {explanation}
      </div>

      {/* Alternatives */}
      {alternatives?.length > 0 && (
        <div style={{ marginBottom:10 }}>
          <p style={{ fontSize:12, fontWeight:"bold", color:"#555", margin:"0 0 4px" }}>Alternatives considered</p>
          <ul style={{ paddingLeft:16, margin:0 }}>
            {alternatives.map((a,i)=>(
              <li key={i} style={{ fontSize:12, color:"#555" }}>{a.name || a.id} {a.reason && `— ${a.reason}`}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Notes */}
      {notes?.length > 0 && <div style={{ color:"#9a6700", fontSize:12, marginBottom:8 }}>⚠ {notes.join(" ")}</div>}

      {/* Evidence + Audit (collapsible) */}
      <button onClick={()=>setExpanded(!expanded)} style={{ fontSize:12, background:"none", border:"1px solid #ccc", borderRadius:4, padding:"3px 10px", cursor:"pointer" }}>
        {expanded ? "Hide" : "Show"} evidence & audit trail
      </button>
      {expanded && (
        <div style={{ marginTop:8 }}>
          <p style={{ fontSize:12, fontWeight:"bold", margin:"6px 0 4px" }}>Evidence</p>
          <EvidenceList evidence={evidence}/>
          <p style={{ fontSize:12, fontWeight:"bold", margin:"10px 0 4px" }}>Audit trail</p>
          <ol style={{ fontSize:11, color:"#666", paddingLeft:16, margin:0 }}>
            {audit_trail?.map((s,i)=><li key={i}>{s}</li>)}
          </ol>
        </div>
      )}
    </div>
  );
}

// ── PAGE: Single record ───────────────────────────────────────────────────────
const EXAMPLES = [
  { label:"Raw Disease Alias", cancer_type:"NSCLC", gene:"EGFR", variant:"Ex19del" },
  { label:"Gene Alias", cancer_type:"NSCLC", gene:"HER1", variant:"L858R" },
  { label:"Variant Alias", cancer_type:"NSCLC", gene:"HER2", variant:"amp" },
  { label:"Catalog Match", cancer_type:"Melanoma", gene:"BRAF", variant:"V600E" },
  { label:"Disease Fuzzy", cancer_type:"melanomaa", gene:"BRAF", variant:"V600E" },
  { label:"Gene Fuzzy", cancer_type:"NSCLC", gene:"ERRB2", variant:"amp" },
  { label:"Variant Fuzzy", cancer_type:"NSCLC", gene:"EGFR", variant:"Ex19dele" },
  { label:"TRK Cat-VRS Review", cancer_type:"NSCLC", gene:"TRK", variant:"fusion" },
  { label:"LLM Review Hook", cancer_type:"NSCLC", gene:"KRAS", variant:"mutation" },
  { label:"Cannot Reconcile", cancer_type:"NSCLC", gene:"unknown_gene", variant:"G12C" },
];

const REVIEW_EXAMPLES = [
  { label:"TRK Fusion", cancer_type:"NSCLC", gene:"TRK", variant:"fusion" },
  { label:"BRAF V600", cancer_type:"Melanoma", gene:"BRAF", variant:"V600" },
  { label:"EGFR Exon20ins", cancer_type:"NSCLC", gene:"EGFR", variant:"Exon20ins" },
  { label:"KRAS Mutation + LLM", cancer_type:"NSCLC", gene:"KRAS", variant:"mutation" },
];

const SAMPLE_CSV_ROWS = [
  { case_id:"workflow_001", workflow_step:"Disease alias + variant alias", cancer_type:"NSCLC", gene:"EGFR", variant:"Ex19del", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_002", workflow_step:"Gene alias normalization", cancer_type:"NSCLC", gene:"HER1", variant:"L858R", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_003", workflow_step:"Gene + copy number synonym", cancer_type:"NSCLC", gene:"HER2", variant:"amp", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_004", workflow_step:"Catalog match", cancer_type:"Melanoma", gene:"BRAF", variant:"V600E", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_005", workflow_step:"Disease fuzzy matching", cancer_type:"melanomaa", gene:"BRAF", variant:"V600E", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_006", workflow_step:"Gene fuzzy matching", cancer_type:"NSCLC", gene:"ERRB2", variant:"amp", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_007", workflow_step:"Variant fuzzy matching", cancer_type:"NSCLC", gene:"EGFR", variant:"Ex19dele", expected_status:"AUTO_RECONCILE" },
  { case_id:"workflow_008", workflow_step:"Cat-VRS categorical ambiguity", cancer_type:"NSCLC", gene:"TRK", variant:"fusion", expected_status:"REVIEW_REQUIRED" },
  { case_id:"workflow_009", workflow_step:"Variant ambiguity candidates", cancer_type:"Melanoma", gene:"BRAF", variant:"V600", expected_status:"REVIEW_REQUIRED" },
  { case_id:"workflow_010", workflow_step:"Catalog review required", cancer_type:"NSCLC", gene:"EGFR", variant:"Exon20ins", expected_status:"REVIEW_REQUIRED" },
  { case_id:"workflow_011", workflow_step:"LLM-gated review suggestion", cancer_type:"NSCLC", gene:"KRAS", variant:"mutation", expected_status:"REVIEW_REQUIRED" },
  { case_id:"workflow_012", workflow_step:"Cannot reconcile safe failure", cancer_type:"NSCLC", gene:"unknown_gene", variant:"G12C", expected_status:"CANNOT_RECONCILE" },
  { case_id:"workflow_013", workflow_step:"Cross-disease HER2 alias", cancer_type:"Breast Cancer", gene:"HER2", variant:"HER2+", expected_status:"AUTO_RECONCILE" },
];

const SAMPLE_CSV_HEADERS = ["case_id","workflow_step","cancer_type","gene","variant","expected_status"];

const SAMPLE_CSV_TEXT = [
  SAMPLE_CSV_HEADERS.join(","),
  ...SAMPLE_CSV_ROWS.map(row => SAMPLE_CSV_HEADERS.map(header => row[header]).join(",")),
].join("\n");

function SinglePage() {
  const [form, setForm] = useState({ cancer_type:"NSCLC", gene:"HER2", variant:"Amplification" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError(""); setResult(null); setLoading(true);
    try {
      const r = await apiFetch("/reconcile", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(form) });
      if (!r.ok) throw new Error(`API error ${r.status}`);
      setResult(await r.json());
    } catch(e) { setError(e.message); }
    finally { setLoading(false); }
  }

  return (
    <div>
      <h2 style={{ color:"#028090", marginBottom:4 }}>Single Record Reconciliation</h2>
      <p style={{ color:"#666", fontSize:13 }}>Reconcile a single disease · gene · variant input.</p>

      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:12 }}>
        {EXAMPLES.map(ex=>(
          <button key={ex.label} onClick={()=>setForm(ex)}
            style={{ fontSize:11, padding:"4px 10px", borderRadius:4, border:"1px solid #028090", background:"#e8f4f6", cursor:"pointer", color:"#028090" }}>
            {ex.label}
          </button>
        ))}
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:10, marginBottom:12 }}>
        {[["cancer_type","Disease / Cancer Type"],["gene","Gene"],["variant","Variant"]].map(([k,lbl])=>(
          <div key={k}>
            <label style={{ fontSize:12, color:"#555", display:"block", marginBottom:3 }}>{lbl}</label>
            <input value={form[k]||""} onChange={e=>setForm({...form,[k]:e.target.value})}
              style={{ width:"100%", padding:"6px 8px", borderRadius:4, border:"1px solid #ccc", fontSize:13, boxSizing:"border-box" }}/>
          </div>
        ))}
      </div>
      <button onClick={submit} disabled={loading}
        style={{ padding:"8px 24px", background:"#028090", color:"#fff", border:"none", borderRadius:6, fontSize:14, cursor:"pointer", opacity:loading?0.6:1 }}>
        {loading ? "Reconciling…" : "Reconcile"}
      </button>
      {error && <p style={{ color:"#cf222e", marginTop:8 }}>{error}</p>}
      <ResultCard result={result}/>
    </div>
  );
}

// ── PAGE: CSV Upload ──────────────────────────────────────────────────────────
function UploadPage() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState(null);

  function useSampleCsv() {
    const sampleFile = new File([SAMPLE_CSV_TEXT], "oncoreconcile_demo_cases.csv", {
      type:"text/csv",
    });
    setFile(sampleFile);
    setError("");
  }

  function downloadSampleCsv() {
    const blob = new Blob([SAMPLE_CSV_TEXT], { type:"text/csv" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "oncoreconcile_demo_cases.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function upload() {
    if (!file) return;
    setError(""); setResults(null); setSummary(null); setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await apiFetch("/reconcile/upload", { method:"POST", body:fd });
      if (!r.ok) { const e = await r.json(); throw new Error(e.detail || `Error ${r.status}`); }
      const data = await r.json();
      setResults(data.results);
      setSummary(data.summary);
    } catch(e) { setError(e.message); }
    finally { setLoading(false); }
  }

  return (
    <div>
      <h2 style={{ color:"#028090", marginBottom:4 }}>CSV Batch Upload</h2>
      <p style={{ color:"#666", fontSize:13 }}>Upload a CSV with columns: <code>case_id</code> (optional), <code>cancer_type</code> (optional), <code>gene</code>, <code>variant</code>. Extra demo columns are ignored by the API.</p>

      <div style={{ border:"1px solid #d0d7de", borderRadius:8, background:"#fff", padding:12, margin:"12px 0 16px" }}>
        <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:10, flexWrap:"wrap", marginBottom:8 }}>
          <strong style={{ color:"#444", fontSize:13 }}>Sample CSV</strong>
          <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
            <button onClick={useSampleCsv}
              style={{ marginTop:0, fontSize:12, padding:"5px 12px", borderRadius:4, border:"1px solid #028090", background:"#e8f4f6", color:"#028090", cursor:"pointer" }}>
              Use Sample
            </button>
            <button onClick={downloadSampleCsv}
              style={{ marginTop:0, fontSize:12, padding:"5px 12px", borderRadius:4, border:"1px solid #ccc", background:"#fff", color:"#333", cursor:"pointer" }}>
              Download CSV
            </button>
          </div>
        </div>
        <div style={{ overflowX:"auto" }}>
          <table style={{ fontSize:12, minWidth:760 }}>
            <thead>
              <tr>
                {SAMPLE_CSV_HEADERS.map(header=>(
                  <th key={header} style={{ color:"#555", background:"#f6f8fa" }}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SAMPLE_CSV_ROWS.map(row=>(
                <tr key={row.case_id}>
                  {SAMPLE_CSV_HEADERS.map(header=>(
                    <td key={header}>{row[header]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:12 }}>
        <input type="file" accept=".csv" onChange={e=>setFile(e.target.files[0])}
          style={{ fontSize:13 }}/>
        {file && <span style={{ fontSize:12, color:"#666" }}>{file.name}</span>}
        <button onClick={upload} disabled={!file||loading}
          style={{ padding:"7px 20px", background:"#028090", color:"#fff", border:"none", borderRadius:6, fontSize:13, cursor:"pointer", opacity:(!file||loading)?0.6:1 }}>
          {loading ? "Processing…" : "Upload & Reconcile"}
        </button>
      </div>

      {error && <p style={{ color:"#cf222e" }}>{error}</p>}

      {summary && (
        <div style={{ display:"flex", gap:12, marginBottom:16, flexWrap:"wrap" }}>
          {[["Total",summary.total_records,"#555"],["Auto",summary.auto_reconcile,STATUS_COLOR.AUTO_RECONCILE],
            ["Review",summary.review_required,STATUS_COLOR.REVIEW_REQUIRED],["Cannot",summary.cannot_reconcile,STATUS_COLOR.CANNOT_RECONCILE]].map(([l,n,c])=>(
            <div key={l} style={{ background:"#f5f5f5", borderRadius:8, padding:"10px 18px", textAlign:"center", border:`2px solid ${c}` }}>
              <div style={{ fontSize:22, fontWeight:"bold", color:c }}>{n}</div>
              <div style={{ fontSize:11, color:"#666" }}>{l}</div>
            </div>
          ))}
        </div>
      )}

      {results && results.map((r,i)=>(
        <div key={i} style={{ border:"1px solid #e0e0e0", borderRadius:6, marginBottom:8, overflow:"hidden" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, padding:"8px 12px", background:"#f9f9f9", cursor:"pointer" }}
            onClick={()=>setExpandedIdx(expandedIdx===i?null:i)}>
            <Badge label={r.review_status} color={STATUS_COLOR[r.review_status]}/>
            <span style={{ fontSize:13, fontWeight:"bold" }}>{r.input?.gene} / {r.input?.variant}</span>
            <span style={{ fontSize:12, color:"#888" }}>{r.input?.cancer_type}</span>
            <span style={{ marginLeft:"auto", fontSize:12, color:"#028090" }}>{expandedIdx===i?"▲":"▼"}</span>
          </div>
          {expandedIdx===i && <div style={{ padding:"0 12px 12px" }}><ResultCard result={r}/></div>}
        </div>
      ))}
    </div>
  );
}

// ── PAGE: Review Queue ────────────────────────────────────────────────────────
function ReviewQueuePage() {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({total:0,pending:0,reviewed:0});
  const [filter, setFilter] = useState("pending");
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState("");
  const [seedError, setSeedError] = useState("");
  const [deciding, setDeciding] = useState({});
  const [curatorId, setCuratorId] = useState("curator-1");
  const [selectedCandidateByCase, setSelectedCandidateByCase] = useState({});
  const [expandedAuditByCase, setExpandedAuditByCase] = useState({});

  async function load() {
    setLoading(true);
    try {
      const r = await apiFetch(`/review-queue?status=${filter}`);
      const data = await r.json();
      setItems(data.items);
      setSummary({ total:data.total, pending:data.pending, reviewed:data.reviewed });
    } catch(e) { console.error(e); }
    finally { setLoading(false); }
  }

  useEffect(()=>{ load(); }, [filter]);

  async function seedReviewExample(example) {
    setSeedError("");
    setSeeding(example.label);
    try {
      const r = await apiFetch("/reconcile", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          case_id:`review-demo-${example.label.toLowerCase().replace(/[^a-z0-9]+/g,"-")}-${Date.now()}`,
          cancer_type:example.cancer_type,
          gene:example.gene,
          variant:example.variant,
        }),
      });
      if (!r.ok) throw new Error(`API error ${r.status}`);
      const result = await r.json();
      if (result.review_status !== "REVIEW_REQUIRED") {
        setSeedError(`${example.label} returned ${result.review_status}, so it was not added to the queue.`);
      }
      if (filter !== "pending") {
        setFilter("pending");
      } else {
        load();
      }
    } catch(e) {
      setSeedError(e.message);
    } finally {
      setSeeding("");
    }
  }

  async function decide(caseId, decision) {
    setDeciding(d=>({...d,[caseId]:true}));
    try {
      await apiFetch(`/review-queue/${caseId}/decision`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({ case_id:caseId, decision, curator_id:curatorId })
      });
      load();
    } catch(e) { console.error(e); }
    finally { setDeciding(d=>({...d,[caseId]:false})); }
  }

  async function editToCandidate(item, candidate) {
    if (!candidate) return;
    const name = candidate.name || candidate.id || "";
    const gene = candidate.gene || name.split(" ")[0] || item.canonical?.gene;
    setDeciding(d=>({...d,[item.case_id]:true}));
    try {
      await apiFetch(`/review-queue/${item.case_id}/decision`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          case_id:item.case_id,
          decision:"edit",
          curator_id:curatorId,
          override_canonical:{
            cancer_type:item.canonical?.cancer_type,
            gene,
            variant:name || item.canonical?.variant,
          },
          notes:`Edited to selected candidate: ${name || "unknown candidate"}.`
        })
      });
      load();
    } catch(e) { console.error(e); }
    finally { setDeciding(d=>({...d,[item.case_id]:false})); }
  }

  async function reopenItem(caseId) {
    setDeciding(d=>({...d,[caseId]:true}));
    try {
      await apiFetch(`/review-queue/${caseId}/decision`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          case_id:caseId,
          decision:"reopen",
          curator_id:curatorId,
          notes:"Reopened for additional human review."
        })
      });
      if (filter !== "pending") {
        setFilter("pending");
      } else {
        load();
      }
    } catch(e) { console.error(e); }
    finally { setDeciding(d=>({...d,[caseId]:false})); }
  }

  return (
    <div>
      <h2 style={{ color:"#028090", marginBottom:4 }}>Human Review Queue</h2>
      <p style={{ color:"#666", fontSize:13 }}>REVIEW_REQUIRED cases awaiting curator decision.</p>

      <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap", margin:"12px 0 16px" }}>
        <span style={{ fontSize:12, color:"#555", fontWeight:"bold" }}>Add demo case:</span>
        {REVIEW_EXAMPLES.map(ex=>(
          <button key={ex.label} onClick={()=>seedReviewExample(ex)} disabled={Boolean(seeding)}
            style={{ marginTop:0, fontSize:11, padding:"5px 10px", borderRadius:4, border:"1px solid #9a6700", background:"#fff8dc", cursor:"pointer", color:"#7d4e00", opacity:seeding?0.6:1 }}>
            {seeding === ex.label ? "Adding…" : ex.label}
          </button>
        ))}
      </div>
      {seedError && <p style={{ color:"#cf222e", fontSize:12, marginTop:-8 }}>{seedError}</p>}

      <div style={{ display:"flex", gap:12, alignItems:"center", marginBottom:16, flexWrap:"wrap" }}>
        <div style={{ display:"flex", gap:8 }}>
          {["pending","reviewed","all"].map(f=>(
            <button key={f} onClick={()=>setFilter(f)}
              style={{ padding:"5px 14px", borderRadius:4, border:`1px solid ${filter===f?"#028090":"#ccc"}`,
                background:filter===f?"#028090":"#fff", color:filter===f?"#fff":"#333", cursor:"pointer", fontSize:12 }}>
              {f.charAt(0).toUpperCase()+f.slice(1)}
            </button>
          ))}
        </div>
        <div style={{ display:"flex", gap:8 }}>
          {[["Total",summary.total,"#555"],["Pending",summary.pending,STATUS_COLOR.REVIEW_REQUIRED],["Reviewed",summary.reviewed,STATUS_COLOR.AUTO_RECONCILE]].map(([l,n,c])=>(
            <span key={l} style={{ fontSize:12, color:c, fontWeight:"bold" }}>{l}: {n}</span>
          ))}
        </div>
        <div style={{ marginLeft:"auto", display:"flex", alignItems:"center", gap:6 }}>
          <label style={{ fontSize:12, color:"#555" }}>Curator ID:</label>
          <input value={curatorId} onChange={e=>setCuratorId(e.target.value)}
            style={{ fontSize:12, padding:"3px 8px", border:"1px solid #ccc", borderRadius:4, width:120 }}/>
        </div>
        <button onClick={load} style={{ fontSize:12, padding:"5px 12px", border:"1px solid #ccc", borderRadius:4, cursor:"pointer" }}>
          ↻ Refresh
        </button>
      </div>

      {loading && <p style={{ color:"#888" }}>Loading…</p>}
      {!loading && items.length === 0 && <p style={{ color:"#888" }}>No items in queue.</p>}

      {items.map(item=>{
        const candidateIndex = Number(selectedCandidateByCase[item.case_id] ?? 0);
        const selectedCandidate = item.alternatives?.[candidateIndex] || item.alternatives?.[0];
        return (
        <div key={item.case_id} style={{ border:"2px solid #e8a020", borderRadius:8, padding:14, marginBottom:12, background:"#fffdf5" }}>
          <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:8, flexWrap:"wrap" }}>
            <Badge label={item.review_status} color={STATUS_COLOR[item.review_status]}/>
            <span style={{ fontWeight:"bold", fontSize:14 }}>{item.input?.gene} / {item.input?.variant}</span>
            <span style={{ fontSize:12, color:"#666" }}>{item.input?.cancer_type}</span>
            <span style={{ fontSize:12, color:"#888" }}>Score: {(item.confidence_score*100).toFixed(0)}%</span>
            {item.decision && <Badge label={`✓ ${item.decision}`} color={item.decision==="approve"?STATUS_COLOR.AUTO_RECONCILE:STATUS_COLOR.CANNOT_RECONCILE}/>}
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8, marginBottom:8, fontSize:13 }}>
            {[["Disease",item.canonical?.cancer_type],["Gene",item.canonical?.gene],["Variant",item.canonical?.variant]].map(([k,v])=>(
              <div key={k} style={{ background:"#f5f5f5", borderRadius:4, padding:"6px 10px" }}>
                <span style={{ color:"#888", fontSize:11 }}>{k}</span><br/>
                <strong>{v || "—"}</strong>
              </div>
            ))}
          </div>

          <div style={{ background:"#f0f4f8", borderRadius:6, padding:8, fontSize:12, marginBottom:10, color:"#444" }}>
            {item.explanation}
          </div>

          {/* Score breakdown mini */}
          {item.score_breakdown && (
            <div style={{ marginBottom:10 }}>
              {Object.entries(item.score_breakdown).map(([k,v])=>(
                <ScoreBar key={k} label={k.replace(/_/g," ")} value={v}/>
              ))}
            </div>
          )}

          {/* Alternatives */}
          {item.alternatives?.length > 0 && (
            <div style={{ marginBottom:10 }}>
              <p style={{ fontSize:11, color:"#888", margin:"0 0 4px" }}>Alternatives considered:</p>
              <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
                {item.alternatives.map((a,i)=>(
                  <span key={i} style={{
                    fontSize:11,
                    background:i===candidateIndex?"#ddf4ff":"#eee",
                    border:`1px solid ${i===candidateIndex?"#0969da":"transparent"}`,
                    borderRadius:4,
                    padding:"2px 8px"
                  }}>
                    {a.name || a.id}
                  </span>
                ))}
              </div>
              {!item.decision && (
                <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap", marginTop:8 }}>
                  <label style={{ fontSize:11, color:"#666" }}>Edit candidate:</label>
                  <select
                    value={candidateIndex}
                    onChange={e=>setSelectedCandidateByCase(s=>({...s,[item.case_id]:e.target.value}))}
                    style={{ fontSize:12, padding:"4px 8px", border:"1px solid #ccc", borderRadius:4, minWidth:180 }}
                  >
                    {item.alternatives.map((a,i)=>(
                      <option key={i} value={i}>{a.name || a.id}</option>
                    ))}
                  </select>
                </div>
              )}
              <p style={{ fontSize:11, color:"#666", margin:"6px 0 0" }}>
                Edit to Candidate stores the selected alternative as the reviewed canonical result.
              </p>
            </div>
          )}

          {item.notes?.length > 0 && (
            <p style={{ fontSize:12, color:"#9a6700", margin:"0 0 10px" }}>⚠ {item.notes.join(" ")}</p>
          )}

          <button
            onClick={()=>setExpandedAuditByCase(s=>({...s,[item.case_id]:!s[item.case_id]}))}
            style={{ fontSize:12, background:"#fff", border:"1px solid #ccc", borderRadius:4, padding:"4px 10px", cursor:"pointer", margin:"0 0 10px" }}
          >
            {expandedAuditByCase[item.case_id] ? "Hide" : "Show"} evidence & audit trail
          </button>
          {expandedAuditByCase[item.case_id] && (
            <div style={{ border:"1px solid #d0d7de", borderRadius:6, background:"#fff", padding:10, marginBottom:10 }}>
              <p style={{ fontSize:12, fontWeight:"bold", margin:"0 0 6px", color:"#444" }}>Governance evidence</p>
              <EvidenceList evidence={item.evidence}/>
              <p style={{ fontSize:12, fontWeight:"bold", margin:"10px 0 4px", color:"#444" }}>Audit trail</p>
              <ol style={{ fontSize:11, color:"#666", paddingLeft:16, margin:0 }}>
                {item.audit_trail?.map((s,i)=><li key={i}>{s}</li>)}
              </ol>
              {item.curator_notes && (
                <p style={{ fontSize:11, color:"#666", margin:"8px 0 0" }}>
                  <strong>Curator notes:</strong> {item.curator_notes}
                </p>
              )}
            </div>
          )}

          {/* Decision buttons */}
          {!item.decision && (
            <div style={{ display:"flex", gap:8 }}>
              <button onClick={()=>decide(item.case_id,"approve")} disabled={deciding[item.case_id]}
                style={{ padding:"6px 20px", background:STATUS_COLOR.AUTO_RECONCILE, color:"#fff", border:"none", borderRadius:6, cursor:"pointer", fontSize:13 }}>
                ✓ Approve
              </button>
              <button onClick={()=>decide(item.case_id,"reject")} disabled={deciding[item.case_id]}
                style={{ padding:"6px 20px", background:STATUS_COLOR.CANNOT_RECONCILE, color:"#fff", border:"none", borderRadius:6, cursor:"pointer", fontSize:13 }}>
                ✗ Reject
              </button>
              <button onClick={()=>editToCandidate(item, selectedCandidate)} disabled={deciding[item.case_id] || !item.alternatives?.length}
                style={{ padding:"6px 20px", background:"#0969da", color:"#fff", border:"none", borderRadius:6, cursor:"pointer", fontSize:13, opacity:item.alternatives?.length?1:0.5 }}>
                Edit to Candidate
              </button>
            </div>
          )}
          {item.decision && item.curator_id && (
            <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
              <p style={{ fontSize:11, color:"#888", margin:0 }}>Reviewed by {item.curator_id}</p>
              <button onClick={()=>reopenItem(item.case_id)} disabled={deciding[item.case_id]}
                style={{ marginTop:0, padding:"4px 12px", background:"#fff", color:"#555", border:"1px solid #ccc", borderRadius:6, cursor:"pointer", fontSize:12 }}>
                Reopen
              </button>
            </div>
          )}
        </div>
      )})}
    </div>
  );
}

// ── PAGE: Benchmark Metrics ──────────────────────────────────────────────────
function BenchmarkPage() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setError(""); setLoading(true);
    try {
      const r = await apiFetch("/benchmark");
      if (!r.ok) throw new Error(`API error ${r.status}`);
      setMetrics(await r.json());
    } catch(e) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(()=>{ load(); }, []);

  const pct = value => `${Math.round((value || 0) * 100)}%`;
  return (
    <div>
      <h2 style={{ color:"#028090", marginBottom:4 }}>Benchmark Validation</h2>
      <p style={{ color:"#666", fontSize:13 }}>Accuracy, coverage, and review-rate validation for the curated MVP benchmark.</p>
      <button onClick={load} disabled={loading}
        style={{ padding:"7px 20px", background:"#028090", color:"#fff", border:"none", borderRadius:6, fontSize:13, cursor:"pointer", opacity:loading?0.6:1 }}>
        {loading ? "Refreshing…" : "Refresh Metrics"}
      </button>
      {error && <p style={{ color:"#cf222e" }}>{error}</p>}
      {metrics && (
        <>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(160px,1fr))", gap:12, marginTop:16 }}>
            {[["Accuracy",pct(metrics.accuracy),metrics.target_status?.accuracy],["Coverage",pct(metrics.coverage),metrics.target_status?.coverage],
              ["Review Rate",pct(metrics.review_rate),true],["Cases",metrics.total_cases,true]].map(([label,value,ok])=>(
              <div key={label} style={{ background:"#fff", border:`2px solid ${ok ? STATUS_COLOR.AUTO_RECONCILE : STATUS_COLOR.CANNOT_RECONCILE}`, borderRadius:8, padding:14 }}>
                <div style={{ fontSize:26, fontWeight:"bold", color:ok ? STATUS_COLOR.AUTO_RECONCILE : STATUS_COLOR.CANNOT_RECONCILE }}>{value}</div>
                <div style={{ fontSize:12, color:"#666" }}>{label}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop:14, background:"#f8fafc", border:"1px solid #e2e8f0", borderRadius:8, padding:12, fontSize:13 }}>
            Target accuracy: {pct(metrics.targets?.accuracy)} · Target coverage: {pct(metrics.targets?.coverage)}
          </div>
          <div style={{ marginTop:14, background:"#fff", border:"1px solid #d0d7de", borderRadius:8, padding:14 }}>
            <p style={{ fontSize:13, fontWeight:"bold", color:"#444", margin:"0 0 8px" }}>How these numbers are calculated</p>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))", gap:10, fontSize:12, color:"#444" }}>
              <div style={{ background:"#f6f8fa", borderRadius:6, padding:10 }}>
                <strong>Accuracy</strong><br/>
                Full matches / total cases<br/>
                <span style={{ color:"#666" }}>{metrics.counts?.full_correct} / {metrics.total_cases}</span>
              </div>
              <div style={{ background:"#f6f8fa", borderRadius:6, padding:10 }}>
                <strong>Coverage</strong><br/>
                Not CANNOT_RECONCILE / total cases<br/>
                <span style={{ color:"#666" }}>{metrics.counts?.resolved} / {metrics.total_cases}</span>
              </div>
              <div style={{ background:"#f6f8fa", borderRadius:6, padding:10 }}>
                <strong>Review rate</strong><br/>
                REVIEW_REQUIRED / total cases<br/>
                <span style={{ color:"#666" }}>{metrics.counts?.review_required} / {metrics.total_cases}</span>
              </div>
            </div>
            <p style={{ fontSize:12, color:"#666", margin:"10px 0 0" }}>
              Benchmark source: {metrics.benchmark_file}. Cases are manually curated from the local disease, gene, and variant catalog and include auto-reconcile, review-required, and safe-failure examples.
            </p>
            <p style={{ fontSize:12, color:"#666", margin:"6px 0 0" }}>
              This is internal MVP validation, not independent external clinical validation. Future validation should use blinded curator review and larger real-world datasets.
            </p>
          </div>
          {metrics.failures?.length > 0 && (
            <div style={{ marginTop:14 }}>
              <p style={{ fontSize:12, fontWeight:"bold", color:"#555" }}>First failures</p>
              <table style={{ fontSize:12 }}>
                <thead><tr><th>Case</th><th>Expected</th><th>Actual</th></tr></thead>
                <tbody>
                  {metrics.failures.map(f=>(
                    <tr key={f.case_id}><td>{f.case_id}</td><td>{f.expected_status}</td><td>{f.actual_status}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ── Nav + App shell ───────────────────────────────────────────────────────────
function Nav() {
  const navStyle = { textDecoration:"none", padding:"8px 16px", borderRadius:6, fontSize:13, fontWeight:"bold" };
  const active = { background:"#028090", color:"#fff" };
  const inactive = { background:"#e8f4f6", color:"#028090" };
  return (
    <nav style={{ display:"flex", gap:8, marginBottom:24, paddingBottom:12, borderBottom:"1px solid #e0e0e0", alignItems:"center" }}>
      <span style={{ fontWeight:"bold", fontSize:16, color:"#0A1628", marginRight:8 }}>🧬 OncoReconcile AI</span>
      {[["Single Record","/"],["CSV Upload","/upload"],["Review Queue","/review"],["Benchmark","/benchmark"]].map(([label,path])=>(
        <NavLink key={path} to={path} end={path==="/"}
          style={({isActive})=>({...navStyle,...(isActive?active:inactive)})}>
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div style={{ maxWidth:900, margin:"0 auto", padding:"24px 16px", fontFamily:"system-ui,sans-serif" }}>
        <Nav/>
        <Routes>
          <Route path="/" element={<SinglePage/>}/>
          <Route path="/upload" element={<UploadPage/>}/>
          <Route path="/review" element={<ReviewQueuePage/>}/>
          <Route path="/benchmark" element={<BenchmarkPage/>}/>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")).render(<App/>);
