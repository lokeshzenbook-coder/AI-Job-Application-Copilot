import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Application } from '../types';

export default function ApplicationTracker() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => { loadApplications(); }, [filter]);

  async function loadApplications() {
    setLoading(true);
    try {
      const params = filter === 'all' ? undefined : filter;
      const data = await api.getApplications(params);
      setApplications(data.applications);
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(id: number, action: 'prepare' | 'approve' | 'cancel') {
    try {
      switch (action) {
        case 'prepare': await api.prepareApplication(id); break;
        case 'approve':
          if (!confirm('Are you sure you want to approve this application for submission?')) return;
          await api.approveApplication(id);
          break;
        case 'cancel':
          if (!confirm('Cancel this application?')) return;
          await api.cancelApplication(id);
          break;
      }
      await loadApplications();
    } catch (err) {
      alert(`Failed: ${(err as Error).message}`);
    }
  }

  async function handleTailor(jobId: number) {
    try {
      await api.tailorResume(jobId);
      await loadApplications();
    } catch (err) {
      alert(`Tailor failed: ${(err as Error).message}`);
    }
  }

  async function handleCoverLetter(jobId: number) {
    try {
      await api.generateCoverLetter(jobId);
      await loadApplications();
    } catch (err) {
      alert(`Cover letter failed: ${(err as Error).message}`);
    }
  }

  const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
    QUEUED: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Queued' },
    READY_FOR_REVIEW: { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Ready for Review' },
    SUBMITTED: { bg: 'bg-cyan-100', text: 'text-cyan-700', label: 'Submitted' },
    REJECTED: { bg: 'bg-red-100', text: 'text-red-700', label: 'Rejected' },
    INTERVIEW: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Interview' },
    WITHDRAWN: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Withdrawn' },
  };

  return (
    <div>
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <h3 className="text-lg font-semibold text-gray-900">Applications ({applications.length})</h3>
        <div className="flex gap-1 ml-auto">
          {['all', 'QUEUED', 'READY_FOR_REVIEW', 'SUBMITTED', 'INTERVIEW'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {f === 'all' ? 'All' : statusConfig[f]?.label || f}
            </button>
          ))}
        </div>
        <button
          onClick={() => api.downloadExcel()}
          className="bg-green-600 text-white px-4 py-1.5 rounded-lg hover:bg-green-700 text-sm"
        >
          Export Excel
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      ) : applications.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg mb-2">No applications yet</p>
          <p className="text-sm">Search and analyze jobs first, then applications will appear here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app) => {
            const sc = statusConfig[app.status] || statusConfig.QUEUED;
            const isExpanded = expandedId === app.id;
            return (
              <div key={app.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                {/* Header row */}
                <div
                  className="flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpandedId(isExpanded ? null : app.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-900">{app.job?.company || 'Unknown'}</span>
                      <span className="text-gray-400">&middot;</span>
                      <span className="text-gray-700 truncate">{app.job?.title || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {app.job?.match_score && (
                        <span className={`font-semibold ${app.job.match_score >= 85 ? 'text-green-600' : 'text-amber-600'}`}>
                          {app.job.match_score.toFixed(0)}% match
                        </span>
                      )}
                      {app.job?.location && <span>{app.job.location}</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${sc.bg} ${sc.text}`}>
                      {sc.label}
                    </span>
                    <span className="text-gray-400 text-lg">{isExpanded ? '\u25B2' : '\u25BC'}</span>
                  </div>
                </div>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="border-t px-4 py-4 bg-gray-50 space-y-4">
                    {/* Resume & Cover Letter status */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white p-3 rounded border">
                        <div className="text-xs font-medium text-gray-500 mb-1">Tailored Resume</div>
                        {app.resume_version ? (
                          <div className="text-sm text-green-700">Generated</div>
                        ) : (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleTailor(app.job_id); }}
                            className="text-sm text-purple-600 hover:underline"
                          >
                            Generate Tailored Resume
                          </button>
                        )}
                      </div>
                      <div className="bg-white p-3 rounded border">
                        <div className="text-xs font-medium text-gray-500 mb-1">Cover Letter</div>
                        {app.cover_letter ? (
                          <div className="text-sm text-green-700">Generated</div>
                        ) : (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleCoverLetter(app.job_id); }}
                            className="text-sm text-teal-600 hover:underline"
                          >
                            Generate Cover Letter
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Cover letter preview */}
                    {app.cover_letter && (
                      <div className="bg-white p-3 rounded border">
                        <div className="text-xs font-medium text-gray-500 mb-1">Cover Letter Preview</div>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-4">{app.cover_letter}</p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2">
                      {app.status === 'QUEUED' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAction(app.id, 'prepare'); }}
                          className="bg-purple-600 text-white px-4 py-1.5 rounded-lg hover:bg-purple-700 text-sm"
                        >
                          Prepare for Review
                        </button>
                      )}
                      {app.status === 'READY_FOR_REVIEW' && (
                        <>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleAction(app.id, 'approve'); }}
                            className="bg-green-600 text-white px-4 py-1.5 rounded-lg hover:bg-green-700 text-sm"
                          >
                            Approve & Submit
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleAction(app.id, 'cancel'); }}
                            className="bg-red-100 text-red-700 px-4 py-1.5 rounded-lg hover:bg-red-200 text-sm"
                          >
                            Cancel
                          </button>
                        </>
                      )}
                      {app.job?.url && (
                        <a
                          href={app.job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-sm px-2 py-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View Job Posting
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
