import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import CreateProjectPage from './pages/CreateProjectPage';
import ProjectDashboard from './pages/ProjectDashboard';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/new" element={<CreateProjectPage />} />
        <Route path="/project/:projectId" element={<ProjectDashboard />} />
        <Route path="/project" element={<ProjectDashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
