"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { Application, ApplicationStatus } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";

const transitions: Record<ApplicationStatus, ApplicationStatus[]> = {
  pending: ["shortlisted", "rejected"], shortlisted: ["offered", "rejected"], offered: ["rejected"], rejected: [],
};

export function ApplicationRow({ application, onUpdated }: { application: Application; onUpdated: (value: Application) => void }) {
  const [nextStatus, setNextStatus] = useState<ApplicationStatus | "">("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  async function update() {
    if (!nextStatus || !note.trim()) { setError("Choose a status and add a manager note."); return; }
    try {
      const updated = await apiFetch<Application>(`/api/applications/${application.id}/status`, {
        method: "PATCH", body: JSON.stringify({ status: nextStatus, note }),
      });
      onUpdated(updated); setNextStatus(""); setNote(""); setError("");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Update failed"); }
  }

  return (
    <article className="application-card">
      <div className="application-summary">
        <div><h3>{application.applicant_name}</h3><a href={`mailto:${application.email}`}>{application.email}</a></div>
        <div className="experience">{application.years_experience} years</div>
        <StatusBadge status={application.status} />
        <button className="button button-secondary button-small" onClick={() => setOpen(!open)}>{open ? "Hide" : "Review"}</button>
      </div>
      {open && <div className="application-detail">
        <p>{application.cv_summary}</p>
        {application.linkedin_url && <a className="text-link" href={application.linkedin_url} target="_blank" rel="noreferrer">LinkedIn profile ↗</a>}
        <h4>Status history</h4>
        <ol className="history">{application.history.map((item) => <li key={item.id}><StatusBadge status={item.to_status} /><span>{item.note}</span><time>{new Date(item.created_at).toLocaleString()}</time></li>)}</ol>
        {transitions[application.status].length > 0 && <div className="status-form">
          <select value={nextStatus} onChange={(e) => setNextStatus(e.target.value as ApplicationStatus)}><option value="">Next status…</option>{transitions[application.status].map((value) => <option key={value}>{value}</option>)}</select>
          <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Required manager note" />
          <button className="button button-small" onClick={update}>Update</button>
        </div>}
        {error && <p className="form-error">{error}</p>}
      </div>}
    </article>
  );
}

