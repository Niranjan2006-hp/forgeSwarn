import React, { useState } from 'react';
import { FileCode, FileText, Database, Shield, Wrench, Download, Copy, Check } from 'lucide-react';

export default function ArtifactViewer({ artifacts = [] }) {
  const [selectedFile, setSelectedFile] = useState(
    artifacts.length > 0 ? artifacts[0].filename : 'engineering_contract.json'
  );
  const [copied, setCopied] = useState(false);

  if (!artifacts || artifacts.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
        <FileCode className="w-10 h-10 text-slate-600 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-slate-300">Project Memory Clean</h3>
        <p className="text-xs text-slate-500 mt-1">Artifacts are recorded dynamically as the swarm progresses.</p>
      </div>
    );
  }

  const activeArtifact = artifacts.find(a => a.filename === selectedFile) || artifacts[0];

  const handleCopy = () => {
    if (activeArtifact) {
      navigator.clipboard.writeText(activeArtifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getIconForFile = (filename) => {
    if (filename.endsWith('.sql')) return <Database className="w-3.5 h-3.5 text-cyan-400" />;
    if (filename.endsWith('.md')) return <FileText className="w-3.5 h-3.5 text-blue-400" />;
    if (filename.includes('security')) return <Shield className="w-3.5 h-3.5 text-rose-400" />;
    if (filename.includes('repair')) return <Wrench className="w-3.5 h-3.5 text-amber-400" />;
    return <FileCode className="w-3.5 h-3.5 text-emerald-400" />;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col md:flex-row min-h-[550px]">
      {/* File Sidebar */}
      <div className="w-full md:w-64 bg-slate-950/80 border-b md:border-b-0 md:border-r border-slate-800 p-3 space-y-1">
        <span className="text-[10px] font-mono uppercase text-slate-500 tracking-wider px-2 block mb-2">
          Shared Project Memory ({artifacts.length})
        </span>

        {artifacts.map((art) => (
          <button
            key={art.id}
            onClick={() => setSelectedFile(art.filename)}
            className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs font-mono transition text-left ${
              (selectedFile === art.filename)
                ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {getIconForFile(art.filename)}
            <span className="truncate">{art.filename}</span>
          </button>
        ))}
      </div>

      {/* Content Viewer */}
      <div className="flex-1 flex flex-col bg-[#070A0F]">
        <div className="p-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getIconForFile(activeArtifact.filename)}
            <span className="text-xs font-mono font-semibold text-slate-200">{activeArtifact.filename}</span>
            <span className="text-[10px] text-slate-500 font-mono">Created by: {activeArtifact.created_by}</span>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>

        <div className="p-4 flex-1 overflow-auto max-h-[500px]">
          <pre className="font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
            {activeArtifact.content}
          </pre>
        </div>
      </div>
    </div>
  );
}
