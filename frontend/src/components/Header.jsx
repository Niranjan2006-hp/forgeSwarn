import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Cpu, Activity, PlusCircle, Home, Layers, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Header({ activeProject }) {
  const location = useLocation();

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>DEPLOYED</span>
          </span>
        );
      case 'FAILURE_DETECTED':
      case 'DIAGNOSING':
      case 'REPAIRING':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950 text-amber-400 border border-amber-800 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>SELF-REPAIRING</span>
          </span>
        );
      case 'TESTING':
      case 'REGRESSION_TESTING':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-950 text-blue-400 border border-blue-800">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping"></span>
            <span>TESTING</span>
          </span>
        );
      case 'DEPLOYING':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-950 text-indigo-400 border border-indigo-800">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
            <span>DEPLOYING</span>
          </span>
        );
      case 'ANALYZING':
      case 'ARCHITECTING':
      case 'DEVELOPING':
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-950 text-cyan-400 border border-cyan-800">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>SWARM ACTIVE</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span>
            <span>{status || 'IDLE'}</span>
          </span>
        );
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-[#080B10]/90 backdrop-blur-md border-b border-slate-800 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-4">
          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-wider text-white">FORGE<span className="text-cyan-400">SWARM</span></span>
                <span className="text-[10px] px-1.5 py-0.5 rounded font-mono uppercase bg-cyan-950 text-cyan-400 border border-cyan-800">v1.0</span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Autonomous AI Engineering Team</p>
            </div>
          </Link>

          {activeProject && (
            <div className="hidden lg:flex items-center pl-4 border-l border-slate-800 space-x-3">
              <span className="text-xs text-slate-400">Project:</span>
              <span className="text-xs font-semibold text-slate-200">{activeProject.name}</span>
              {getStatusBadge(activeProject.status)}
              {activeProject.is_demo_mode && (
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-amber-300 border border-amber-900/50">
                  DEMO MODE
                </span>
              )}
            </div>
          )}
        </div>

        {/* Navigation & Actions */}
        <div className="flex items-center space-x-3">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center space-x-1.5 ${
              location.pathname === '/' ? 'text-cyan-400 bg-cyan-950/40 border border-cyan-800/60' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Home className="w-3.5 h-3.5" />
            <span>Overview</span>
          </Link>

          <Link
            to="/new"
            className="bg-cyan-600 hover:bg-cyan-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center space-x-1.5 shadow-md shadow-cyan-600/30"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Requirement</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
