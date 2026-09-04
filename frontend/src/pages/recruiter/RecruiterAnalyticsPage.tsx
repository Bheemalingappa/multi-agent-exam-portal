import React, { useEffect, useState } from 'react';
import { getAnalyticsDashboardApi } from '../../api/submissions';
import { AnalyticsSummary } from '../../types/analytics';
import { AnalyticsCharts } from '../../components/recruiter/AnalyticsCharts';
import { BarChart2, Loader2 } from 'lucide-react';

export const RecruiterAnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const res = await getAnalyticsDashboardApi();
        setAnalytics(res.analytics);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart2 className="w-6 h-6 text-emerald-400" /> Platform Analytics & Score Metrics
        </h1>
        <p className="text-xs text-slate-400">Detailed visualizations of score distributions, sandbox latency, and candidate pass rates.</p>
      </div>

      {analytics && <AnalyticsCharts analytics={analytics} />}
    </div>
  );
};
