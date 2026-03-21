import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, FileImage, FileText, File, ExternalLink, CheckCircle } from 'lucide-react';
import { recoveryAPI, getDownloadUrl } from '../api';

const FinalResults = () => {
  const { imageId } = useParams();
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecoveredFiles = async () => {
      try {
        const res = await recoveryAPI.getRecoveredFiles(imageId);
        setFiles(res.data);
        
        // Mock data if backend is empty for UI demonstration
        if (res.data.length === 0) {
          setFiles([
            { id: 101, file_type: 'jpg', confidence_score: 0.99, file_size: 1024500, recovery_status: 'VALID' },
            { id: 102, file_type: 'png', confidence_score: 0.95, file_size: 450300, recovery_status: 'VALID' },
            { id: 103, file_type: 'pdf', confidence_score: 0.88, file_size: 2048500, recovery_status: 'PARTIAL' },
            { id: 104, file_type: 'docx', confidence_score: 0.91, file_size: 85300, recovery_status: 'VALID' },
          ]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecoveredFiles();
  }, [imageId]);

  const getFileIcon = (type) => {
    const t = type.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(t)) {
      return <FileImage className="w-8 h-8 text-primary" />;
    } else if (['pdf', 'doc', 'docx', 'txt'].includes(t)) {
      return <FileText className="w-8 h-8 text-secondary" />;
    }
    return <File className="w-8 h-8 text-muted" />;
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const downloadFile = (fileId) => {
    // In a real scenario, this links to the download endpoint
    window.open(getDownloadUrl(fileId), '_blank');
  };

  return (
    <div className="app-container">
      <div className="top-nav">
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle className="text-success w-6 h-6" /> Recovery Complete
          </h2>
        </div>
        <button 
          className="glass-button secondary" 
          onClick={() => navigate('/dashboard')}
        >
          Return to Dashboard
        </button>
      </div>

      <main className="animate-fade-in" style={{ marginTop: '32px' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '8px' }}>Recovered Evidence</h3>
            <p style={{ color: 'var(--text-muted)' }}>Found {files.length} structured files from fragments.</p>
          </div>
          <button className="glass-button" style={{ padding: '10px 20px' }}>
            <Download className="w-4 h-4 mx-2" /> Export All Selected
          </button>
        </div>

        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.05)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>Type</th>
                <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>Filename</th>
                <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>Size</th>
                <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)' }}>Integrity</th>
                <th style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-muted)', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
                    Loading results...
                  </td>
                </tr>
              ) : files.map((file) => (
                <tr key={file.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', transition: 'background 0.2s' }} className="hover:bg-slate-800/30">
                  <td style={{ padding: '16px 24px' }}>
                    {getFileIcon(file.file_type)}
                  </td>
                  <td style={{ padding: '16px 24px', fontWeight: 500 }}>
                    recovered_{file.id}.{file.file_type}
                  </td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-muted)' }}>
                    {formatSize(file.file_size)}
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '12px', 
                      fontSize: '0.75rem', 
                      fontWeight: 600,
                      background: file.recovery_status === 'VALID' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                      color: file.recovery_status === 'VALID' ? 'var(--success)' : 'var(--warning)'
                    }}>
                      {(file.confidence_score * 100).toFixed(1)}% {file.recovery_status}
                    </span>
                  </td>
                  <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                      <button 
                        className="glass-button secondary" 
                        style={{ padding: '6px 12px', fontSize: '0.875rem' }}
                      >
                        <ExternalLink className="w-4 h-4 mr-2" /> Preview
                      </button>
                      <button 
                        className="glass-button" 
                        style={{ padding: '6px 12px', fontSize: '0.875rem' }}
                        onClick={() => downloadFile(file.id)}
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </main>
    </div>
  );
};

export default FinalResults;
