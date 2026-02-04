import React, { useEffect, useRef } from 'react';

const LiveMonitor = ({ videoRef, startCamera, isActive, incidents }) => {
  const canvasRef = useRef(null);

  // Frame Transmission Logic
  useEffect(() => {
    let intervalId;

    const sendFrame = async () => {
        if (!isActive || !videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');

        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            // Draw video frame to canvas
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert to blob and send
            canvas.toBlob(async (blob) => {
                if (!blob) return;
                
                const formData = new FormData();
                formData.append('file', blob, 'frame.jpg');

                try {
                    await fetch('http://localhost:8000/analyze-frame', {
                        method: 'POST',
                        body: formData,
                    });
                    // System relies on WebSocket for response/alerts
                } catch (error) {
                    console.error("Frame transmission error:", error);
                }
            }, 'image/jpeg', 0.8);
        }
    };

    if (isActive) {
        // Send frames every 500ms (2 FPS) to balance load
        intervalId = setInterval(sendFrame, 500); 
    }

    return () => {
        if (intervalId) clearInterval(intervalId);
    };
  }, [isActive, videoRef]);

  return (
    <div className="w-full h-full flex gap-6">
      {/* Hidden Canvas for Frame Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* LEFT: MAIN HUD FRAME */}
      <div className="flex-1 relative rounded-2xl overflow-hidden bg-black border border-white/10 shadow-2xl group">
        
        {/* Video Element */}
        {isActive ? (
            <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover opacity-90" />
        ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-surface-950 to-black">
                {/* No Signal Animation */}
                <div className="text-center relative z-10">
                    <div className="size-24 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-6 border border-white/10 relative overflow-hidden">
                         <div className="absolute inset-0 border-t border-brand-500/50 rounded-full animate-spin duration-[3000ms]"></div>
                         <span className="material-symbols-outlined text-slate-600 text-4xl">videocam_off</span>
                    </div>
                    <h3 className="text-white font-bold text-xl tracking-wide mb-2">SIGNAL TERMINATED</h3>
                    <p className="text-sm text-slate-500 mb-8 max-w-xs mx-auto">Surveillance feed disconnected. Establish secure link to restore visuals.</p>
                    <button 
                        onClick={startCamera}
                        className="group relative px-8 py-3 bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-lg overflow-hidden transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] hover:shadow-[0_0_30px_rgba(37,99,235,0.6)]"
                    >
                        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 backdrop-blur-sm"></div>
                        <div className="relative flex items-center gap-2">
                             <span className="material-symbols-outlined animate-pulse">power_settings_new</span>
                             INITIALIZE FEED
                        </div>
                    </button>
                </div>
                {/* Background Grid Pattern */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px] opacity-20"></div>
            </div>
        )}

        {/* HUD OVERLAYS (Only visible when active) */}
        {isActive && (
            <>
                {/* Vignette & Scanlines */}
                <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle,transparent_50%,black_150%)]"></div>
                <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.1)_50%)] bg-[size:100%_4px] opacity-50"></div>
                
                {/* Animated Scanner Line */}
                <div className="absolute top-0 left-0 w-full h-1 bg-brand-500/30 shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-scan-y pointer-events-none"></div>

                {/* Corner Brackets */}
                <div className="absolute top-4 left-4 w-16 h-16 border-l-2 border-t-2 border-brand-500/50 rounded-tl-lg pointer-events-none"></div>
                <div className="absolute top-4 right-4 w-16 h-16 border-r-2 border-t-2 border-brand-500/50 rounded-tr-lg pointer-events-none"></div>
                <div className="absolute bottom-4 left-4 w-16 h-16 border-l-2 border-b-2 border-brand-500/50 rounded-bl-lg pointer-events-none"></div>
                <div className="absolute bottom-4 right-4 w-16 h-16 border-r-2 border-b-2 border-brand-500/50 rounded-br-lg pointer-events-none"></div>

                {/* Top Data Bar */}
                <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-start pointer-events-none">
                    <div className="flex gap-4">
                        <div className="bg-black/60 border border-white/10 backdrop-blur-md px-4 py-2 rounded-lg flex items-center gap-3 shadow-xl">
                            <span className="relative flex h-3 w-3">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-danger-400 opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-3 w-3 bg-danger-500"></span>
                            </span>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-slate-400 font-bold tracking-wider">STATUS</span>
                                <span className="text-xs font-mono font-bold text-white tracking-widest text-shadow-sm">LIVE FEED RECORDING</span>
                            </div>
                        </div>
                        <div className="hidden md:flex bg-black/60 border border-white/10 backdrop-blur-md px-4 py-2 rounded-lg items-center gap-3 shadow-xl">
                            <div className="flex flex-col border-r border-white/10 pr-3">
                                <span className="text-[10px] text-slate-400 font-bold">SOURCE</span>
                                <span className="text-xs font-mono text-brand-400">CAM-01: ALPHA</span>
                            </div>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-slate-400 font-bold">RESOLUTION</span>
                                <span className="text-xs font-mono text-white">4K UHD • 60FPS</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-2">
                         <div className="px-3 py-1 bg-brand-900/30 border border-brand-500/30 rounded text-[10px] font-mono text-brand-400 backdrop-blur-sm">System: SECURE</div>
                         <div className="px-3 py-1 bg-white/5 border border-white/10 rounded text-[10px] font-mono text-slate-300 backdrop-blur-sm">Encrypted: AES-256</div>
                    </div>
                </div>

                {/* Center Tactical Crosshair */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
                     <div className="relative size-32">
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 h-4 w-0.5 bg-white/50"></div>
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-4 w-0.5 bg-white/50"></div>
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-0.5 bg-white/50"></div>
                        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-0.5 bg-white/50"></div>
                        <div className="absolute inset-0 border border-dashed border-white/20 rounded-full animate-spin-slow"></div>
                     </div>
                </div>

                {/* Bottom Telemetry */}
                <div className="absolute bottom-6 left-8 right-8 flex justify-between items-end pointer-events-none">
                    <div className="bg-black/60 border border-white/10 backdrop-blur-md p-3 rounded-lg flex gap-6 shadow-xl">
                         <div>
                             <span className="block text-[10px] text-slate-500 font-bold">LATITUDE</span>
                             <span className="font-mono text-sm text-brand-300">34.0522° N</span>
                         </div>
                         <div>
                             <span className="block text-[10px] text-slate-500 font-bold">LONGITUDE</span>
                             <span className="font-mono text-sm text-brand-300">118.2437° W</span>
                         </div>
                         <div>
                             <span className="block text-[10px] text-slate-500 font-bold">ZOOM</span>
                             <span className="font-mono text-sm text-white">1.0x</span>
                         </div>
                    </div>
                </div>
            </>
        )}
      </div>

      {/* RIGHT: INTEL PANEL */}
      <div className="w-80 flex flex-col bg-[#0f1115] border border-white/5 rounded-2xl overflow-hidden shadow-2xl shrink-0 backdrop-blur-xl relative">
          <div className="p-4 border-b border-white/5 bg-white/2 flex items-center justify-between">
              <h3 className="font-bold text-white text-xs tracking-[0.2em] font-mono flex items-center gap-2">
                 <span className="size-2 rounded-sm bg-brand-500 shadow-[0_0_8px_#3b82f6]"></span>
                 INTELLIGENCE LOG
              </h3>
              <div className="flex gap-1">
                  <span className="size-1 bg-slate-600 rounded-full"></span>
                  <span className="size-1 bg-slate-600 rounded-full"></span>
                  <span className="size-1 bg-slate-600 rounded-full"></span>
              </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-3 relative no-scrollbar">
             {incidents.length === 0 ? (
                 <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-700 gap-4 opacity-70">
                    <div className="size-20 border border-dashed border-slate-700 rounded-full flex items-center justify-center animate-spin-slow">
                        <span className="material-symbols-outlined text-4xl">travel_explore</span>
                    </div>
                    <span className="text-xs font-mono uppercase tracking-widest">Scanning Local Area...</span>
                 </div>
             ) : (
                 incidents.map((inc, i) => (
                     <div key={i} className="relative p-4 bg-white/5 border border-white/5 rounded-lg hover:bg-white/10 hover:border-brand-500/30 transition-all duration-300 group cursor-pointer overflow-hidden">
                        {/* Urgent Glow for Critical */}
                        <div className={`absolute top-0 left-0 w-0.5 h-full ${inc.label?.includes('Weapon') ? 'bg-danger-500 shadow-[0_0_10px_#ef4444]' : 'bg-warning-500'}`}></div>
                        
                        <div className="flex justify-between items-start mb-2 pl-2">
                            <span className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded ${
                                inc.label?.includes('Weapon') 
                                ? 'bg-danger-900/40 text-danger-400 border border-danger-500/20' 
                                : 'bg-warning-900/40 text-warning-400 border border-warning-500/20'
                            }`}>
                                {inc.label || "THREAT DETECTED"}
                            </span>
                            <span className="text-[10px] text-slate-500 font-mono">{new Date(inc.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div className="pl-2">
                            <p className="text-xs text-slate-300 font-medium leading-relaxed">
                                Abnormality detected in Sector 4.
                            </p>
                            <div className="mt-2 flex items-center gap-2">
                                <div className="h-1 flex-1 bg-white/10 rounded-full overflow-hidden">
                                     <div className="h-full bg-brand-500 w-[88%] shadow-[0_0_8px_#3b82f6]"></div>
                                </div>
                                <span className="text-[10px] font-mono text-brand-400">88% CONF</span>
                            </div>
                        </div>
                     </div>
                 ))
             )}
          </div>
          
          {/* Quick Actions Footer */}
          <div className="p-4 border-t border-white/10 grid grid-cols-2 gap-3 bg-black/40">
               <button className="px-4 py-2.5 rounded-lg bg-surface-800 text-xs font-bold text-slate-400 hover:text-white border border-transparent hover:border-slate-600 transition-all flex items-center justify-center gap-2 group">
                  <span className="material-symbols-outlined text-sm group-hover:animate-pulse">lock</span> LOCKDOWN
               </button>
               <button className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-danger-900 to-danger-800 text-xs font-bold text-white border border-danger-700/50 hover:shadow-[0_0_15px_rgba(239,68,68,0.4)] transition-all flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-sm">notifications_active</span> DISPATCH
               </button>
          </div>
      </div>
    </div>
  );
};

export default LiveMonitor;
