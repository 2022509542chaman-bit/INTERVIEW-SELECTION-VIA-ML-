/**
 * Dashboard.tsx
 * Admin dashboard with stats, charts, and candidate table
 */

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Download, Trash2, Eye, MoreVertical } from 'lucide-react';

interface Candidate {
  id: number;
  name: string;
  total_score: number;
  decision: string;
  grade: string;
  star_rating: number;
  percentile: number;
  created_at: string;
}

interface DashboardStats {
  total: number;
  hired: number;
  borderline: number;
  rejected: number;
  avg_score: number;
  min_score: number;
  max_score: number;
  score_distribution: {
    [key: string]: number;
  };
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'score' | 'name'>('score');
  const [filterDecision, setFilterDecision] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, candidatesRes] = await Promise.all([
          fetch('/api/stats'),
          fetch('/api/candidates?limit=100'),
        ]);

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        if (candidatesRes.ok) {
          const candData = await candidatesRes.json();
          setCandidates(candData);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleExportCSV = async () => {
    try {
      const response = await fetch('/api/export/csv');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `candidates-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export CSV:', error);
    }
  };

  const handleDeleteCandidate = async (id: number) => {
    if (!confirm('Are you sure you want to delete this candidate?')) return;
    try {
      await fetch(`/api/candidates/${id}`, { method: 'DELETE' });
      setCandidates(candidates.filter((c) => c.id !== id));
    } catch (error) {
      console.error('Failed to delete candidate:', error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-screen text-gray-500">Loading...</div>;
  }

  const chartData = [
    { name: 'Selected', value: stats?.hired || 0, color: '#10b981' },
    { name: 'Borderline', value: stats?.borderline || 0, color: '#f59e0b' },
    { name: 'Rejected', value: stats?.rejected || 0, color: '#ef4444' },
  ];

  const filtered = filterDecision
    ? candidates.filter((c) => c.decision === filterDecision)
    : candidates;
  const sorted = [...filtered].sort((a, b) =>
    sortBy === 'score' ? b.total_score - a.total_score : a.name.localeCompare(b.name)
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            <Download size={20} />
            Export CSV
          </button>
        </div>

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-gray-600 text-sm font-medium mb-2">Total</div>
              <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
            </div>

            <div className="bg-green-50 rounded-lg shadow p-6 border-2 border-green-200">
              <div className="text-green-600 text-sm font-medium mb-2">Selected</div>
              <div className="text-3xl font-bold text-green-700">{stats.hired}</div>
            </div>

            <div className="bg-yellow-50 rounded-lg shadow p-6 border-2 border-yellow-200">
              <div className="text-yellow-600 text-sm font-medium mb-2">Borderline</div>
              <div className="text-3xl font-bold text-yellow-700">{stats.borderline}</div>
            </div>

            <div className="bg-red-50 rounded-lg shadow p-6 border-2 border-red-200">
              <div className="text-red-600 text-sm font-medium mb-2">Rejected</div>
              <div className="text-3xl font-bold text-red-700">{stats.rejected}</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-gray-600 text-sm font-medium mb-2">Avg Score</div>
              <div className="text-3xl font-bold text-blue-600">{stats.avg_score.toFixed(1)}%</div>
            </div>
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Pie Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Decision Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Score Distribution */}
          {stats && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Score Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={Object.entries(stats.score_distribution).map(([label, count]) => ({
                  range: label.replace('_', '-'),
                  count,
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Candidates Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-900">Candidates ({sorted.length})</h2>
            <div className="flex gap-2">
              <select
                value={filterDecision || ''}
                onChange={(e) => setFilterDecision(e.target.value || null)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="">All Decisions</option>
                <option value="SELECTED">Selected</option>
                <option value="BORDERLINE">Borderline</option>
                <option value="REJECTED">Rejected</option>
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'score' | 'name')}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="score">Sort by Score</option>
                <option value="name">Sort by Name</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Decision</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Percentile</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {sorted.map((candidate) => (
                  <tr key={candidate.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{candidate.name}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">{candidate.total_score.toFixed(1)}%</td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold ${
                          candidate.decision === 'SELECTED'
                            ? 'bg-green-100 text-green-800'
                            : candidate.decision === 'BORDERLINE'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {candidate.decision}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">{candidate.grade}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{candidate.percentile.toFixed(1)}th</td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleDeleteCandidate(candidate.id)}
                        className="text-red-600 hover:text-red-800 transition"
                      >
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
