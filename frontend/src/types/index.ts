export interface Job {
  id: number;
  company: string;
  title: string;
  location: string;
  remote_type: string;
  posted_at: string | null;
  url: string;
  description: string;
  match_score: number | null;
  interview_probability: string | null;
  recommendation: string | null;
  experience_match: number | null;
  aws_match: number | null;
  kubernetes_match: number | null;
  terraform_match: number | null;
  cicd_match: number | null;
  devsecops_match: number | null;
  python_match: number | null;
  gitops_match: number | null;
  mandatory_gaps: string;
  nice_to_have_gaps: string;
  match_reason: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: number;
  job_id: number;
  resume_version: string;
  cover_letter: string;
  application_url: string;
  status: string;
  applied_at: string | null;
  interview_date: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
  job: Job | null;
}

export interface DashboardStats {
  total_jobs: number;
  jobs_last_24h: number;
  unique_jobs: number;
  strong_matches: number;
  applications_ready: number;
  submitted: number;
  interviews: number;
  rejected: number;
}

export interface MatchResult {
  match_score: number;
  interview_probability: string;
  recommendation: string;
  experience_match: number;
  aws_match: number;
  kubernetes_match: number;
  terraform_match: number;
  cicd_match: number;
  devsecops_match: number;
  python_match: number;
  gitops_match: number;
  mandatory_gaps: string[];
  nice_to_have_gaps: string[];
  reason: string;
}
