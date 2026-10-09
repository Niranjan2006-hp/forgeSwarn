import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, Sparkles, Rocket, ArrowRight, ShieldCheck, Layers, Bot } from 'lucide-react';
import Header from '../components/Header';
import { projectApi } from '../services/api';

const PRESET_REQUIREMENTS = [
  {
    title: 'Interactive Calculator Application',
    domain: 'Productivity',
    name: 'Scientific & Expression Calculator Application',
    requirement: 'Build a full-featured calculator web application with arithmetic operations (+, -, *, /), parentheses evaluation, percentage calculation, keyboard support, dark mode UI, and an interactive calculation audit history log.'
  },
  {
    title: 'Hospital Appointment Management System',
    domain: 'Healthcare',
    name: 'Hospital Appointment Management System',
    requirement: 'Build a hospital appointment platform where patients can register, view doctors, check available appointment slots, book appointments, and cancel appointments. A doctor must never have two patients booked for the same time slot.'
  },
  {
    title: 'Real-Time Inventory & Flash Sale System',
    domain: 'E-Commerce',
    name: 'Warehouse Flash Sale & Inventory System',
    requirement: 'Build an inventory order management system where customers can view products, check real-time stock levels, place orders, and cancel orders. An item with zero stock must never be oversold under concurrent checkout requests.'
  }
];

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [requirement, setRequirement] = useState('');
  const [appType, setAppType] = useState('Web Application');
  const [techPref, setTechPref] = useState('FastAPI + React + SQLAlchemy');
  const [deployTarget, setDeployTarget] = useState('Docker / Local Sandbox');
  const [autonomy, setAutonomy] = useState('HIGH');
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [llmProvider, setLlmProvider] = useState('mock');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!requirement.trim()) return;

    setIsSubmitting(true);
    try {
      const res = await projectApi.createProject({
        name,
        requirement,
        application_type: appType,
        tech_preference: techPref,
        deployment_target: deployTarget,
        autonomy_level: autonomy,
        is_demo_mode: isDemoMode,
        llm_provider: llmProvider
      });

      const newProjectId = res.data.id;
      // Start pipeline immediately
      await projectApi.startProject(newProjectId);
      navigate(`/project/${newProjectId}`);
    } catch (err) {
      console.error('Failed to create project', err);
      alert('Error launching project. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadPreset = (preset) => {
    setName(preset.name);
    setRequirement(preset.requirement);
  };

  return (
    <div className="min-h-screen bg-[#080B10] text-slate-100 flex flex-col font-sans">
      <Header />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-8 space-y-8">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span className="text-xs font-mono uppercase text-cyan-400 font-bold tracking-wider">
              Autonomous Swarm Dispatch
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white mt-1 tracking-tight">
            Launch New Engineering Project
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            Don't give AI a coding task. Give it a product requirement. ForgeSwarm will analyze, form the specialized team, architect, develop, test concurrency invariants, diagnose failures, self-repair, and deploy.
          </p>
        </div>

        {/* Preset Selector */}
        <div>
          <span className="text-xs font-mono uppercase text-slate-400 block mb-2">
            Quick-Select Requirement Preset:
          </span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PRESET_REQUIREMENTS.map((p, i) => (
              <button
                key={i}
                type="button"
                onClick={() => loadPreset(p)}
                className={`p-3 rounded-xl border text-left transition text-xs flex flex-col justify-between ${
                  name === p.name
                    ? 'bg-cyan-950/70 border-cyan-500 text-white shadow-md shadow-cyan-900/30'
                    : 'bg-slate-900/70 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div>
                  <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold block mb-1">
                    {p.domain}
                  </span>
                  <span className="font-semibold text-white block">{p.title}</span>
                </div>
                <span className="text-[10px] text-slate-500 mt-2">Click to load</span>
              </button>
            ))}
          </div>
        </div>

        {/* Project Form */}
        <form onSubmit={handleSubmit} className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
          <div>
            <label className="block text-xs font-mono uppercase text-slate-300 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. University Course Registration System"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 transition font-medium"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-slate-300 mb-2">
              Natural-Language Software Requirement & Business Rules
            </label>
            <textarea
              rows={4}
              value={requirement}
              onChange={(e) => setRequirement(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-4 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 transition leading-relaxed"
              placeholder="e.g. Build an application where..."
              required
            />
          </div>

          {/* Architecture & Deployment Selectors */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1.5">Application Type</label>
              <select
                value={appType}
                onChange={(e) => setAppType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200"
              >
                <option>Web Application</option>
                <option>REST API Microservice</option>
                <option>Full-Stack Portal</option>
              </select>
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1.5">Technology Preference</label>
              <select
                value={techPref}
                onChange={(e) => setTechPref(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200"
              >
                <option>FastAPI + React + SQLAlchemy</option>
                <option>Auto Select by Chief Architect</option>
              </select>
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1.5">Deployment Target</label>
              <select
                value={deployTarget}
                onChange={(e) => setDeployTarget(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200"
              >
                <option>Docker / Local Sandbox</option>
                <option>Isolated Subprocess Staging</option>
              </select>
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1.5">Autonomy & Risk Level</label>
              <select
                value={autonomy}
                onChange={(e) => setAutonomy(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200"
              >
                <option value="HIGH">HIGH (Fully Autonomous Self-Repair)</option>
                <option value="MEDIUM">MEDIUM (Gate on Database Schema Changes)</option>
                <option value="LOW">LOW (Approval at Every Step)</option>
              </select>
            </div>
          </div>

          {/* Mode Switch */}
          <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bot className="w-5 h-5 text-cyan-400" />
              <div>
                <span className="text-xs font-semibold text-white block">Deterministic Demo Mode</span>
                <span className="text-[11px] text-slate-400">
                  Enables 100% reliable hackathon presentation with injected double-booking failure and autonomous self-repair.
                </span>
              </div>
            </div>

            <input
              type="checkbox"
              checked={isDemoMode}
              onChange={(e) => setIsDemoMode(e.target.checked)}
              className="w-4 h-4 text-cyan-600 rounded bg-slate-800 border-slate-700"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold py-3.5 px-6 rounded-xl transition shadow-xl shadow-cyan-600/20 flex items-center justify-center space-x-2 text-sm"
          >
            {isSubmitting ? (
              <span>Assembling Swarm...</span>
            ) : (
              <>
                <span>START ENGINEERING</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
