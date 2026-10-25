import Link from "next/link";

const applicantUrl = process.env.NEXT_PUBLIC_APPLICANT_URL ?? "http://localhost:3000";

export function Header() {
  return (
    <header className="site-header">
      <Link href="/dashboard" className="brand">
        <span className="brand-mark">JB</span>
        <span>JobBoard <strong>Admin</strong></span>
      </Link>
      <nav aria-label="Admin navigation">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/jobs/new" className="button button-small">Post a job</Link>
        <a href={applicantUrl} target="_blank" rel="noreferrer">Applicant site ↗</a>
      </nav>
    </header>
  );
}
