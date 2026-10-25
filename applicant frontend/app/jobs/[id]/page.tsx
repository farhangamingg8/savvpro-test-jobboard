"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ApplyForm } from "@/components/ApplyForm";
import { apiFetch } from "@/lib/api";
import { Job } from "@/lib/types";

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<Job>(`/api/jobs/${params.id}`).then(setJob).catch((e) => setError(e.message)); }, [params.id]);
  if (error) return <div className="page-shell narrow empty-state">{error}</div>;
  if (!job) return <div className="page-shell narrow empty-state">Loading role…</div>;
  return <div className="page-shell detail-layout">
    <article className="job-detail">
      <Link href="/" className="back-link">← All roles</Link>
      <span className="eyebrow">{job.department}</span><h1>{job.title}</h1>
      <div className="job-meta large"><span>⌖ {job.location}</span><span>{money.format(job.salary_min)}–{money.format(job.salary_max)}</span><span>Apply by {new Date(`${job.deadline}T00:00:00`).toLocaleDateString()}</span></div>
      <h2>About the role</h2><p className="description">{job.description}</p>
      <h2>Skills we value</h2><div className="skills large">{job.required_skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
    </article>
    <aside className="apply-panel"><div><span className="eyebrow">Your next chapter</span><h2>Apply for this role</h2><p>Tell us a little about your experience. We review every application.</p></div><ApplyForm jobId={job.id} disabled={!job.accepting_applications} /></aside>
  </div>;
}

