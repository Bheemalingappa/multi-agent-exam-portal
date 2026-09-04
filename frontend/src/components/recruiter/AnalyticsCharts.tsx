import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { AnalyticsSummary } from '../../types/analytics';

interface AnalyticsChartsProps {
  analytics: AnalyticsSummary;
}

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({ analytics }) => {
  const scoreData = [
    { name: 'Average Final Score', score: analytics.average_final_score || 0 },
    { name: 'Avg Functional Score', score: analytics.average_functional_score || 0 },
  ];

  const pieData = [
    { name: 'Completed Submissions', value: analytics.completed_submissions || 1 },
    { name: 'Failed Submissions', value: analytics.failed_submissions || 0 },
  ];

  const COLORS = ['#10b981', '#f43f5e'];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Bar Chart */}
      <div className="bg-slate-850 p-6 rounded-xl border border-slate-700">
        <h4 className="text-sm font-semibold text-slate-300 mb-4">Candidate Performance Metrics</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scoreData}>
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={12} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
              <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pie Chart */}
      <div className="bg-slate-850 p-6 rounded-xl border border-slate-700">
        <h4 className="text-sm font-semibold text-slate-300 mb-4">Submission Status Breakdown</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
