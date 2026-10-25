"use client";

import { FormEvent, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Application } from "@/lib/types";

export function ApplyForm({ jobId, disabled }: { jobId: number; disabled: boolean }) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true); setError(""); setMessage("");
    const form = new FormData(event.currentTarget);
    const payload = {
      applicant_name: form.get("applicant_name"),
      email: form.get("email"),
      years_experience: Number(form.get("years_experience")),
      cv_summary: form.get("cv_summary"),
      linkedin_url: form.get("linkedin_url") || null,
    };
    try {
      await apiFetch<Application>(`/api/jobs/${jobId}/applications`, { method: "POST", body: JSON.stringify(payload) });
      setMessage("Application received. Good luck!");
      event.currentTarget.reset();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not submit the application");
    } finally { setSubmitting(false); }
  }

  if (disabled) return <div className="notice">This role is not accepting new applications.</div>;
  return (
    <form className="form-stack" onSubmit={submit}>
      <div className="form-grid">
        <label>Full name<input name="applicant_name" required maxLength={200} /></label>
        <label>Email<input name="email" type="email" required /></label>
        <label>Years of experience<input name="years_experience" type="number" min="0" required /></label>
        <label>LinkedIn URL <span>(optional)</span><input name="linkedin_url" type="url" placeholder="https://linkedin.com/in/..." /></label>
      </div>
      <label>CV summary <span>(max 1000 characters)</span><textarea name="cv_summary" required maxLength={1000} rows={6} /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      {message && <p className="form-success" role="status">{message}</p>}
      <button className="button" disabled={submitting}>{submitting ? "Submitting…" : "Submit application"}</button>
    </form>
  );
}

