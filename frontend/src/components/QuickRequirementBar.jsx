import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Play, PlusCircle, Layers, ChevronDown, ChevronUp, Bot, ShieldCheck } from 'lucide-react';
import { projectApi } from '../services/api';

const QUICK_PRESETS = [
  {
    label: '🏥 Hospital Appointments',
    name: 'Hospital Appointment Management System',
    requirement: 'Build a hospital appointment platform where patients can register, view doctors, check available appointment slots, book appointments, and cancel appointments. A doctor must never have two patients booked for the same time slot.'
  },
  {
    label: '🚗 Car Rental Fleet',
    name: 'Car Rental Fleet Management System',
    requirement: 'Build a car rental fleet management system where customers can reserve cars, view available vehicles, and cancel reservations. A vehicle must never be reserved by two customers for the same dates.'
  },
  {
    label: '📚 Library Book Lending',
    name: 'Library Book Lending System',
    requirement: 'Build a library book lending system where students can register, view available books, borrow books, and return books. A book copy must never be borrowed by two students at the same time.'
  },
  {
    label: '⚡ Flash Sale Inventory',
    name: 'Flash Sale Warehouse Inventory System',
    requirement: 'Build a flash sale warehouse inventory checkout system where shoppers can view limited inventory items, place reserve orders, and cancel orders. An inventory item must never be reserved by more shoppers than available stock at the same timestamp.'
  },
  {
    label: '🎓 Course Enrollment',
    name: 'University Course Enrollment System',
    requirement: 'Build a course registration portal where students can browse courses, check instructor schedules, enroll in classes, and drop classes. A course section must never exceed its maximum student capacity under concurrent enrollments.'
  },
  {
    label: '🏨 Hotel Room Booking',
    name: 'Boutique Hotel Room Reservation Platform',
    requirement: 'Build a hotel reservation platform where guests can view room types, check room availability by dates, book rooms, and cancel reservations. A hotel room must never be double-booked for overlapping date intervals.'
  }
];

export default function QuickRequirementBar({ onProjectCreated }) {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(true);
  const [name, setName] = useState('');
  const [requirement, setRequirement] = useState('');
  const [llmProvider, setLlmProvider] = useState('mock');
  const [isSubmitting, setIsSubmitting] = useState(false);

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
    <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-[#0c1424] border border-cyan-500/30 rounded-2xl shadow-xl shadow-cyan-950/20 overflow-hidden">
      {/* Header bar / toggle */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="px-5 py-3.5 bg-slate-950/60 border-b border-slate-800/80 flex items-center justify-between cursor-pointer hover:bg-slate-950/80 transition"
      >
        <div className="flex items-center space-x-3">
          <div className="w-7 h-7 rounded-lg bg-cyan-600/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-white tracking-wide uppercase font-mono">
                Input New Software Requirement
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
                Universal Dynamic Swarm
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Enter any custom requirement below — ForgeSwarm will dynamically decompose, build, test, and self-repair it.
            </p>
          </div>
        </div>

        <button 
          type="button"
          className="text-slate-400 hover:text-slate-200 transition p-1"
        >
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expandable Form Body */}
      {isExpanded && (
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Quick Presets */}
          <div>
            <span className="text-[11px] font-mono uppercase text-slate-400 block mb-1.5">
              Quick Presets (or type your own custom requirement below):
            </span>
            <div className="flex flex-wrap gap-2">
              {QUICK_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleApplyPreset(p)}
                  className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-cyan-950/60 hover:text-cyan-300 hover:border-cyan-700/60 text-slate-300 border border-slate-700/80 transition font-medium text-left"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Requirement Text Area */}
          <div>
            <label className="block text-xs font-semibold text-slate-200 mb-1">
              Natural-Language Software Requirement:
            </label>
            <textarea
              rows={3}
              value={requirement}
              onChange={(e) => setRequirement(e.target.value)}
              placeholder="e.g. Build an equipment reservation system where engineers can reserve testing labs, view available time slots, and cancel reservations. A lab must never be reserved by two teams for the same slot."
              className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition leading-relaxed font-sans"
              required
            />
          </div>

          {/* Project Name and Options Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                Project Name (optional, auto-generated if empty):
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Enterprise Lab Reservation Platform"
                className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                AI Engine:
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                <option value="mock">Autonomous Agent Engine (Mock Mode)</option>
                <option value="gemini">Google Gemini 1.5 Pro</option>
                <option value="openai">OpenAI GPT-4o</option>
              </select>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
            <div className="flex items-center space-x-2 text-[11px] text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Full lifecycle: Architecture → Concurrency Probe → TOCTOU Diagnosis → Repair → Staging</span>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !requirement.trim()}
              className="bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition shadow-lg shadow-cyan-600/30 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Assembling Swarm & Starting...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Launch Autonomous Swarm</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
