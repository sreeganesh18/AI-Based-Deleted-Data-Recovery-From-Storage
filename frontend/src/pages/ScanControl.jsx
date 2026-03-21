import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, Square, Settings, Database, Server, BarChart2 } from 'lucide-react';
import { recoveryAPI } from '../api';

const ScanControl = () => {
  const { imageId } = useParams();
  const navigate = useNavigate();
  
  const [scanStatus, setScanStatus] = useState('idle'); // idle, processing, completed, error
  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [stats, setStats] = useState({
    sectorsScanned: 0,
    fragmentsFound: 0,
    estimatedTime: '--:--'
  });

  const triggerScan = async () => {
    try {
      setScanStatus('starting');
      const response = await recoveryAPI.startRecovery(imageId);
      setTaskId(response.data.task_id);
      setScanStatus('processing');
    } catch (err) {
      console.error(err);
      setScanStatus('error');
    }
  };

  useEffect(() => {
    let pollInterval;
    
    if (taskId && scanStatus === 'processing') {
      pollInterval = setInterval(async () => {
        try {
          const res = await recoveryAPI.getTaskStatus(taskId);
          const status = res.data.status;
          
          if (status === 'SUCCESS') {
            setScanStatus('completed');
            setProgress(100);
            clearInterval(pollInterval);
          } else if (status === 'FAILURE') {
            setScanStatus('error');
            clearInterval(pollInterval);
          } else {
            // Simulate progression visually 
            setProgress(prev => Math.min(prev + (Math.random() * 5), 95));
            setStats(prev => ({
              sectorsScanned: prev.sectorsScanned + Math.floor(Math.random() * 10000),
              fragmentsFound: prev.fragmentsFound + Math.floor(Math.random() * 50),
              estimatedTime: '00:04:23'
            }));
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 3000);
    }

    return () => clearInterval(pollInterval);
  }, [taskId, scanStatus]);

  return (
    <div className="app-container">
      <div className="top-nav">
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Recovery Control Panel</h2>
        {scanStatus === 'completed' && (
          <button 
            className="glass-button" 
            onClick={() => navigate(`/fragment-visualization/${imageId}`)}
          >
            Review Fragments
          </button>
        )}
      </div>

      <main className="animate-fade-in" style={{ marginTop: '32px' }}>
        
        <div className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '4px' }}>Sector-Level Scan Progress</h3>
              <p style={{ color: 'var(--text-muted)' }}>Image ID: {imageId}</p>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                className="glass-button" 
                onClick={triggerScan}
                disabled={scanStatus !== 'idle'}
                style={{ padding: '10px 20px', background: scanStatus === 'processing' ? 'var(--primary-hover)' : 'var(--success)' }}
              >
                <Play className="w-4 h-4 mr-2" /> {scanStatus === 'processing' ? 'Running' : 'Start Scan'}
              </button>
              <button 
                className="glass-button secondary" 
                style={{ padding: '10px 20px', color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                disabled={scanStatus !== 'processing'}
              >
                <Square className="w-4 h-4 mr-2" /> Stop
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '1rem', fontWeight: 500 }}>
              <span style={{ color: scanStatus === 'completed' ? 'var(--success)' : 'var(--text-main)' }}>
                {scanStatus === 'idle' ? 'Ready' : scanStatus === 'processing' ? 'Analyzing Sectors...' : scanStatus === 'completed' ? 'Analysis Complete' : 'Error Occurred'}
              </span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div style={{ width: '100%', height: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px', overflow: 'hidden', boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.2)' }}>
              <div 
                className={scanStatus === 'processing' ? 'animate-pulse' : ''}
                style={{ 
                  width: `${progress}%`, 
                  height: '100%', 
                  background: scanStatus === 'completed' ? 'var(--success)' : scanStatus === 'error' ? 'var(--danger)' : 'linear-gradient(90deg, var(--primary), var(--secondary))',
                  transition: 'width 0.5s ease-out',
                  boxShadow: '0 0 10px rgba(59, 130, 246, 0.5)'
                }}
              />
            </div>
          </div>
        </div>

        <div className="grid-layout">
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '50%', color: 'var(--primary)' }}>
              <Database className="w-8 h-8" />
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '4px' }}>Sectors Scanned</p>
              <h3 style={{ fontSize: '1.75rem', fontFamily: 'monospace' }}>{stats.sectorsScanned.toLocaleString()}</h3>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '50%', color: 'var(--secondary)' }}>
              <BarChart2 className="w-8 h-8" />
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '4px' }}>Fragments Found</p>
              <h3 style={{ fontSize: '1.75rem', fontFamily: 'monospace' }}>{stats.fragmentsFound.toLocaleString()}</h3>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '50%', color: 'var(--warning)' }}>
              <Server className="w-8 h-8" />
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '4px' }}>Estimated Time</p>
              <h3 style={{ fontSize: '1.75rem', fontFamily: 'monospace' }}>{scanStatus === 'processing' ? stats.estimatedTime : '--:--'}</h3>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
};

export default ScanControl;
