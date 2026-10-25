"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { Job } from "@/lib/types";

export default function NewJobPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError("");
    const data = new FormData(event.currentTarget);
    const max = data.get("max_applicants");
    const payload = {
      title: data.get("title"), department: data.get("department"), description: data.get("description"), location: data.get("location"),
      salary_min: Number(data.get("salary_min")), salary_max: Number(data.get("salary_max")),
      required_skills: String(data.get("required_skills")).split(",").map((item) => item.trim()).filter(Boolean),
      max_applicants: max ? Number(max) : null, deadline: data.get("deadline"),
    };
    try {
      const job = await apiFetch<Job>("/api/jobs", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      router.push(`/jobs/${job.id}/applications`);
    }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not create job"); setSaving(false); }
  }
  return <div className="page-shell narrow"><section className="dashboard-heading"><span className="eyebrow">Hiring manager</span><h1>Post a new role.</h1><p>Create a clear opportunity for your next teammate.</p></section><form className="form-stack card form-card" onSubmit={submit}><div className="form-grid"><label>Job title<input name="title" required /></label><label>Department<input name="department" required /></label><label>Location<select name="location" required><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">Onsite</option></select></label><label>Deadline<input name="deadline" type="date" required /></label><label>Minimum salary<input name="salary_min" type="number" min="0" required /></label><label>Maximum salary<input name="salary_max" type="number" min="1" required /></label><label>Maximum applicants <span>(optional)</span><input name="max_applicants" type="number" min="1" /></label><label>Required skills <span>(comma separated)</span><input name="required_skills" required placeholder="Python, FastAPI, SQL" /></label></div><label>Description<textarea name="description" rows={8} required /></label>{error && <p className="form-error">{error}</p>}<button className="button" disabled={saving}>{saving ? "Publishing…" : "Publish role"}</button></form></div>;
}

