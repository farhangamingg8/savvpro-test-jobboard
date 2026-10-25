"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ApplicationRow } from "@/components/ApplicationRow";
import { apiFetch } from "@/lib/api";
import { Application, ApplicationStatus, Job } from "@/lib/types";

export default function ApplicationsPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [filter, setFilter] = useState<ApplicationStatus | "">("");
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    try {
      const suffix = filter ? `?status=${filter}` : "";
      const [jobData, appData] = await Promise.all([apiFetch<Job>(`/api/jobs/${params.id}`), apiFetch<Application[]>(`/api/jobs/${params.id}/applications${suffix}`)]);
      setJob(jobData); setApplications(appData);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Could not load pipeline"); }
  }, [filter, params.id]);
  useEffect(() => { load(); }, [load]);

  async function closeJob() {
    if (!window.confirm("Close this job to new applications? Existing pending applications will remain pending.")) return;
    try { await apiFetch<Job>(`/api/jobs/${params.id}/close`, { method: "POST" }); await load(); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not close job"); }
  }

  function replace(updated: Application) { setApplications((current) => current.map((item) => item.id === updated.id ? updated : item).filter((item) => !filter || item.status === filter)); }
  return <div className="page-shell">
    <Link href="/dashboard" className="back-link">← Back to dashboard</Link>
    <div className="pipeline-header"><div><span className="eyebrow">Hiring pipeline</span><h1>{job?.title ?? "Applications"}</h1><p>{applications.length} application{applications.length === 1 ? "" : "s"} in this view</p></div>{job && <button className="button button-danger" disabled={job.is_closed} onClick={closeJob}>{job.is_closed ? "Job closed" : "Close job"}</button>}</div>
    <div className="pipeline-toolbar"><label>Filter by status<select value={filter} onChange={(e) => setFilter(e.target.value as ApplicationStatus | "")}><option value="">All applications</option><option value="pending">Pending</option><option value="shortlisted">Shortlisted</option><option value="offered">Offered</option><option value="rejected">Rejected</option></select></label></div>
    {error && <p className="form-error">{error}</p>}
    <div className="application-list">{applications.map((application) => <ApplicationRow key={application.id} application={application} onUpdated={replace} />)}{!error && !applications.length && <div className="empty-state">No applications in this stage yet.</div>}</div>
  </div>;
}

