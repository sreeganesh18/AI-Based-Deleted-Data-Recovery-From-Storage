import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { HardDrive, Usb, Search, UploadCloud, AlertCircle } from 'lucide-react';
import { recoveryAPI } from '../api';

const StorageSelection = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [deviceType, setDeviceType] = useState('hdd');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleStartScan = async () => {
    if (!selectedFile) {
      setError('Please select a disk image file to scan');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Create a dummy investigation ID for now
      const investigationId = Math.floor(Math.random() * 1000);
      
      const response = await recoveryAPI.uploadImage(
        investigationId, 
        selectedFile,
        (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      );

      // Extract image ID from response and go to Scan Control
      const { image_id } = response.data;
      navigate(`/scan-control/${image_id}`);
      
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to initialize scan setup.');
      setLoading(false);
    }
  };

  const getDeviceIcon = (type) => {
    switch(type) {
      case 'hdd': return <HardDrive className="w-12 h-12" />;
      case 'ssd': return <HardDrive className="w-12 h-12" />; // Lucide doesn't have an SSD specifically, same icon with diff style 
      case 'usb': return <Usb className="w-12 h-12" />;
      default: return <HardDrive className="w-12 h-12" />;
    }
  };

  const devices = [
    { id: 'hdd', name: 'Hard Disk Drive (HDD)', icon: 'hdd' },
    { id: 'ssd', name: 'Solid State Drive (SSD)', icon: 'ssd' },
    { id: 'usb', name: 'USB / Removable', icon: 'usb' },
  ];

  return (
    <div className="app-container">
      <div className="top-nav">
        <h2 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Storage Selection</h2>
        <button className="glass-button secondary" onClick={() => navigate('/dashboard')} style={{ padding: '8px 16px' }}>Back to Dashboard</button>
      </div>

      <main className="animate-fade-in" style={{ maxWidth: '800px', margin: '0 auto', width: '100%', marginTop: '32px' }}>
        
        {error && (
          <div className="glass-panel" style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.3)', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <AlertCircle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        )}

        <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>1. Select Device Type</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '40px' }}>
          {devices.map(dev => (
            <div 
              key={dev.id}
              className="glass-panel"
              style={{ 
                padding: '24px', 
                textAlign: 'center', 
                cursor: 'pointer',
                borderColor: deviceType === dev.id ? 'var(--primary)' : 'var(--border-color)',
                boxShadow: deviceType === dev.id ? '0 0 15px var(--primary-glow)' : 'none',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px'
              }}
              onClick={() => setDeviceType(dev.id)}
            >
              <div style={{ color: deviceType === dev.id ? 'var(--primary)' : 'var(--text-muted)' }}>
                {getDeviceIcon(dev.icon)}
              </div>
              <p style={{ fontWeight: 500 }}>{dev.name}</p>
            </div>
          ))}
        </div>

        <h3 style={{ fontSize: '1.25rem', marginBottom: '16px' }}>2. Upload Target Image</h3>
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', borderStyle: 'dashed', borderWidth: '2px', marginBottom: '32px' }}>
          <UploadCloud className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <h4 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>Select Disk Image</h4>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '0.9rem' }}>Upload .dd, .img, or RAW format evidence files</p>
          
          <input 
            type="file" 
            id="file-upload" 
            style={{ display: 'none' }} 
            onChange={(e) => setSelectedFile(e.target.files[0])}
          />
          <label htmlFor="file-upload" className="glass-button secondary">
            Browse Files
          </label>
          
          {selectedFile && (
            <div style={{ marginTop: '24px', padding: '16px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', display: 'inline-block' }}>
              <p style={{ fontWeight: 600, color: 'var(--primary)' }}>{selectedFile.name}</p>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{(selectedFile.size / (1024 * 1024 * 1024)).toFixed(2)} GB</p>
            </div>
          )}
        </div>

        {uploadProgress > 0 && uploadProgress < 100 && (
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.875rem' }}>
              <span>Uploading Evidence...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div style={{ width: '100%', height: '8px', background: 'var(--bg-card)', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${uploadProgress}%`, height: '100%', background: 'var(--primary)', transition: 'width 0.2s' }}></div>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px' }}>
          <button 
            className="glass-button" 
            style={{ padding: '14px 32px', fontSize: '1.1rem' }}
            onClick={handleStartScan}
            disabled={!selectedFile || loading}
          >
            {loading ? 'Initializing Scan...' : 'Start Scan'} <Search className="w-5 h-5 ml-2" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default StorageSelection;
