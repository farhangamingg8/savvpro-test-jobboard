import { ApplicationStatus } from "@/lib/types";

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  return <span className={`status status-${status}`}>{status}</span>;
}

