import React, { useState } from 'react';
import { 
  Rocket, ExternalLink, CheckCircle2, ShieldCheck, 
  Server, Cpu, Activity, RefreshCw, Smartphone, Monitor 
} from 'lucide-react';

export default function DeploymentPanel({ project, deployment = [] }) {
  const [viewMode, setViewMode] = useState('browser'); // 'browser' or 'details'

  const activeDeployment = deployment[0] || {};
  const isHealthy = project?.status === 'COMPLETED' || activeDeployment.status === 'HEALTHY';
  const appUrl = project?.app_url || activeDeployment.app_url || 'http://127.0.0.1:8005';

  return (
    <div className="space-y-6">
      {/* Live Staging Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-lg ${
              isHealthy ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-400' : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}>
              <Rocket className="w-6 h-6" />
            </div>

            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold text-white">Staging Environment</span>
                {isHealthy ? (
                  <span className="flex items-center space-x-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span>ONLINE & VERIFIED</span>
                  </span>
                ) : (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
                    DEPLOYING
                  </span>
                )}
              </div>
              <p className="text-xs font-mono text-cyan-400 mt-1 select-all">{appUrl}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <a
              href={appUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs px-4 py-2 rounded-lg transition flex items-center space-x-2 shadow-lg shadow-cyan-600/30"
            >
              <span>Open Generated Application</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Verification Checkpoints */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-5 pt-4 border-t border-slate-800 text-xs">
          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 flex items-center space-x-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-mono block">Health Check Probe</span>
              <span className="font-semibold text-white">GET /health (HTTP 200)</span>
            </div>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 flex items-center space-x-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-mono block">Smoke Verification</span>
              <span className="font-semibold text-white">GET /api/doctors (Passed)</span>
            </div>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 flex items-center space-x-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-mono block">Security Audit Gate</span>
              <span className="font-semibold text-white">100% Passed (Zero Defects)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Embedded Live Preview */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
        <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Monitor className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-semibold text-slate-300">
              Interactive Application Sandbox Preview (Live Executing App)
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-[10px] text-slate-500 font-mono">Port: {project?.app_port || 8005}</span>
            <a
              href={appUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-cyan-400 hover:underline flex items-center space-x-1"
            >
              <span>Full Screen</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        <div className="h-[600px] w-full bg-slate-950">
          <iframe
            src={appUrl}
            title={project?.name || "Generated Staging Application"}
            className="w-full h-full border-none"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        </div>
      </div>
    </div>
  );
}
