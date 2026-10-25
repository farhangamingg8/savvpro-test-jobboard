import Link from "next/link";

export function Header() {
  return (
    <header className="site-header">
      <Link href="/" className="brand" aria-label="JobBoard Pro home">
        <span className="brand-mark">JB</span>
        <span>JobBoard <strong>Pro</strong></span>
      </Link>
      <nav aria-label="Main navigation">
        <Link href="/">Open roles</Link>
      </nav>
    </header>
  );
}

