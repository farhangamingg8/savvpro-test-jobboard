export type Location = "remote" | "hybrid" | "onsite";
export type ApplicationStatus = "pending" | "shortlisted" | "offered" | "rejected";

export interface Job {
  id: number;
  title: string;
  department: string;
  description: string;
  location: Location;
  salary_min: number;
  salary_max: number;
  required_skills: string[];
  max_applicants: number | null;
  deadline: string;
  is_closed: boolean;
  created_at: string;
  application_count: number;
  accepting_applications: boolean;
}

export interface JobList {
  total_count: number;
  page: number;
  per_page: number;
  results: Job[];
}

export interface HistoryEvent {
  id: number;
  from_status: ApplicationStatus | null;
  to_status: ApplicationStatus;
  note: string;
  created_at: string;
}

export interface Application {
  id: number;
  job_id: number;
  applicant_name: string;
  email: string;
  years_experience: number;
  cv_summary: string;
  linkedin_url: string | null;
  status: ApplicationStatus;
  created_at: string;
  history: HistoryEvent[];
}

export interface Stats {
  total_jobs: number;
  open_jobs: number;
  closed_jobs: number;
  total_applications: number;
  avg_applications_per_job: number;
  top_department: string | null;
}

