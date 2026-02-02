import { useState, useEffect, useRef } from 'react';

export default function Dashboard() {
  const [incidents, setIncidents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [cameras, setCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState('');
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);
  const canvasRef = useRef(null);
  const analysisIntervalRef = useRef(null);

  // Get available cameras
  const getCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      console.log('Available cameras:', videoDevices);
      setCameras(videoDevices);
      
      // Auto-select first camera (usually laptop camera)
      if (videoDevices.length > 0) {
        setSelectedCamera(videoDevices[0].deviceId);
        console.log('Auto-selected camera:', videoDevices[0].label);
      }
    } catch (err) {
      console.error('Error enumerating cameras:', err);
    }
  };

  // Stop camera
  const stopCamera = () => {
    console.log('Stopping camera...');
    
    // Stop frame analysis
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
      analysisIntervalRef.current = null;
      console.log('Stopped frame analysis');
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('Stopped track:', track.label);
      });
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setCameraError('');
    console.log('✅ Camera stopped');
  };

  // Send frame to backend for analysis
  const sendFrameForAnalysis = async () => {
    // Check if video element and stream exist (don't rely on state due to closure)
    if (!videoRef.current || !streamRef.current) {
      console.log('⚠️ Skipping frame analysis - camera not active');
      return;
    }
    
    const video = videoRef.current;
    
    // Check if video is ready
    if (video.videoWidth === 0 || video.videoHeight === 0 || video.readyState < 2) {
      console.log('⚠️ Video not ready yet, skipping this frame');
      return;
    }
    
    try {
      console.log('📸 Capturing frame for analysis...');
      
      // Create canvas to capture frame
      if (!canvasRef.current) {
        canvasRef.current = document.createElement('canvas');
      }
      
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      console.log(`✅ Frame captured: ${canvas.width}x${canvas.height}`);
      
      // Convert to blob
      canvas.toBlob(async (blob) => {
        if (!blob) {
          console.error('❌ Failed to create blob from canvas');
          return;
        }
        
        console.log(`📤 Sending frame to backend (${(blob.size / 1024).toFixed(2)} KB)...`);
        
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');
        
        try {
          // Send to backend
          const response = await fetch('http://localhost:8000/analyze-frame', {
            method: 'POST',
            body: formData
          });
          
          if (!response.ok) {
            console.error(`❌ Backend error: ${response.status} ${response.statusText}`);
            return;
          }
          
          const result = await response.json();
          
          console.log('📊 Analysis result:', result);
          
          if (result.detected) {
            console.log('🚨 THREAT DETECTED:', result.type);
            console.log('   Confidence:', (result.confidence * 100).toFixed(1) + '%');
            console.log('   Description:', result.description);
            if (result.angry_face) console.log('   😡 Angry face detected!');
            if (result.weapon) console.log('   🔫 Weapon detected!');
          } else {
            console.log('✅ No threats - normal activity');
          }
        } catch (fetchErr) {
          console.error('❌ Network error sending frame:', fetchErr);
        }
      }, 'image/jpeg', 0.8);
      
    } catch (err) {
      console.error('❌ Error in sendFrameForAnalysis:', err);
    }
  };

  // Start camera with low resolution fallback
  const startCameraLowRes = async () => {
    try {
      console.log('Trying lower resolution...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 }
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setCameraError('');
        console.log('✅ Camera started with lower resolution');
        
        // Start sending frames for analysis every 3 seconds
        analysisIntervalRef.current = setInterval(sendFrameForAnalysis, 3000);
        console.log('Started frame analysis (every 3 seconds)');
      }
    } catch (err) {
      console.error('❌ Low resolution camera error:', err);
      let errorMessage = 'Failed to start camera: ' + err.message;
      
      if (err.name === 'NotReadableError') {
        errorMessage = 'Camera is being used by another application.\n\nPlease close:\n• Microsoft Teams\n• Zoom\n• Skype\n• Discord (if video enabled)\n• Other browser tabs using camera\n• Windows Camera app\n• OBS Studio\n\nThen refresh this page.';
      }
      
      setCameraError(errorMessage);
      setCameraActive(false);
    }
  };

  // Start camera
  const startCamera = async () => {
    try {
      console.log('Starting camera...');
      setCameraError('');

      // Get available cameras first
      await getCameras();

      // Stop existing stream if any
      if (streamRef.current) {
        stopCamera();
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      console.log('Requesting camera access...');
      
      const constraints = {
        video: selectedCamera 
          ? { deviceId: { exact: selectedCamera } }
          : { 
              facingMode: 'user',
              width: { ideal: 1280 },
              height: { ideal: 720 }
            },
        audio: false
      };

      console.log('Camera constraints:', constraints);

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      const videoTrack = stream.getVideoTracks()[0];
      console.log('📹 Camera started:', {
        label: videoTrack.label,
        id: videoTrack.id,
        settings: videoTrack.getSettings()
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setCameraError('');
        console.log('✅ Laptop camera started successfully!');
        
        // Start sending frames for analysis every 3 seconds
        analysisIntervalRef.current = setInterval(sendFrameForAnalysis, 3000);
        console.log('Started frame analysis (every 3 seconds)');
      }
    } catch (err) {
      console.error('❌ Camera error:', err);
      
      if (err.name === 'OverconstrainedError') {
        console.log('Constraints not supported, trying fallback...');
        await startCameraLowRes();
      } else {
        let errorMessage = 'Failed to start camera: ' + err.message;
        
        if (err.name === 'NotReadableError') {
          errorMessage = 'Camera is being used by another application.\n\nPlease close:\n• Microsoft Teams\n• Zoom\n• Skype\n• Discord (if video enabled)\n• Other browser tabs using camera\n• Windows Camera app\n• OBS Studio\n\nThen refresh this page.';
        } else if (err.name === 'NotFoundError') {
          errorMessage = 'No camera found on this device.';
        } else if (err.name === 'NotAllowedError') {
          errorMessage = 'Camera permission denied. Please allow camera access.';
        }
        
        setCameraError(errorMessage);
        setCameraActive(false);
      }
    }
  };

  // Toggle camera
  const toggleCamera = () => {
    console.log('Toggle camera clicked. Current state:', cameraActive);
    if (cameraActive) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  // Connect to WebSocket
  const connectWebSocket = () => {
    console.log('Connecting to WebSocket...');
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Alert received:', data);
      setIncidents(prev => [data, ...prev].slice(0, 10));
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected, reconnecting in 5s...');
      setConnected(false);
      setTimeout(connectWebSocket, 5000);
    };
    
    wsRef.current = ws;
  };

  // Initialize on mount
  useEffect(() => {
    connectWebSocket();
    getCameras();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      stopCamera();
    };
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#e2e8f0', fontFamily: 'system-ui' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#1e293b', padding: '1rem 1.5rem', borderBottom: '1px solid #334155' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1400px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f1f5f9' }}>🎥 Laptop Camera - Violence Detection</h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.875rem' }}>
              WebSocket: {connected ? <span style={{ color: '#22c55e' }}>● Connected</span> : <span style={{ color: '#ef4444' }}>● Disconnected</span>}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
          
          {/* Left Column - Camera */}
          <div>
            <div style={{ backgroundColor: '#1e293b', borderRadius: '0.5rem', padding: '1.5rem', border: '1px solid #334155' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Live Camera Feed</h2>
              
              {/* Camera Selector */}
              {cameras.length > 1 && (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: '#94a3b8' }}>
                    Select Camera:
                  </label>
                  <select 
                    value={selectedCamera}
                    onChange={(e) => setSelectedCamera(e.target.value)}
                    style={{ 
                      width: '100%', 
                      padding: '0.5rem', 
                      backgroundColor: '#0f172a', 
                      color: '#e2e8f0', 
                      border: '1px solid #334155', 
                      borderRadius: '0.375rem',
                      fontSize: '0.875rem'
                    }}
                  >
                    {cameras.map((camera, index) => (
                      <option key={camera.deviceId} value={camera.deviceId}>
                        {camera.label || `Camera ${index + 1}`}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              
              {/* Video Element */}
              <div style={{ position: 'relative', backgroundColor: '#000', borderRadius: '0.375rem', overflow: 'hidden', marginBottom: '1rem' }}>
                <video 
                  ref={videoRef}
                  autoPlay 
                  playsInline
                  muted
                  style={{ 
                    width: '100%', 
                    height: 'auto', 
                    display: 'block',
                    minHeight: '400px',
                    objectFit: 'contain'
                  }}
                />
                {!cameraActive && (
                  <div style={{ 
                    position: 'absolute', 
                    top: 0, 
                    left: 0, 
                    right: 0, 
                    bottom: 0, 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    color: '#64748b',
                    fontSize: '1rem'
                  }}>
                    Camera inactive
                  </div>
                )}
              </div>

              {/* Camera Control Button */}
              <button
                onClick={toggleCamera}
                style={{
                  width: '100%',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: cameraActive ? '#dc2626' : '#22c55e',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '1rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseOver={(e) => e.target.style.opacity = '0.9'}
                onMouseOut={(e) => e.target.style.opacity = '1'}
              >
                {cameraActive ? '⏸ Stop Camera' : '▶ Start Camera'}
              </button>

              {/* Error Display */}
              {cameraError && (
                <div style={{ 
                  marginTop: '1rem', 
                  padding: '1rem', 
                  backgroundColor: '#7f1d1d', 
                  border: '1px solid #991b1b', 
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-line',
                  lineHeight: '1.6'
                }}>
                  <strong>⚠️ Error:</strong><br />
                  {cameraError}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Alerts */}
          <div>
            <div style={{ backgroundColor: '#1e293b', borderRadius: '0.5rem', padding: '1.5rem', border: '1px solid #334155' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Recent Alerts</h2>
              
              {incidents.length === 0 ? (
                <p style={{ color: '#64748b', fontSize: '0.875rem' }}>No alerts yet. System monitoring...</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {incidents.map((incident, index) => (
                    <div 
                      key={index}
                      style={{ 
                        padding: '1rem', 
                        backgroundColor: '#0f172a', 
                        border: '1px solid #334155', 
                        borderRadius: '0.375rem',
                        borderLeft: '3px solid #ef4444'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span style={{ fontWeight: '600', color: '#ef4444' }}>⚠️ {incident.type || 'Alert'}</span>
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          {new Date(incident.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
                        {incident.description || 'Violence detected'}
                      </p>
                      {incident.confidence && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
                          Confidence: {Math.round(incident.confidence * 100)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
