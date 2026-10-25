"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { JobList, Stats } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [jobs, setJobs] = useState<JobList | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch<Stats>("/api/stats"),
      apiFetch<JobList>("/api/jobs?include_closed=true&per_page=100"),
    ])
      .then(([statsData, jobsData]) => { setStats(statsData); setJobs(jobsData); })
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Could not load dashboard"));
  }, []);

  const cards = stats ? [
    ["Total roles", stats.total_jobs],
    ["Open roles", stats.open_jobs],
    ["Closed roles", stats.closed_jobs],
    ["Applications", stats.total_applications],
    ["Avg. per role", stats.avg_applications_per_job],
    ["Top department", stats.top_department ?? "—"],
  ] : [];

  return (
    <div className="page-shell">
      <section className="dashboard-heading">
        <span className="eyebrow">Live hiring intelligence</span>
        <h1>Recruiting at a glance.</h1>
        <p>Manage every role and application from this administration workspace.</p>
      </section>
      {error && <p className="form-error">{error}</p>}
      {!stats && !error ? <div className="empty-state">Loading analytics…</div> : (
        <div className="stats-grid">
          {cards.map(([label, value], index) => (
            <article className={`stat-card ${index === 5 ? "featured" : ""}`} key={label}>
              <span>{label}</span><strong>{value}</strong>
            </article>
          ))}
        </div>
      )}
      <section className="jobs-section">
        <div className="section-heading">
          <div><span className="eyebrow">Role management</span><h2>All job listings</h2></div>
          <Link href="/jobs/new" className="button">Post a job</Link>
        </div>
        <div className="job-table">
          {jobs?.results.map((job) => (
            <article className="job-row" key={job.id}>
              <div><h3>{job.title}</h3><p>{job.department} · {job.location}</p></div>
              <span>{job.application_count} applicants</span>
              <span className={`availability ${job.is_closed ? "closed" : "open"}`}>{job.is_closed ? "Closed" : "Open"}</span>
              <Link href={`/jobs/${job.id}/applications`} className="text-link">Manage →</Link>
            </article>
          ))}
          {jobs && jobs.results.length === 0 && <div className="empty-state">No jobs yet. Post the first role.</div>}
        </div>
      </section>
    </div>
  );
}

