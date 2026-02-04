import React, { useState } from 'react';

const IncidentHistory = ({ incidents = [] }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data if empty
  const displayIncidents = incidents.length > 0 ? incidents : [
      { id: 1, type: 'WEAPON_DETECTED', location: 'Lobby North', confidence: 0.98, timestamp: new Date(), status: 'CRITICAL', zone: 'Zone A' },
      { id: 2, type: 'VIOLENCE_DETECTED', location: 'Parking P2', confidence: 0.85, timestamp: new Date(Date.now() - 3600000), status: 'WARNING', zone: 'Zone C' }
  ];

  const filtered = displayIncidents.filter(inc => {
      if(filter !== 'all' && inc.status !== filter) return false;
      if(searchTerm && !inc.type.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
  });

  return (
    <div className="h-full flex flex-col gap-4">
      {/* 1. Toolbar */}
      <div className="flex items-center justify-between p-4 bg-surface-900 border border-surface-800 rounded-lg shadow-sm">
          <div className="flex gap-2">
             <button 
                onClick={() => setFilter('all')}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${filter === 'all' ? 'bg-surface-700 text-white' : 'text-slate-400 hover:text-white'}`}
             >
                 All Events
             </button>
             <button 
                onClick={() => setFilter('CRITICAL')}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${filter === 'CRITICAL' ? 'bg-danger-900/30 text-danger-500 border border-danger-500/20' : 'text-slate-400 hover:text-danger-500'}`}
             >
                 Critical
             </button>
             <button 
                onClick={() => setFilter('WARNING')}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${filter === 'WARNING' ? 'bg-warning-500/10 text-warning-500 border border-warning-500/20' : 'text-slate-400 hover:text-warning-500'}`}
             >
                 Warnings
             </button>
          </div>

          <div className="relative">
             <span className="material-symbols-outlined absolute left-3 top-2 text-slate-500 text-sm">search</span>
             <input 
                type="text" 
                placeholder="Search logs..." 
                className="pl-8 pr-4 py-1.5 bg-surface-950 border border-surface-700 rounded text-sm text-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none w-64"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
             />
          </div>
      </div>

      {/* 2. Data Table */}
      <div className="flex-1 bg-surface-900 border border-surface-800 rounded-lg overflow-hidden shadow-sm flex flex-col">
          <div className="grid grid-cols-12 bg-surface-800 p-3 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-surface-700">
              <div className="col-span-2">Timestamp</div>
              <div className="col-span-3">Event Type</div>
              <div className="col-span-2">Location / Zone</div>
              <div className="col-span-2">Confidence</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-1 text-right">Actions</div>
          </div>

          <div className="divide-y divide-surface-800 overflow-y-auto">
              {filtered.map((incident, idx) => (
                  <div key={idx} className="grid grid-cols-12 p-4 text-sm hover:bg-surface-800 transition-colors group items-center">
                       <div className="col-span-2 font-mono text-slate-400 text-xs">
                           {new Date(incident.timestamp).toLocaleTimeString()} <span className="text-slate-600">{new Date(incident.timestamp).toLocaleDateString()}</span>
                       </div>
                       
                       <div className="col-span-3 font-medium text-slate-200 flex items-center gap-2">
                           <span className={`size-2 rounded-full ${incident.status === 'CRITICAL' ? 'bg-danger-500' : 'bg-warning-500'}`}></span>
                           {incident.type || incident.label}
                       </div>
                       
                       <div className="col-span-2 text-slate-400">
                           {incident.location || incident.zone || 'Unknown'}
                       </div>

                       <div className="col-span-2">
                           <div className="w-24 h-1.5 bg-surface-950 rounded-full overflow-hidden">
                               <div 
                                 className={`h-full ${incident.confidence > 0.9 ? 'bg-success-500' : 'bg-warning-500'}`} 
                                 style={{ width: `${(incident.confidence || 0.8) * 100}%` }}
                               ></div>
                           </div>
                           <span className="text-[10px] text-slate-500 mt-1 block">{(incident.confidence * 100).toFixed(0)}% Match</span>
                       </div>

                       <div className="col-span-2">
                           <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                               incident.status === 'CRITICAL' 
                               ? 'bg-danger-900/20 text-danger-500 border-danger-500/20' 
                               : 'bg-warning-500/10 text-warning-500 border-warning-500/20'
                           }`}>
                               {incident.status || 'INVESTIGATE'}
                           </span>
                       </div>

                       <div className="col-span-1 text-right opacity-0 group-hover:opacity-100 transition-opacity">
                           <button className="text-slate-400 hover:text-white p-1">
                               <span className="material-symbols-outlined text-lg">visibility</span>
                           </button>
                       </div>
                  </div>
              ))}
              
              {filtered.length === 0 && (
                  <div className="p-8 text-center text-slate-500">
                      No incidents found matching current filters.
                  </div>
              )}
          </div>
          
          <div className="p-2 border-t border-surface-800 bg-surface-900 text-[10px] text-slate-500 flex justify-between px-4">
              <span>Showing {filtered.length} records</span>
              <div className="flex gap-2">
                  <span className="hover:text-slate-300 cursor-pointer">Previous</span>
                  <span className="hover:text-slate-300 cursor-pointer">Next</span>
              </div>
          </div>
      </div>
    </div>
  );
};

export default IncidentHistory;
