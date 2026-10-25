"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { JobCard } from "@/components/JobCard";
import { PaginationControls } from "@/components/PaginationControls";
import { apiFetch } from "@/lib/api";
import { JobList } from "@/lib/types";

const empty: JobList = { total_count: 0, page: 1, per_page: 6, results: [] };

export default function JobsPage() {
  const [data, setData] = useState<JobList>(empty);
  const [filters, setFilters] = useState({ search: "", location: "", skill: "", include_closed: false });
  const [applied, setApplied] = useState(filters);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    const params = new URLSearchParams({ page: String(page), per_page: "6" });
    if (applied.search) params.set("search", applied.search);
    if (applied.location) params.set("location", applied.location);
    if (applied.skill) params.set("skill", applied.skill);
    if (applied.include_closed) params.set("include_closed", "true");
    try { setData(await apiFetch<JobList>(`/api/jobs?${params}`)); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Could not load jobs"); }
    finally { setLoading(false); }
  }, [applied, page]);

  useEffect(() => { load(); }, [load]);

  function search(event: FormEvent) { event.preventDefault(); setPage(1); setApplied(filters); }

  return <>
    <section className="hero">
      <div className="hero-copy"><span className="eyebrow">Careers with purpose</span><h1>Do work that<br /><em>moves things forward.</em></h1><p>Explore meaningful roles, meet ambitious teams, and bring your perspective to work that matters.</p><a className="hero-link" href="#open-roles">Explore open roles <span>↓</span></a></div>
      <div className="hero-stat"><small>Live opportunities</small><strong>{data.total_count}</strong><span>roles matching your search</span></div>
    </section>
    <section className="page-shell" id="open-roles">
      <form className="filters" onSubmit={search}>
        <label>Job or department<input value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} placeholder="e.g. Frontend or Engineering" /></label>
        <label>Location<select value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })}><option value="">All locations</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">Onsite</option></select></label>
        <label>Skill<input value={filters.skill} onChange={(e) => setFilters({ ...filters, skill: e.target.value })} placeholder="e.g. Python" /></label>
        <div className="filter-actions">
          <label className="check-label">
            <input type="checkbox" checked={filters.include_closed} onChange={(e) => setFilters({ ...filters, include_closed: e.target.checked })} />
            <span>Include closed</span>
          </label>
          <button className="button" type="submit">Search roles</button>
        </div>
      </form>
      <div className="section-heading"><div><span className="eyebrow">Opportunities</span><h2>Find your place</h2></div><span>{data.total_count} result{data.total_count === 1 ? "" : "s"}</span></div>
      {error && <p className="form-error">{error}</p>}
      {loading ? <div className="empty-state">Loading roles…</div> : data.results.length ? <div className="job-grid">{data.results.map((job) => <JobCard key={job.id} job={job} />)}</div> : <div className="empty-state">No roles match those filters. Try broadening your search.</div>}
      <PaginationControls page={page} perPage={6} total={data.total_count} onPageChange={setPage} />
    </section>
  </>;
}

