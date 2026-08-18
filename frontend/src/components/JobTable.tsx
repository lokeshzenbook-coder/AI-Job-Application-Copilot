import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Job } from '../types';

interface Props {
  onSelectJob: (job: Job) => void;
}

const statusColors: Record<string, string> = {
  DISCOVERED: 'bg-gray-100 text-gray-700',
  ANALYZING: 'bg-yellow-100 text-yellow-700',
  MATCHED: 'bg-blue-100 text-blue-700',
  QUEUED: 'bg-green-100 text-green-700',
  READY_FOR_REVIEW: 'bg-purple-100 text-purple-700',
  SUBMITTED: 'bg-cyan-100 text-cyan-700',
  REJECTED: 'bg-red-100 text-red-700',
  INTERVIEW: 'bg-emerald-100 text-emerald-700',
};

const probColors: Record<string, string> = {
  VERY_HIGH: 'text-green-700 font-bold',
  HIGH: 'text-green-600 font-semibold',
  MEDIUM: 'text-amber-600',
  LOW: 'text-red-500',
};

export default function JobTable({ onSelectJob }: Props) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => { loadJobs(); }, [filter]);

  async function loadJobs() {
    try {
      const params: any = { limit: 200 };
      if (filter === 'matched') params.min_score = 85;
      else if (filter !== 'all') params.status = filter;
      const data = await api.getJobs(params);
      setJobs(data.jobs);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    setSearching(true);
    try {
      await api.searchJobs();
      await loadJobs();
    } catch (err) {
      alert(`Search failed: ${(err as Error).message}`);
    } finally {
      setSearching(false);
    }
  }

  async function handleAnalyzeAll() {
    setAnalyzing(true);
    try {
      await api.analyzeAll();
      await loadJobs();
    } catch (err) {
      alert(`Analysis failed: ${(err as Error).message}`);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <button
          onClick={handleSearch}
          disabled={searching}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium"
        >
          {searching ? 'Searching...' : 'Search LinkedIn Jobs'}
        </button>
        <button
          onClick={handleAnalyzeAll}
          disabled={analyzing}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
        >
          {analyzing ? 'Analyzing...' : 'Analyze All Jobs'}
        </button>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="all">All Jobs</option>
          <option value="DISCOVERED">Discovered</option>
          <option value="MATCHED">Matched</option>
          <option value="QUEUED">Queued</option>
          <option value="matched">85%+ Matches</option>
        </select>
        <span className="text-sm text-gray-500">{jobs.length} jobs</span>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-8 text-gray-400">No jobs found. Click "Search LinkedIn Jobs" to start.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200 rounded-lg text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">#</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Company</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Role</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Location</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Match %</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Interview Prob</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {jobs.map((job, idx) => (
                <tr
                  key={job.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectJob(job)}
                >
                  <td className="px-3 py-2 text-gray-500">{idx + 1}</td>
                  <td className="px-3 py-2 font-medium text-gray-900">{job.company}</td>
                  <td className="px-3 py-2 text-gray-700 max-w-[250px] truncate">{job.title}</td>
                  <td className="px-3 py-2 text-gray-500 max-w-[150px] truncate">{job.location}</td>
                  <td className="px-3 py-2">
                    {job.match_score !== null ? (
                      <span className={`font-semibold ${job.match_score >= 85 ? 'text-green-600' : job.match_score >= 70 ? 'text-amber-600' : 'text-gray-500'}`}>
                        {job.match_score.toFixed(0)}%
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className={`px-3 py-2 ${probColors[job.interview_probability || ''] || 'text-gray-500'}`}>
                    {job.interview_probability || '-'}
                  </td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[job.status] || 'bg-gray-100'}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-xs"
                      onClick={(e) => e.stopPropagation()}
                    >
                      View
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
