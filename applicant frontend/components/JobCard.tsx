import Link from "next/link";
import { Job } from "@/lib/types";

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function JobCard({ job }: { job: Job }) {
  return (
    <article className="card job-card">
      <div className="card-topline">
        <span className="eyebrow">{job.department}</span>
        <span className={`availability ${job.accepting_applications ? "open" : "closed"}`}>
          {job.accepting_applications ? "Accepting" : "Not accepting"}
        </span>
      </div>
      <h2><Link href={`/jobs/${job.id}`}>{job.title}</Link></h2>
      <div className="job-meta">
        <span>⌖ {job.location}</span>
        <span>{money.format(job.salary_min)}–{money.format(job.salary_max)}</span>
      </div>
      <p className="clamp">{job.description}</p>
      <div className="skills">
        {job.required_skills.map((skill) => <span key={skill}>{skill}</span>)}
      </div>
      <footer>
        <span>{job.application_count} applicant{job.application_count === 1 ? "" : "s"}</span>
        <Link href={`/jobs/${job.id}`} className="text-link">View role →</Link>
      </footer>
    </article>
  );
}

