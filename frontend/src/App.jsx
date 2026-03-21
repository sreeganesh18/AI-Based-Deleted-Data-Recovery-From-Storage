import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import StorageSelection from './pages/StorageSelection';
import ScanControl from './pages/ScanControl';
import FragmentVisualization from './pages/FragmentVisualization';
import Reconstruction from './pages/Reconstruction';
import FinalResults from './pages/FinalResults';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/storage-selection" element={
          <ProtectedRoute>
            <StorageSelection />
          </ProtectedRoute>
        } />
        
        <Route path="/scan-control/:imageId" element={
          <ProtectedRoute>
            <ScanControl />
          </ProtectedRoute>
        } />
        
        <Route path="/fragment-visualization/:imageId" element={
          <ProtectedRoute>
            <FragmentVisualization />
          </ProtectedRoute>
        } />
        
        <Route path="/reconstruction/:imageId" element={
          <ProtectedRoute>
            <Reconstruction />
          </ProtectedRoute>
        } />
        
        <Route path="/final-results/:imageId" element={
          <ProtectedRoute>
            <FinalResults />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
