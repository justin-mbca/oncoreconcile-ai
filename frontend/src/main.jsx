import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

/*
 * Reference implementation — frontend reconciliation result rendering.
 *
 * Owner: Anne
 * Branch: anne/evidence-rendering  (branch off vanguard_justin)
 * Due: June 6, 2026
 *
 * What to complete:
 *   - Ensure API_BASE_URL uses VITE_API_BASE_URL env var (Eric's task: add .env.local)
 *   - Improve styling of confidence badge and review status badge (style.css)
 *   - Add CSV upload section (optional Checkpoint 1 stretch task)
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const CONFIDENCE_COLORS = {
  HIGH: "#1a7f37",
  MEDIUM: "#9a6700",
  LOW: "#cf222e",
};

const STATUS_COLORS = {
  AUTO_RECONCILE: "#1a7f37",
  REVIEW_REQUIRED: "#9a6700",
  CANNOT_RECONCILE: "#cf222e",
};

const EXAMPLE_INPUTS = [
  { label: "EGFR Exon 19 Deletion", cancer_type: "NSCLC", gene: "EGFR", variant: "Exon 19 Deletion" },
  { label: "HER2 Amplification", cancer_type: "NSCLC", gene: "HER2", variant: "amp" },
  { label: "TRK Fusion Review", cancer_type: "NSCLC", gene: "TRK", variant: "fusion" },
  { label: "Cannot Reconcile", cancer_type: "NSCLC", gene: "unknown_gene", variant: "G12C" },
  { label: "ALK Rearrangement", cancer_type: "Lung Cancer", gene: "ALK", variant: "Rearrangement" },
  { label: "PIK3CA E545K", cancer_type: "Breast Cancer", gene: "PIK3CA", variant: "E545K" },
  { label: "RET Fusion", cancer_type: "NSCLC", gene: "RET", variant: "Fusion" },
];

function Badge({ label, color }) {
  return (
    <span style={{
      background: color,
      color: "#fff",
      borderRadius: "4px",
      padding: "2px 8px",
      fontSize: "0.85em",
      fontWeight: "bold",
    }}>
      {label}
    </span>
  );
}

function EvidenceList({ evidence }) {
  if (!evidence || evidence.length === 0) return <p style={{ color: "#666" }}>No evidence available.</p>;
  return (
    <ul style={{ paddingLeft: "1.2em", margin: 0 }}>
      {evidence.map((item, i) => (
        <li key={i} style={{ marginBottom: "6px" }}>
          <strong>{item.type}</strong> — {item.description}{" "}
          <span style={{ color: "#666", fontSize: "0.85em" }}>[{item.source}]</span>
        </li>
      ))}
    </ul>
  );
}

function App() {
  const [form, setForm] = useState({
    cancer_type: "NSCLC",
    gene: "HER2",
    variant: "Amplification",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function submitRecord() {
    setError("");
    setResult(null);
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/reconcile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!response.ok) throw new Error(`Request failed: ${response.status}`);
      setResult(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to call backend API");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>OncoReconcile AI</h1>
      <p>Human-Governed Oncology Reconciliation Workbench</p>

      <section className="card">
        <h2>Manual Input</h2>
        <p className="helper-text">
          Try one of these examples to test the backend quickly:
        </p>

        <div className="example-grid">
          {EXAMPLE_INPUTS.map((example) => (
            <button
              key={example.label}
              type="button"
              className="example-button"
              onClick={() => setForm({
                cancer_type: example.cancer_type,
                gene: example.gene,
                variant: example.variant,
              })}
            >
              <strong>{example.label}</strong>
              <span>{example.cancer_type} · {example.gene} · {example.variant}</span>
            </button>
          ))}
        </div>

        <label>Cancer Type</label>
        <input
          value={form.cancer_type}
          onChange={(e) => setForm({ ...form, cancer_type: e.target.value })}
        />

        <label>Gene</label>
        <input
          value={form.gene}
          onChange={(e) => setForm({ ...form, gene: e.target.value })}
        />

        <label>Variant</label>
        <input
          value={form.variant}
          onChange={(e) => setForm({ ...form, variant: e.target.value })}
        />

        <button onClick={submitRecord} disabled={isLoading}>
          {isLoading ? "Reconciling..." : "Reconcile"}
        </button>
        {error && <p style={{ color: "#cf222e" }}>{error}</p>}
      </section>

      {result && (
        <section className="card">
          <h2>Result</h2>

          <h3>Canonical Concept</h3>
          <table>
            <tbody>
              <tr>
                <th>Canonical Cancer Type</th>
                <td>{result.canonical?.cancer_type || <em>not resolved</em>}</td>
              </tr>
              <tr>
                <th>Canonical Gene</th>
                <td>{result.canonical?.gene || <em>not resolved</em>}</td>
              </tr>
              <tr>
                <th>Canonical Variant</th>
                <td>{result.canonical?.variant || <em>not resolved</em>}</td>
              </tr>
            </tbody>
          </table>

          <h3>Assessment</h3>
          <table>
            <tbody>
              <tr>
                <th>Confidence</th>
                <td>
                  <Badge
                    label={result.confidence}
                    color={CONFIDENCE_COLORS[result.confidence] || "#666"}
                  />
                </td>
              </tr>
              <tr>
                <th>Review Status</th>
                <td>
                  <Badge
                    label={result.review_status}
                    color={STATUS_COLORS[result.review_status] || "#666"}
                  />
                </td>
              </tr>
              <tr>
                <th>Explanation</th>
                <td>{result.explanation}</td>
              </tr>
              {result.notes && result.notes.length > 0 && (
                <tr>
                  <th>Notes</th>
                  <td>
                    <ul style={{ paddingLeft: "1.2em", margin: 0 }}>
                      {result.notes.map((note, i) => <li key={i}>{note}</li>)}
                    </ul>
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <h3>Evidence</h3>
          <EvidenceList evidence={result.evidence} />
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
