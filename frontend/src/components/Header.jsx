import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Cpu, Activity, PlusCircle, Home, Layers, CheckCircle2, AlertTriangle, ShieldCheck, ChevronDown, FolderGit2 } from 'lucide-react';
import { projectApi } from '../services/api';

export default function Header({ activeProject }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [allProjects, setAllProjects] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    projectApi.getProjects()
      .then(res => {
        if (res.data) setAllProjects(res.data);
      })
      .catch(err => console.error("Error fetching project list in header", err));
  }, [activeProject?.id]);

  const handleNewRequirementClick = (e) => {
    if (e) e.preventDefault();
    setIsDropdownOpen(false);
    const inputEl = document.getElementById('new-requirement-input');
    const container = document.getElementById('new-requirement-console');
    if (inputEl) {
      container?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => inputEl.focus(), 150);
    } else {
      navigate('/?focus=requirement');
    }
  };

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

          {/* Project Switcher Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 text-xs transition"
            >
              <FolderGit2 className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-200 font-semibold max-w-[160px] sm:max-w-[220px] truncate">
                {activeProject?.name || 'Select Project'}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {isDropdownOpen && (
              <div 
                className="absolute left-0 mt-2 w-80 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-2 z-50 overflow-hidden"
                onMouseLeave={() => setIsDropdownOpen(false)}
              >
                <div className="px-3 py-1.5 border-b border-slate-800 flex items-center justify-between text-[10px] font-mono uppercase text-slate-400">
                  <span>Engineered Projects</span>
                  <span>{allProjects.length} total</span>
                </div>

                <div className="max-h-64 overflow-y-auto divide-y divide-slate-800/60">
                  {allProjects.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => {
                        setIsDropdownOpen(false);
                        navigate(`/project/${p.id}`);
                      }}
                      className={`w-full text-left px-3.5 py-2.5 hover:bg-slate-800 transition flex items-center justify-between ${
                        p.id === activeProject?.id ? 'bg-cyan-950/40 text-cyan-300 font-semibold' : 'text-slate-300'
                      }`}
                    >
                      <div className="truncate mr-2">
                        <div className="text-xs truncate">{p.name}</div>
                        <div className="text-[10px] text-slate-400 truncate">{p.raw_requirement}</div>
                      </div>
                      <span className="shrink-0 text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
                        {p.status}
                      </span>
                    </button>
                  ))}
                </div>

                <div className="p-2 border-t border-slate-800 bg-slate-950/60">
                  <button
                    onClick={handleNewRequirementClick}
                    className="flex items-center justify-center space-x-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium py-1.5 rounded-lg hover:bg-cyan-950/40 transition w-full"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Input New Requirement</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {activeProject && (
            <div className="hidden lg:flex items-center pl-2 space-x-2">
              {getStatusBadge(activeProject.status)}
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

          <button
            onClick={handleNewRequirementClick}
            className="bg-cyan-600 hover:bg-cyan-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center space-x-1.5 shadow-md shadow-cyan-600/30"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Requirement</span>
          </button>
        </div>
      </div>
    </header>
  );
}
