import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Bot, Sparkles, Filter, ChevronRight } from 'lucide-react';

export default function TerminalLogs({ events = [], messages = [] }) {
  const [filter, setFilter] = useState('ALL'); // ALL, AGENTS, SYSTEM
  const terminalEndRef = useRef(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events, messages]);

  const combinedLogs = [
    ...events.map(e => ({
      type: 'EVENT',
      source: e.source,
      message: e.message,
      level: e.level,
      timestamp: e.timestamp
    })),
    ...messages.map(m => ({
      type: 'MESSAGE',
      source: m.sender_name,
      message: m.content,
      level: m.category,
      timestamp: m.created_at
    }))
  ].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const filteredLogs = combinedLogs.filter(log => {
    if (filter === 'AGENTS') return log.type === 'MESSAGE' || log.source.includes('Agent');
    if (filter === 'SYSTEM') return log.type === 'EVENT';
    return true;
  });

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col h-[520px]">
      {/* Terminal Header */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></span>
          </div>
          <span className="text-xs font-mono text-slate-400 ml-2">forge-terminal — live activity & swarm consensus</span>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center space-x-1">
          {['ALL', 'AGENTS', 'SYSTEM'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-0.5 rounded text-[10px] font-mono transition ${
                filter === f ? 'bg-cyan-900 text-cyan-200 border border-cyan-700' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Log Feed */}
      <div className="flex-1 p-4 font-mono text-xs overflow-y-auto space-y-2 bg-[#05080E]">
        <div className="text-slate-600 text-[11px] pb-2 border-b border-slate-900">
          [SYSTEM INITIALIZED] Event listener active. Receiving real-time SSE stream.
        </div>

        {filteredLogs.map((log, index) => {
          let badgeColor = 'text-cyan-400 bg-cyan-950/40 border-cyan-800';
          let levelTag = '[INFO]';
          let textColor = 'text-slate-300';

          if (log.level === 'SUCCESS' || log.level === 'CONSENSUS') {
            badgeColor = 'text-emerald-400 bg-emerald-950/40 border-emerald-800';
            levelTag = '[PASS]';
            textColor = 'text-emerald-200';
          } else if (log.level === 'WARNING') {
            badgeColor = 'text-amber-400 bg-amber-950/40 border-amber-800';
            levelTag = '[WARN]';
            textColor = 'text-amber-200';
          } else if (log.level === 'ERROR') {
            badgeColor = 'text-rose-400 bg-rose-950/40 border-rose-800';
            levelTag = '[FAIL]';
            textColor = 'text-rose-200 font-bold';
          }

          const time = new Date(log.timestamp).toLocaleTimeString();

          return (
            <div key={index} className="flex items-start space-x-2 hover:bg-slate-900/40 p-1 rounded transition">
              <span className="text-[10px] text-slate-600 shrink-0 select-none">[{time}]</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded border font-bold uppercase shrink-0 ${badgeColor}`}>
                {log.source}
              </span>
              <span className={`leading-relaxed break-words ${textColor}`}>
                {log.message}
              </span>
            </div>
          );
        })}

        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
