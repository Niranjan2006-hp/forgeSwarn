import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Cpu, Rocket, ShieldCheck, Wrench, Users, CheckCircle2, 
  ArrowRight, FileSearch, Terminal, Database, Activity, Sparkles, Layers 
} from 'lucide-react';
import Header from '../components/Header';
import QuickRequirementBar from '../components/QuickRequirementBar';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#080B10] text-slate-100 flex flex-col font-sans">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 px-6 border-b border-slate-800">
        <div className="max-w-5xl mx-auto text-center space-y-6 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-800/80 text-cyan-400 text-xs font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Multi-Agent AI Software Engineering Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Don't give AI a coding task.<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
              Give it a product requirement.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
            ForgeSwarm is not a chatbot or prompt-to-file generator. It is an autonomous software engineering organization that analyzes requirements, forms specialized agent teams, writes architecture, detects failures under concurrency, diagnoses root causes, self-repairs, and verifies deployment.
          </p>

          {/* Direct Requirement Input Column */}
          <div className="pt-2 text-left max-w-4xl mx-auto">
            <QuickRequirementBar />
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              to="/project"
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-bold px-6 py-3 rounded-xl transition flex items-center space-x-2 text-sm shadow-md"
            >
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>VIEW CURRENT ACTIVE SWARM</span>
            </Link>
          </div>
        </div>

        {/* Decorative Grid Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none"></div>
      </section>

      {/* The Innovation Loop Section */}
      <section className="py-16 px-6 max-w-6xl mx-auto space-y-12">
        <div className="text-center space-y-2">
          <span className="text-xs font-mono uppercase text-cyan-400 tracking-wider">The Innovation</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">Closed-Loop Autonomous Engineering</h2>
          <p className="text-xs text-slate-400 max-w-2xl mx-auto">
            Traditional AI code generators abandon you the moment syntax errors or concurrency race conditions arise. ForgeSwarm owns the entire engineering lifecycle.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
              <Users className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Dynamic Team Formation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Teams are never fixed. The system determines what specialized capabilities are needed from the requirement (e.g. HIPAA Compliance and ACID Database Agents for Healthcare) and dynamically forms the swarm.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400">
              <Wrench className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Failure Diagnosis & Self-Repair</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              When tests fail (such as double-booking concurrency defects), the Debugger Agent synthesizes the root cause (TOCTOU) and the Repair Agent applies surgical atomic database constraints with zero regressions.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400">
              <Rocket className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Verified Staging Deployment</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              The generated application doesn't sit in markdown blocks. It compiles inside an isolated sandbox, undergoes automated health probe checks (/health), smoke testing, and provides an immediate interactive URL.
            </p>
          </div>
        </div>
      </section>

      {/* Primary Hackathon Demo Preview */}
      <section className="bg-slate-900/50 border-y border-slate-800 py-16 px-6">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-4 max-w-xl">
            <span className="text-xs font-mono uppercase px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              Main Demo Application
            </span>
            <h2 className="text-2xl font-bold text-white">Hospital Appointment Management System</h2>
            <p className="text-xs text-slate-300 leading-relaxed font-mono bg-slate-950 p-4 rounded-lg border border-slate-800">
              "Build a hospital appointment platform where patients can register, view doctors, check available appointment slots, book appointments, and cancel appointments. A doctor must never have two patients booked for the same time slot."
            </p>
            <div className="flex items-center space-x-3 text-xs text-slate-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Full Concurrency Invariant Verified (BR-001)</span>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 p-6 rounded-2xl shadow-2xl max-w-md w-full space-y-4">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-400">Swarm Verification</span>
              <span className="text-emerald-400 font-bold">100% PASS</span>
            </div>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-400">Requirement Traceability</span>
                <span className="text-slate-200">6 / 6 Implemented</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-400">Pytest Suite</span>
                <span className="text-slate-200">17 / 17 Passed</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-900">
                <span className="text-slate-400">Autonomous Bug Fix</span>
                <span className="text-purple-400">TOCTOU Race Repaired</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Staging Sandbox</span>
                <span className="text-cyan-400">Online (:8005)</span>
              </div>
            </div>

            <Link
              to="/project/latest"
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2.5 rounded-lg text-xs transition flex items-center justify-center space-x-2"
            >
              <span>Explore Project Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800 py-6 px-6 text-center text-xs text-slate-500 font-mono">
        ForgeSwarm — Autonomous AI Engineering Team Platform
      </footer>
    </div>
  );
}
