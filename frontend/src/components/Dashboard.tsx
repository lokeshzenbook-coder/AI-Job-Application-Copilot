import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { DashboardStats } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const data = await api.getDashboard();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="text-center py-8 text-gray-500">Loading dashboard...</div>;
  if (!stats) return <div className="text-center py-8 text-red-500">Failed to load dashboard</div>;

  const cards = [
    { label: 'Jobs Discovered', value: stats.total_jobs, color: 'bg-blue-500' },
    { label: 'Jobs < 24h', value: stats.jobs_last_24h, color: 'bg-indigo-500' },
    { label: 'Unique Jobs', value: stats.unique_jobs, color: 'bg-violet-500' },
    { label: '85%+ Matches', value: stats.strong_matches, color: 'bg-green-500' },
    { label: 'Applications Ready', value: stats.applications_ready, color: 'bg-amber-500' },
    { label: 'Submitted', value: stats.submitted, color: 'bg-cyan-500' },
    { label: 'Interviews', value: stats.interviews, color: 'bg-emerald-500' },
    { label: 'Rejected', value: stats.rejected, color: 'bg-red-400' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-white rounded-lg shadow p-4 border border-gray-100">
          <div className={`text-xs font-medium text-white ${card.color} inline-block px-2 py-0.5 rounded mb-2`}>
            {card.label}
          </div>
          <div className="text-3xl font-bold text-gray-900">{card.value}</div>
        </div>
      ))}
    </div>
  );
}
