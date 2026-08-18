import { useState } from 'react';
import { api } from '../api/client';
import type { Job } from '../types';

interface Props {
  job: Job;
  onClose: () => void;
  onRefresh: () => void;
}

export default function JobDetail({ job, onClose, onRefresh }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const mandatoryGaps = JSON.parse(job.mandatory_gaps || '[]');
  const niceGaps = JSON.parse(job.nice_to_have_gaps || '[]');

  async function handleAction(action: string) {
    setLoading(action);
    try {
      let res;
      switch (action) {
        case 'analyze':
          res = await api.analyzeJob(job.id);
          break;
        case 'tailor':
          res = await api.tailorResume(job.id);
          break;
        case 'cover':
          res = await api.generateCoverLetter(job.id);
          break;
      }
      setResult(res);
      onRefresh();
    } catch (err) {
      alert(`Failed: ${(err as Error).message}`);
    } finally {
      setLoading(null);
    }
  }

  const skillScores = [
    { label: 'Experience', score: job.experience_match },
    { label: 'AWS', score: job.aws_match },
    { label: 'Kubernetes', score: job.kubernetes_match },
    { label: 'Terraform', score: job.terraform_match },
    { label: 'CI/CD', score: job.cicd_match },
    { label: 'DevSecOps', score: job.devsecops_match },
    { label: 'Python', score: job.python_match },
    { label: 'GitOps', score: job.gitops_match },
  ];

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-start justify-center pt-8 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full mx-4 mb-8 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-start rounded-t-xl">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{job.title}</h2>
            <p className="text-gray-600">{job.company} &middot; {job.location}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        <div className="p-6 space-y-6">
          {/* Match Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{job.match_score !== null ? `${job.match_score.toFixed(0)}%` : '-'}</div>
              <div className="text-xs text-gray-500">Match Score</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{job.interview_probability || '-'}</div>
              <div className="text-xs text-gray-500">Interview Probability</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{job.recommendation || '-'}</div>
              <div className="text-xs text-gray-500">Recommendation</div>
            </div>
          </div>

          {/* Skill Scores */}
          {skillScores.some((s) => s.score !== null) && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Skill Breakdown</h3>
              <div className="space-y-2">
                {skillScores.map((s) => s.score !== null && (
                  <div key={s.label} className="flex items-center gap-2">
                    <span className="w-24 text-xs text-gray-600">{s.label}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${s.score >= 85 ? 'bg-green-500' : s.score >= 70 ? 'bg-amber-500' : 'bg-red-400'}`}
                        style={{ width: `${s.score}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-700 w-10 text-right">{s.score}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gaps */}
          {(mandatoryGaps.length > 0 || niceGaps.length > 0) && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Skill Gaps</h3>
              {mandatoryGaps.length > 0 && (
                <div className="mb-2">
                  <span className="text-xs font-medium text-red-600">Mandatory Gaps:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {mandatoryGaps.map((g: string) => (
                      <span key={g} className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">{g}</span>
                    ))}
                  </div>
                </div>
              )}
              {niceGaps.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-amber-600">Nice-to-have Gaps:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {niceGaps.map((g: string) => (
                      <span key={g} className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs">{g}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Reason */}
          {job.match_reason && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-1">Match Reason</h3>
              <p className="text-sm text-gray-600">{job.match_reason}</p>
            </div>
          )}

          {/* Job Description */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-1">Job Description</h3>
            <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg max-h-60 overflow-y-auto whitespace-pre-wrap">
              {job.description || 'No description available'}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => handleAction('analyze')}
              disabled={loading !== null}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
            >
              {loading === 'analyze' ? 'Analyzing...' : 'Analyze Job'}
            </button>
            <button
              onClick={() => handleAction('tailor')}
              disabled={loading !== null}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 text-sm"
            >
              {loading === 'tailor' ? 'Tailoring...' : 'Tailor Resume'}
            </button>
            <button
              onClick={() => handleAction('cover')}
              disabled={loading !== null}
              className="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 disabled:opacity-50 text-sm"
            >
              {loading === 'cover' ? 'Generating...' : 'Generate Cover Letter'}
            </button>
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 text-sm"
            >
              Open Job Posting
            </a>
          </div>

          {/* Result */}
          {result && (
            <div className="bg-green-50 border border-green-200 p-4 rounded-lg text-sm">
              <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
