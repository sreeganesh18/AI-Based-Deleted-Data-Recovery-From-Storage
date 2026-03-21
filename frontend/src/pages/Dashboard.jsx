import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, HardDrive, FileCheck, Clock, ArrowRight } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <div className="app-container">
      <nav className="top-nav">
        <div className="nav-brand">
          <Activity className="w-8 h-8 text-primary" />
          <span>AI Data Recovery</span>
        </div>
        <div className="flex items-center gap-4" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span className="text-gray-300">Welcome, {user?.name || 'Investigator'}</span>
          <button 
            onClick={handleLogout}
            className="glass-button secondary"
            style={{ padding: '8px 16px', fontSize: '0.875rem' }}
          >
            Logout
          </button>
        </div>
      </nav>

      <main className="mt-8 animate-fade-in" style={{ marginTop: '32px' }}>
        <div className="mb-10 text-center" style={{ marginBottom: '40px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>Recovery Control Center</h1>
          <p className="text-gray-400" style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
            Monitor and manage AI-powered reconstruction operations for your active investigations.
          </p>
        </div>

        <div className="grid-layout mb-12" style={{ marginBottom: '48px' }}>
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <div style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '12px', color: 'var(--primary)' }}>
              <HardDrive className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-400" style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '4px' }}>Total Scans</p>
              <h3 style={{ fontSize: '2rem' }}>14</h3>
            </div>
          </div>
          
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '12px', color: 'var(--success)' }}>
              <FileCheck className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-400" style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '4px' }}>Files Recovered</p>
              <h3 style={{ fontSize: '2rem' }}>2,845</h3>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <div style={{ padding: '12px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '12px', color: 'var(--secondary)' }}>
              <Clock className="w-8 h-8" />
            </div>
            <div>
              <p className="text-gray-400" style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '4px' }}>Recent Activity</p>
              <h3 style={{ fontSize: '1.25rem' }}>Img_04.dd</h3>
              <p className="text-sm text-gray-500" style={{ fontSize: '0.8rem' }}>2 hours ago</p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
          <button 
            className="glass-button"
            style={{ padding: '16px 32px', fontSize: '1.1rem' }}
            onClick={() => navigate('/storage-selection')}
          >
            Start New Recovery <ArrowRight className="w-5 h-5" />
          </button>
          
          <button 
            className="glass-button secondary"
            style={{ padding: '16px 32px', fontSize: '1.1rem' }}
          >
            Investigation History
          </button>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
