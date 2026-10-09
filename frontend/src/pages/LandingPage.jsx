import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Cpu, Rocket, ShieldCheck, Wrench, Users, CheckCircle2, 
  ArrowRight, FileSearch, Terminal, Database, Activity, Sparkles, Layers, Code2, Zap 
} from 'lucide-react';
import Header from '../components/Header';
import QuickRequirementBar from '../components/QuickRequirementBar';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#080B10] text-slate-100 flex flex-col font-sans relative overflow-hidden bg-grid-pattern">
      <Header />

      {/* Background Ambient Glows */}
      <div className="absolute top-20 left-1/4 w-96 h-96 bg-cyan-500/10 blur-[140px] rounded-full pointer-events-none animate-float"></div>
      <div className="absolute top-48 right-1/4 w-96 h-96 bg-indigo-500/10 blur-[150px] rounded-full pointer-events-none"></div>

      {/* Hero Section */}
      <section className="relative pt-16 pb-20 px-6 z-10">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono shadow-lg shadow-cyan-950/30 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" style={{ animationDuration: '6s' }} />
            <span>Autonomous Multi-Agent AI Software Engineering System</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
            Turn Any Requirement Into<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
              A Live Operating Application
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Specify your software requirement in plain English. ForgeSwarm dynamically orchestrates an autonomous engineering team to decompose architecture, generate code, verify concurrency, auto-repair defects, and launch staging.
          </p>

          {/* Direct Requirement Input Console */}
          <div className="pt-4 text-left max-w-4xl mx-auto">
            <QuickRequirementBar />
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/project"
              className="glass-card hover:bg-slate-800/80 text-slate-200 font-semibold px-6 py-3 rounded-xl transition-all flex items-center space-x-2 text-xs shadow-md border border-slate-700/80"
            >
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>ACCESS WORKSPACE DASHBOARD</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Capabilities */}
      <section className="py-16 px-6 max-w-6xl mx-auto space-y-12 z-10 relative">
        <div className="text-center space-y-2">
          <div className="inline-block px-3 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono uppercase text-cyan-400 tracking-wider">
            Architecture & Workflow
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">Full Autonomous Engineering Lifecycle</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            From natural-language requirements to interactive deployments with self-repairing reliability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-cyan-500/40">
            <div className="w-12 h-12 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 shadow-md">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Dynamic Swarm Assembly</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Teams are tailored to the exact problem domain. The system synthesizes contract specifications, security agents, and database engineers on the fly.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-amber-500/40">
            <div className="w-12 h-12 rounded-xl bg-amber-950/80 border border-amber-800/60 flex items-center justify-center text-amber-400 shadow-md">
              <Wrench className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Automated Failure Diagnosis & Repair</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              When concurrency violations or edge-case tests fail, the diagnostic agent isolates the root cause and surgically commits thread-safe repairs.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-emerald-500/40">
            <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 shadow-md">
              <Rocket className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Instant Staging Deployment</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every engineered solution launches into an isolated execution container with live health probes and an embedded interactive browser window.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800/80 py-8 px-6 text-center text-xs text-slate-500 font-mono z-10 bg-slate-950/40 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-slate-300">FORGE<span className="text-cyan-400">SWARM</span></span>
            <span>— Autonomous Engineering Engine</span>
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span>FastAPI Backend</span>
            <span>•</span>
            <span>React Frontend</span>
            <span>•</span>
            <span>Multi-Agent Swarm</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
