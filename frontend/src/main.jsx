import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://localhost:8000/api";

function App() {
  const [url, setUrl] = useState("https://github.com/tiangolo/fastapi");
  const [repoId, setRepoId] = useState("");
  const [question, setQuestion] = useState("Explain how dependency injection works in this repository.");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [toolOutput, setToolOutput] = useState("");

  async function ingest() {
    setBusy(true);
    setStatus("Indexing repository...");
    try {
      const r = await fetch(API + "/repos/ingest", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({repo_url: url})
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Indexing failed");
      setRepoId(d.repo_id);

      const fr = await fetch(API + "/repos/" + d.repo_id + "/files");
      const fd = await fr.json();
      const nextFiles = fd.files || [];
      setFiles(nextFiles);
      setSelectedFile(nextFiles[0] || "");
      setStatus("Indexed " + d.files_indexed + " files / " + d.chunks_indexed + " chunks.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function ask() {
    if (!repoId) return setStatus("Index a repository first.");
    setBusy(true);
    setStatus("Retrieving context and generating answer...");
    try {
      const r = await fetch(API + "/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({repo_id: repoId, question, top_k: 6})
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Query failed");
      setAnswer(d.answer);
      setCitations(d.citations || []);
      setStatus("Done.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function runTool(kind) {
    if (!repoId || !selectedFile) return setStatus("Index a repository and select a file first.");
    setBusy(true);
    setStatus(kind === "review" ? "Reviewing code..." : "Generating documentation...");
    try {
      const endpoint = kind === "review" ? "/review" : "/docs/generate";
      const r = await fetch(API + endpoint, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({repo_id: repoId, path: selectedFile})
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "Request failed");
      setToolOutput(d.review || d.documentation || "");
      setStatus("Done.");
    } catch (e) {
      setStatus(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header>
        <div>
          <span className="eyebrow">GENAI • RAG • CODE INTELLIGENCE</span>
          <h1>RepoMind</h1>
          <p>Chat with a GitHub repository using source-aware retrieval and citations.</p>
        </div>
        <div className="pill">{repoId ? "INDEXED" : "NOT INDEXED"}</div>
      </header>

      <main>
        <section className="card">
          <h2>1. Index a repository</h2>
          <div className="row">
            <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/owner/repo"/>
            <button onClick={ingest} disabled={busy}>Index repo</button>
          </div>
          <p className="muted">Public GitHub repositories are supported.</p>
        </section>

        <section className="card">
          <h2>2. Ask the codebase</h2>
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows="4"/>
          <button className="wide" onClick={ask} disabled={busy}>Ask RepoMind</button>
          {status && <p className="status">{status}</p>}
        </section>

        <section className="card">
          <h2>3. Analyze a file</h2>
          <div className="row">
            <select value={selectedFile} onChange={(e) => setSelectedFile(e.target.value)} disabled={!files.length}>
              <option value="">Select a file</option>
              {files.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
            <button onClick={() => runTool("review")} disabled={busy || !selectedFile}>Code review</button>
            <button onClick={() => runTool("docs")} disabled={busy || !selectedFile}>Generate docs</button>
          </div>
          {toolOutput && <pre className="answer">{toolOutput}</pre>}
        </section>

        <section className="card">
          <h2>Answer</h2>
          <pre className="answer">{answer || "Your repository answer will appear here."}</pre>
          {citations.length > 0 && (
            <>
              <h3>Retrieved sources</h3>
              <div className="cites">
                {citations.map((c, i) => (
                  <div key={i}>
                    <b>{c.path}</b>
                    <span>lines {c.start_line}-{c.end_line}</span>
                    <em>{c.score.toFixed(3)}</em>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
