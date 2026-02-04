import React from 'react';

const AnalyticsDashboard = () => {
  return (
    <div className="h-full overflow-y-auto p-2">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
            {/* Metric Card 1 */}
            <div className="p-6 bg-surface-900 border border-surface-800 rounded-lg shadow-sm">
                <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Total Detections</div>
                <div className="text-3xl font-mono text-white">1,204</div>
                <div className="text-success-500 text-xs mt-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">trending_up</span> +12% this week
                </div>
            </div>

            {/* Metric Card 2 */}
            <div className="p-6 bg-surface-900 border border-surface-800 rounded-lg shadow-sm">
                <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">False Positives</div>
                <div className="text-3xl font-mono text-white">2.4%</div>
                <div className="text-success-500 text-xs mt-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">arrow_downward</span> -0.5% improved
                </div>
            </div>

            {/* Metric Card 3 */}
            <div className="p-6 bg-surface-900 border border-surface-800 rounded-lg shadow-sm">
                 <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Avg Response Time</div>
                 <div className="text-3xl font-mono text-white">45s</div>
            </div>

            {/* Metric Card 4 */}
            <div className="p-6 bg-surface-900 border border-surface-800 rounded-lg shadow-sm">
                 <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">System Uptime</div>
                 <div className="text-3xl font-mono text-white">99.9%</div>
            </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-96">
            <div className="bg-surface-900 border border-surface-800 rounded-lg p-6 flex flex-col items-center justify-center text-slate-500">
                <span className="material-symbols-outlined text-4xl mb-2 opacity-50">bar_chart</span>
                <span className="text-sm">Threat Activity Graph (Placeholder)</span>
            </div>
            <div className="bg-surface-900 border border-surface-800 rounded-lg p-6 flex flex-col items-center justify-center text-slate-500">
                 <span className="material-symbols-outlined text-4xl mb-2 opacity-50">pie_chart</span>
                 <span className="text-sm">Incident Distribution (Placeholder)</span>
            </div>
        </div>
    </div>
  );
};

export default AnalyticsDashboard;
