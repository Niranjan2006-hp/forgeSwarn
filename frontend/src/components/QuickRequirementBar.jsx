import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Play, PlusCircle, Layers, ChevronDown, ChevronUp, Bot, ShieldCheck } from 'lucide-react';
import { projectApi } from '../services/api';

const QUICK_PRESETS = [
  {
    label: '🧮 Interactive Calculator App',
    name: 'Scientific & Expression Calculator Application',
    requirement: 'Build a full-featured calculator web application with arithmetic operations (+, -, *, /), parentheses evaluation, percentage calculation, keyboard support, dark mode UI, and an interactive calculation audit history log.'
  },
  {
    label: '🏥 Hospital Appointments',
    name: 'Hospital Appointment Management System',
    requirement: 'Build a hospital appointment platform where patients can register, view doctors, check available appointment slots, book appointments, and cancel appointments. A doctor must never have two patients booked for the same time slot.'
  },
  {
    label: '⚡ Flash Sale Inventory',
    name: 'Flash Sale Warehouse Inventory System',
    requirement: 'Build a flash sale warehouse inventory checkout system where shoppers can view limited inventory items, place reserve orders, and cancel orders. An inventory item must never be reserved by more shoppers than available stock.'
  },
  {
    label: '📋 Kanban Task Board',
    name: 'Interactive Kanban Project Workspace',
    requirement: 'Build an agile Kanban project management board where teams can create tasks, assign priority levels, drag tasks across columns (To Do, In Progress, Done), filter by tag, and track milestone progress.'
  },
  {
    label: '🔗 Shortlink URL Redirection',
    name: 'URL Shortener & Click Analytics Platform',
    requirement: 'Build a URL shortener service where users can input long URLs to generate unique short slug aliases, redirect visitors, track total click counts, and inspect timestamped visitor analytics.'
  },
  {
    label: '🚗 Car Rental Fleet',
    name: 'Car Rental Fleet Management System',
    requirement: 'Build a car rental fleet management system where customers can reserve cars, view available vehicles, and cancel reservations. A vehicle must never be reserved by two customers for the same dates.'
  }
];

export default function QuickRequirementBar({ onProjectCreated }) {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(true);
  const [name, setName] = useState('');
  const [requirement, setRequirement] = useState('');
  const [llmProvider, setLlmProvider] = useState('mock');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (window.location.search.includes('focus=requirement') || window.location.hash.includes('requirement')) {
      setIsExpanded(true);
      setTimeout(() => {
        const el = document.getElementById('new-requirement-input');
        const container = document.getElementById('new-requirement-console');
        if (el) {
          container?.scrollIntoView({ behavior: 'smooth', block: 'center' });
          el.focus();
        }
      }, 150);
    }
  }, []);

  const handleApplyPreset = (preset) => {
    setName(preset.name);
    setRequirement(preset.requirement);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!requirement.trim()) return;

    setIsSubmitting(true);
    try {
      const derivedName = name.trim() || requirement.slice(0, 35) + '...';
      const res = await projectApi.createProject({
        name: derivedName,
        requirement: requirement.trim(),
        application_type: 'Web Application',
        tech_preference: 'FastAPI + React + SQLAlchemy',
        deployment_target: 'Docker / Local Sandbox',
        autonomy_level: 'HIGH',
        is_demo_mode: true,
        llm_provider: llmProvider
      });

      const newProjectId = res.data.id;
      // Start pipeline immediately
      await projectApi.startProject(newProjectId);

      if (onProjectCreated) {
        onProjectCreated(newProjectId);
      } else {
        navigate(`/project/${newProjectId}`);
      }
    } catch (err) {
      console.error('Error submitting requirement:', err);
      alert('Failed to launch swarm. Please check backend connection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div id="new-requirement-console" className="glass-panel border border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-950/20 overflow-hidden transition-all duration-300">
      {/* Header bar / toggle */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-5 py-4 bg-slate-950/70 border-b border-slate-800/80 flex items-center justify-between cursor-pointer hover:bg-slate-900/60 transition group"
      >
        <div className="flex items-center space-x-3.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white shadow-md shadow-cyan-600/30 group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs sm:text-sm font-bold text-white tracking-wide uppercase font-mono">
                Launch New Autonomous Project
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-cyan-950/80 text-cyan-400 border border-cyan-800">
                Any Requirement
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Enter any software specification below — ForgeSwarm will build, test, and host it.
            </p>
          </div>
        </div>

        <button 
          type="button"
          className="text-slate-400 group-hover:text-cyan-400 transition p-1.5 rounded-lg bg-slate-900/60 border border-slate-800"
        >
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expandable Form Body */}
      {isExpanded && (
        <form onSubmit={handleSubmit} className="p-5 sm:p-6 space-y-4 bg-slate-950/40">
          {/* Quick Presets */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono uppercase text-slate-400 tracking-wider">
                Popular Presets (or type your own below):
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {QUICK_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleApplyPreset(p)}
                  className="text-xs px-3 py-1.5 rounded-xl bg-slate-900/80 hover:bg-cyan-950/80 hover:text-cyan-300 hover:border-cyan-500/50 text-slate-300 border border-slate-800 transition-all font-medium text-left shadow-sm hover:scale-[1.02]"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Requirement Text Area */}
          <div>
            <label className="block text-xs font-semibold text-slate-200 mb-1.5 flex items-center justify-between">
              <span>Software Requirement & Functionality:</span>
              <span className="text-[10px] font-mono text-cyan-400">Natural-Language Grounding</span>
            </label>
            <textarea
              id="new-requirement-input"
              rows={3}
              value={requirement}
              onChange={(e) => setRequirement(e.target.value)}
              placeholder="e.g. Build an operating scientific calculator with arithmetic buttons, parentheses, dark mode UI, and a computation history log."
              className="w-full bg-slate-900/90 border border-slate-700/80 focus:border-cyan-500 rounded-xl px-4 py-3 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all leading-relaxed font-sans shadow-inner"
              required
            />
          </div>

          {/* Project Name and Options Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                Project Name (optional):
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Calculator Application"
                className="w-full bg-slate-900/90 border border-slate-700/80 focus:border-cyan-500 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 transition-all"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                Swarm Engine:
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="mock">Autonomous Agent Engine (Instant)</option>
                <option value="gemini">Google Gemini 1.5 Pro</option>
                <option value="openai">OpenAI GPT-4o</option>
              </select>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
            <div className="flex items-center space-x-2 text-[11px] text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Full lifecycle: Architecture → Concurrency Invariant → Auto-Repair → Live Sandbox</span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !requirement.trim()}
              className="w-full sm:w-auto bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs px-6 py-3 rounded-xl transition-all shadow-lg shadow-cyan-600/30 hover:shadow-cyan-500/50 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Assembling Swarm & Starting...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Launch Swarm Pipeline</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
