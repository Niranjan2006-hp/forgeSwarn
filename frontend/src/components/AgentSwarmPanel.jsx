import React from 'react';
import { Bot, Check, Shield, Cpu, Terminal, Wrench, Bug, Sparkles, HelpCircle } from 'lucide-react';

export default function AgentSwarmPanel({ agents = [] }) {
  if (!agents || agents.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
        <Bot className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h3 className="text-sm font-medium text-slate-400">Swarm Formation Pending</h3>
        <p className="text-xs text-slate-500 mt-1">Agents will be dynamically assembled based on the Engineering Contract.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
          Dynamically Formed Swarm ({agents.length} Specialized Agents)
        </h3>
        <span className="text-[11px] text-cyan-400 font-mono">100% Autonomous Consensus</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((ag) => (
          <div
            key={ag.id}
            className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl p-4.5 transition-all shadow-md hover:shadow-cyan-950/20 flex flex-col justify-between"
          >
            <div>
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2.5">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs"
                    style={{ backgroundColor: `${ag.avatar_color}25`, color: ag.avatar_color, border: `1px solid ${ag.avatar_color}60` }}
                  >
                    <Bot className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white leading-tight">{ag.name}</h4>
                    <p className="text-[11px] text-slate-400">{ag.role}</p>
                  </div>
                </div>

                <div className="flex flex-col items-end">
                  <span className="flex items-center space-x-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/70 text-emerald-400 border border-emerald-800/80">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span>ACTIVE</span>
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono mt-1">
                    Conf: {Math.round((ag.confidence || 0.95) * 100)}%
                  </span>
                </div>
              </div>

              {/* Selection Reasoning */}
              {ag.selection_reason && (
                <div className="bg-slate-950/70 border border-slate-800/70 rounded-lg p-2.5 mb-3 text-[11px] text-slate-300 leading-relaxed">
                  <span className="font-semibold text-cyan-400">Why Selected: </span>
                  {ag.selection_reason}
                </div>
              )}

              {/* Capabilities */}
              <div className="mb-3">
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 block mb-1.5">
                  Declared Capabilities
                </span>
                <div className="flex flex-wrap gap-1">
                  {(ag.capabilities || []).map((cap, i) => (
                    <span
                      key={i}
                      className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60"
                    >
                      {cap.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Restrictions */}
            {ag.restrictions && ag.restrictions.length > 0 && (
              <div className="pt-2 border-t border-slate-800/70 text-[10px] text-slate-500 flex items-center space-x-1">
                <Shield className="w-3 h-3 text-slate-500" />
                <span>Restricted: {ag.restrictions.join(', ').replace(/_/g, ' ')}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
