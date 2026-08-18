const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Resume
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return request<{ message: string; profile_id: number; full_name: string; technologies_count: number }>(
      '/resume/upload',
      { method: 'POST', body: form, headers: {} }
    );
  },
  getProfile: () => request<any>('/resume/profile'),

  // Jobs
  searchJobs: () => request<any>('/jobs/search', { method: 'POST' }),
  getJobs: (params?: { status?: string; min_score?: number; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    if (params?.min_score !== undefined) query.set('min_score', String(params.min_score));
    if (params?.limit) query.set('limit', String(params.limit));
    return request<{ total: number; jobs: any[] }>(`/jobs?${query}`);
  },
  getJob: (id: number) => request<any>(`/jobs/${id}`),
  analyzeJob: (id: number) => request<any>(`/jobs/${id}/analyze-single`, { method: 'POST' }),
  analyzeAll: () => request<any>('/jobs/analyze', { method: 'POST' }),
  tailorResume: (id: number) => request<any>(`/jobs/${id}/tailor-resume`, { method: 'POST' }),
  generateCoverLetter: (id: number) => request<any>(`/jobs/${id}/cover-letter`, { method: 'POST' }),

  // Applications
  getApplications: (status?: string) => {
    const query = status ? `?status=${status}` : '';
    return request<{ total: number; applications: any[] }>(`/applications${query}`);
  },
  prepareApplication: (id: number) => request<any>(`/applications/${id}/prepare`, { method: 'POST' }),
  approveApplication: (id: number) => request<any>(`/applications/${id}/approve`, { method: 'POST' }),
  cancelApplication: (id: number) => request<any>(`/applications/${id}/cancel`, { method: 'POST' }),
  fillApplicationForm: (id: number) => request<any>(`/applications/${id}/fill-form`, { method: 'POST' }),
  submitApplication: (id: number) => request<any>(`/applications/${id}/submit`, { method: 'POST' }),

  // Dashboard
  getDashboard: () => request<any>('/dashboard'),

  // Export
  downloadExcel: async () => {
    const res = await fetch(`${API_BASE}/export/excel`);
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'job_matches.xlsx';
    a.click();
    URL.revokeObjectURL(url);
  },
  downloadCsv: async () => {
    const res = await fetch(`${API_BASE}/export/csv`);
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'job_matches.csv';
    a.click();
    URL.revokeObjectURL(url);
  },
};
