import { useState } from 'react';
import Dashboard from './components/Dashboard';
import JobTable from './components/JobTable';
import JobDetail from './components/JobDetail';
import ResumeUpload from './components/ResumeUpload';
import ApplicationTracker from './components/ApplicationTracker';
import { api } from './api/client';
import type { Job } from './types';

type Tab = 'dashboard' | 'jobs' | 'applications';

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  function refresh() {
    setRefreshKey((k) => k + 1);
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'jobs', label: 'Jobs' },
    { key: 'applications', label: 'Applications' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-gray-900">AI Job Copilot</h1>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">DevOps / DevSecOps</span>
          </div>
          <button
            onClick={() => api.downloadExcel()}
            className="bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700 text-sm"
          >
            Export Excel
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 flex gap-1">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {tab === 'dashboard' && (
          <div className="space-y-6">
            <Dashboard key={`dash-${refreshKey}`} />
            <ResumeUpload onResumeUploaded={refresh} />
          </div>
        )}
        {tab === 'jobs' && (
          <JobTable key={`jobs-${refreshKey}`} onSelectJob={setSelectedJob} />
        )}
        {tab === 'applications' && (
          <ApplicationTracker key={`apps-${refreshKey}`} />
        )}
      </main>

      {/* Job Detail Modal */}
      {selectedJob && (
        <JobDetail
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onRefresh={refresh}
        />
      )}
    </div>
  );
}
