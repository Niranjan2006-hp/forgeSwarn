import React from 'react';
import { GitCommit, Check, Sparkles, Scale, Layers } from 'lucide-react';

export default function DecisionLedger({ decisions = [] }) {
  if (!decisions || decisions.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
        <Scale className="w-10 h-10 text-slate-600 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-slate-300">Decision Ledger Pending</h3>
        <p className="text-xs text-slate-500 mt-1">Decisions are logged dynamically as agents debate trade-offs.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400">
          Agent Architectural Consensus & Decision Ledger ({decisions.length})
        </h3>
        <span className="text-[11px] text-cyan-400 font-mono">Immutable Audit Trail</span>
      </div>

      <div className="space-y-3">
        {decisions.map((dec) => (
          <div
            key={dec.id}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-md hover:border-slate-700 transition"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold uppercase">
                    Consensus Conf: {Math.round((dec.confidence || 0.95) * 100)}%
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {new Date(dec.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white mt-1.5">{dec.decision}</h4>
              </div>

              <div className="flex -space-x-1.5 overflow-hidden">
                {(dec.participating_agents || []).map((agName, i) => (
                  <div
                    key={i}
                    title={agName}
                    className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-cyan-300"
                  >
                    {agName.charAt(0)}
                  </div>
                ))}
              </div>
            </div>

            <p className="text-xs text-slate-300 mt-2.5 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <span className="text-cyan-400 font-semibold">Architectural Rationale: </span>
              {dec.reason}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3 pt-3 border-t border-slate-800 text-[11px]">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-500 block mb-1">
                  Evaluated Alternatives:
                </span>
                <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                  {(dec.alternatives || []).map((alt, j) => (
                    <li key={j}>{alt}</li>
                  ))}
                </ul>
              </div>

              <div>
                <span className="text-[10px] uppercase font-mono text-slate-500 block mb-1">
                  Affected Components:
                </span>
                <div className="flex flex-wrap gap-1">
                  {(dec.affected_components || []).map((comp, k) => (
                    <span
                      key={k}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700"
                    >
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
