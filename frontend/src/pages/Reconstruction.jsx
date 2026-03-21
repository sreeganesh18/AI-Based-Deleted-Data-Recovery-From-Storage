import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layers, CheckCircle, Loader2 } from 'lucide-react';

const Reconstruction = () => {
  const { imageId } = useParams();
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('Initializing graph...');
  const [logs, setLogs] = useState(['Starting block clustering...']);

  useEffect(() => {
    // Simulate the reconstruction process
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        
        const newProgress = Math.min(prev + 2.5, 100);
        
        // Update simulation logs
        if (newProgress === 20) {
          setCurrentFile('Building fragment adjacency matrix...');
          setLogs(l => [...l, 'Mapped 8 clusters based on sequence analysis.']);
        } else if (newProgress === 40) {
          setCurrentFile('Reconstructing File_001.jpg...');
          setLogs(l => [...l, 'Reconstructing JPEG streams (8/12 verified).']);
        } else if (newProgress === 65) {
          setCurrentFile('Reconstructing Document_002.pdf...');
          setLogs(l => [...l, 'Reconstructing Document streams (5/5 verified).']);
        } else if (newProgress === 90) {
          setCurrentFile('Finalizing verification hashes...');
          setLogs(l => [...l, 'Calculating SHA-256 for recovered instances.']);
        } else if (newProgress >= 100) {
          setCurrentFile('Reconstruction Complete');
          setLogs(l => [...l, 'Pipeline finished successfully.']);
        }
        
        return newProgress;
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <div className="top-nav">
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>File Reconstruction Engine</h2>
          <p style={{ color: 'var(--text-muted)' }}>Image ID: {imageId}</p>
        </div>
        {progress === 100 && (
          <button 
            className="glass-button" 
            style={{ padding: '10px 24px', background: 'var(--success)' }}
            onClick={() => navigate(`/final-results/${imageId}`)}
          >
            View Recovered Files
          </button>
        )}
      </div>

      <main className="animate-fade-in" style={{ marginTop: '32px', maxWidth: '800px', margin: '40px auto 0 auto' }}>
        
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
          
          <div style={{ position: 'relative', width: '200px', height: '200px', margin: '0 auto 32px auto' }}>
            <svg viewBox="0 0 100 100" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
              <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
              <circle 
                cx="50" cy="50" r="45" 
                fill="none" 
                stroke="var(--primary)" 
                strokeWidth="8" 
                strokeDasharray="283" 
                strokeDashoffset={283 - (283 * progress) / 100} 
                style={{ transition: 'stroke-dashoffset 0.5s ease-in-out' }}
                strokeLinecap="round"
              />
            </svg>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '2.5rem', fontWeight: 700 }}>{Math.round(progress)}%</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '16px', color: progress === 100 ? 'var(--success)' : 'var(--text-main)' }}>
            {progress === 100 ? <CheckCircle className="w-6 h-6" /> : <Loader2 className="w-6 h-6 animate-spin" />}
            <h3 style={{ fontSize: '1.5rem' }}>{currentFile}</h3>
          </div>
          
        </div>

        <div className="glass-panel" style={{ padding: '24px', marginTop: '32px' }}>
          <h4 style={{ fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers className="w-5 h-5 text-secondary" /> Processing Logs
          </h4>
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.8)', 
            padding: '16px', 
            borderRadius: '8px',
            minHeight: '200px',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            color: 'var(--text-muted)'
          }}>
            {logs.map((log, i) => (
              <div key={i} style={{ marginBottom: '8px' }}>
                <span style={{ color: 'var(--primary)' }}>[{new Date().toLocaleTimeString()}]</span> {log}
              </div>
            ))}
          </div>
        </div>

      </main>
    </div>
  );
};

export default Reconstruction;
