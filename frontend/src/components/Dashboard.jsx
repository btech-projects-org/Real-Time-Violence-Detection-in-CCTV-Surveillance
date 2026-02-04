import React, { useState, useEffect, useRef } from 'react';
import LiveMonitor from './LiveMonitor';
import IncidentHistory from './IncidentHistory';
import AnalyticsDashboard from './AnalyticsDashboard';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('live'); // 'live', 'incidents', 'analytics'
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);
  const [incidents, setIncidents] = useState([]);
  const [isCameraActive, setIsCameraActive] = useState(false); // Fix: State for UI update
  
  // Refs
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);

  // 1. Camera Logic
  useEffect(() => {
    async function getCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === 'videoinput');
            setCameras(videoDevices);
            if(videoDevices.length) setSelectedCamera(videoDevices[0].deviceId);
        } catch(e) { console.error(e); }
    }
    getCameras();

    return () => {
        if(streamRef.current) stopCamera();
    }
  }, []);

  // Fix: Attach stream to video element AFTER it mounts (when isCameraActive becomes true)
  useEffect(() => {
    if (isCameraActive && videoRef.current && streamRef.current) {
        videoRef.current.srcObject = streamRef.current;
    }
  }, [isCameraActive]);

  // 2. WebSocket Logic
  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;
    let isMounted = true;

    const connectWS = () => {
        if (!isMounted) return;
        
        ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onopen = () => {
            console.log("WS Connected");
        };

        ws.onmessage = (event) => {
            if (!isMounted) return;
            try {
                const data = JSON.parse(event.data);
                const newIncident = { ...data, timestamp: new Date() };
                setIncidents(prev => [newIncident, ...prev].slice(0, 50));
            } catch (e) { console.error("WS Parse Error", e); }
        };

        ws.onclose = () => {
            if (isMounted) {
                console.log("WS Closed. Reconnecting...");
                reconnectTimeout = setTimeout(connectWS, 3000);
            }
        };

        ws.onError = (err) => {
            console.error("WS Error", err);
            if(ws) ws.close();
        };

        wsRef.current = ws;
    };

    connectWS();

    return () => {
        isMounted = false;
        if (reconnectTimeout) clearTimeout(reconnectTimeout);
        if (ws) {
            ws.onclose = null; // Prevent reconnect trigger
            
            // Fix: Check state to prevent "WebSocket is closed before the connection is established" warning
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                ws.close();
            }
        }
    }
  }, []);

  const startCamera = async () => {
    if (streamRef.current) stopCamera();
    try {
        const constraints = { video: selectedCamera ? { deviceId: { exact: selectedCamera } } : true };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;
        if(videoRef.current) videoRef.current.srcObject = stream;
        setIsCameraActive(true); // Trigger re-render
    } catch(err) {
        console.error("Camera Error", err);
    }
  };

  const stopCamera = () => {
      if(streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
      if(videoRef.current) videoRef.current.srcObject = null;
      setIsCameraActive(false); // Trigger re-render
  };

  // Nav Item Helper
  const NavItem = ({ id, icon, label }) => {
      const isActive = activeView === id;
      return (
          <button 
            onClick={() => setActiveView(id)}
            className={`w-full flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden ${
                isActive 
                ? 'bg-gradient-to-r from-brand-600 to-brand-700 text-white shadow-[0_0_20px_rgba(59,130,246,0.5)] border border-brand-500/50' 
                : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'
            }`}
            title={isSidebarCollapsed ? label : ''}
          >
              {/* Glow Effect for active item */}
              {isActive && <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent skew-x-12 animate-shimmer"></div>}
              
              <span className={`material-symbols-outlined text-[24px] z-10 ${isActive ? 'text-white' : 'text-slate-500 group-hover:text-white transition-colors'}`}>{icon}</span>
              
              {!isSidebarCollapsed && (
                  <span className="text-sm font-medium tracking-wide z-10 whitespace-nowrap opacity-0 animate-fade-in-right" style={{animationFillMode: 'forwards'}}>
                      {label}
                  </span>
              )}
          </button>
      );
  }

  return (
    <div className="flex h-screen w-screen bg-[#05070a] text-slate-200 overflow-hidden font-sans selection:bg-brand-500 selection:text-white relative">
      
      {/* Background Gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-surface-900 via-[#05070a] to-black pointer-events-none"></div>
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-brand-900/10 blur-[120px] rounded-full pointer-events-none mix-blend-screen"></div>

      {/* 1. SIDEBAR NAVIGATION */}
      <aside 
        className={`${isSidebarCollapsed ? 'w-20' : 'w-72'} shrink-0 flex flex-col border-r border-white/5 bg-[#0a0c10]/80 backdrop-blur-xl transition-all duration-500 z-50 relative shadow-2xl`}
      >
        {/* Logo Area */}
        <div className="h-20 flex items-center justify-center border-b border-white/5 relative overflow-hidden">
             
             <div 
                className="relative z-10 flex items-center gap-3 cursor-pointer group"
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
             >
                 <div className="size-10 bg-gradient-to-br from-brand-500 to-brand-700 rounded-lg flex items-center justify-center text-white shadow-[0_0_15px_rgba(59,130,246,0.4)] group-hover:shadow-[0_0_25px_rgba(59,130,246,0.6)] transition-all duration-300">
                    <span className="material-symbols-outlined text-2xl">security</span>
                 </div>
                 {!isSidebarCollapsed && (
                     <div className="animate-fade-in-right">
                        <h1 className="font-bold text-white tracking-tight leading-none text-lg">SENTINEL<span className="text-brand-500">AI</span></h1>
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="size-1.5 rounded-full bg-success-500 animate-pulse"></span>
                            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">System Active</span>
                        </div>
                     </div>
                 )}
             </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-3 py-6 space-y-2">
            <NavItem id="live" icon="videocam" label="Live Surveillance" />
            <NavItem id="incidents" icon="history" label="Incident Logs" />
            <NavItem id="analytics" icon="analytics" label="Intelligence" />
            
            <div className="my-6 border-t border-white/5 mx-2"></div>
            
            <NavItem id="settings" icon="settings" label="Configuration" />
        </nav>

        {/* User Profile / Footer */}
        <div className="p-4 border-t border-white/5 bg-white/2">
            <button className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'justify-start gap-3'} p-2 rounded-lg hover:bg-white/5 transition-all group`}>
                <div className="size-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-600 border border-white/10 flex items-center justify-center shadow-lg">
                    <span className="material-symbols-outlined text-sm text-slate-300">person</span>
                </div>
                {!isSidebarCollapsed && (
                    <div className="text-left overflow-hidden">
                        <p className="text-sm font-bold text-slate-200">Admin Officer</p>
                        <p className="text-xs text-slate-500">Security Level 5</p>
                    </div>
                )}
            </button>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col relative overflow-hidden z-10">
        
        {/* Top Header Bar */}
        <header className="h-16 shrink-0 border-b border-white/5 bg-[#0a0c10]/50 backdrop-blur-md flex items-center justify-between px-8 z-40">
            {/* Breadcrumb / Title */}
            <div className="flex-1">
                 <h2 className="text-xl font-medium text-white tracking-wide flex items-center gap-3">
                    <span className="text-slate-500 font-normal">Console</span>
                    <span className="material-symbols-outlined text-slate-600 text-sm">arrow_forward_ios</span>
                    <span className="font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                        {activeView === 'live' && 'Live Surveillance Monitor'}
                        {activeView === 'incidents' && 'Incident History Log'}
                        {activeView === 'analytics' && 'Intelligence Dashboard'}
                    </span>
                 </h2>
            </div>
            
            {/* Status Modules */}
            <div className="flex items-center gap-6">
                {/* Weather / Env Mock */}
                <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-slate-400 bg-white/5 px-3 py-1.5 rounded-full border border-white/5">
                    <span className="material-symbols-outlined text-sm">cloud</span>
                    <span>24°C • CLOUDY</span>
                </div>

                {/* Connection Status */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/40 border border-white/5 backdrop-blur-md">
                    <div className={`size-2 rounded-full ${wsRef.current?.readyState === 1 ? 'bg-success-500 shadow-[0_0_10px_#22c55e]' : 'bg-red-500'} transition-all duration-500`}></div>
                    <span className="text-xs font-mono font-bold tracking-wider text-slate-300">
                        {wsRef.current?.readyState === 1 ? 'NETWORK SECURE' : 'OFFLINE'}
                    </span>
                </div>

                {/* Clock */}
                <div className="text-right">
                    <p className="text-lg font-bold text-white leading-none font-mono tracking-widest">{new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                    <p className="text-[10px] text-brand-500 uppercase tracking-[0.2em] font-bold">System Time</p>
                </div>
            </div>
        </header>

        {/* Content Viewport */}
        <div className="flex-1 overflow-hidden relative p-6">
             {activeView === 'live' && (
                <LiveMonitor 
                    videoRef={videoRef}
                    startCamera={startCamera} 
                    isActive={isCameraActive}
                    incidents={incidents}
                />
             )}
             {activeView === 'incidents' && <IncidentHistory incidents={incidents} />}
             {activeView === 'analytics' && <AnalyticsDashboard incidents={incidents} />}
        </div>

      </main>
    </div>
  );
};

export default Dashboard;
