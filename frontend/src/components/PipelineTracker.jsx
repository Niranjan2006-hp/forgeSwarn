import React from 'react';
import { 
  FileSearch, FileCode2, Users2, Compass, Code2, 
  GitMerge, FlaskConical, Wrench, ShieldCheck, Rocket, 
  CheckCircle2, AlertCircle, Loader2 
} from 'lucide-react';

const STAGES = [
  { id: 'ANALYZING', label: 'Requirement Analysis', icon: FileSearch },
  { id: 'CONTRACT_GENERATED', label: 'Engineering Contract', icon: FileCode2 },
  { id: 'TEAM_FORMED', label: 'Team Formation', icon: Users2 },
  { id: 'ARCHITECTING', label: 'Architecture Design', icon: Compass },
  { id: 'DEVELOPING', label: 'Development', icon: Code2 },
  { id: 'TESTING', label: 'Testing & Concurrency', icon: FlaskConical },
  { id: 'REPAIRING', label: 'Self-Repair & Diagnosis', icon: Wrench },
  { id: 'SECURITY_REVIEW', label: 'Security Gate', icon: ShieldCheck },
  { id: 'DEPLOYING', label: 'Deployment & Staging', icon: Rocket }
];

export default function PipelineTracker({ currentStatus }) {
  const getStageState = (stageId, index) => {
    const statusOrder = [
      'CREATED',
      'ANALYZING',
      'CONTRACT_GENERATED',
      'TEAM_FORMED',
      'ARCHITECTING',
      'DEVELOPING',
      'TESTING',
      'FAILURE_DETECTED',
      'DIAGNOSING',
      'REPAIRING',
      'REGRESSION_TESTING',
      'SECURITY_REVIEW',
      'DEPLOYING',
      'COMPLETED'
    ];

    if (currentStatus === 'COMPLETED') return 'completed';
    if (currentStatus === 'FAILED') {
      const failedIdx = statusOrder.indexOf(currentStatus);
      if (index === failedIdx) return 'failed';
    }

    // Mapping currentStatus to active stage index
    let activeIndex = 0;
    if (currentStatus === 'ANALYZING') activeIndex = 0;
    else if (currentStatus === 'CONTRACT_GENERATED') activeIndex = 1;
    else if (currentStatus === 'TEAM_FORMED') activeIndex = 2;
    else if (currentStatus === 'ARCHITECTING') activeIndex = 3;
    else if (currentStatus === 'DEVELOPING') activeIndex = 4;
    else if (currentStatus === 'TESTING' || currentStatus === 'FAILURE_DETECTED') activeIndex = 5;
    else if (currentStatus === 'DIAGNOSING' || currentStatus === 'REPAIRING' || currentStatus === 'REGRESSION_TESTING') activeIndex = 6;
    else if (currentStatus === 'SECURITY_REVIEW') activeIndex = 7;
    else if (currentStatus === 'DEPLOYING') activeIndex = 8;
    else if (currentStatus === 'COMPLETED') activeIndex = 9;

    if (index < activeIndex) return 'completed';
    if (index === activeIndex) return 'running';
    return 'pending';
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide uppercase font-mono flex items-center space-x-2">
            <span>Swarm Engineering Pipeline</span>
            <span className="text-[11px] text-cyan-400 font-normal">({currentStatus})</span>
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-2">
        {STAGES.map((stg, idx) => {
          const state = getStageState(stg.id, idx);
          const Icon = stg.icon;

          let badgeColor = 'bg-slate-800/40 text-slate-500 border-slate-800';
          let iconColor = 'text-slate-500';
          let indicator = null;

          if (state === 'completed') {
            badgeColor = 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60';
            iconColor = 'text-emerald-400';
            indicator = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
          } else if (state === 'running') {
            badgeColor = 'bg-cyan-950/80 text-cyan-200 border-cyan-500 shadow-md shadow-cyan-500/20';
            iconColor = 'text-cyan-400 animate-pulse';
            indicator = <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin" />;
          } else if (state === 'failed') {
            badgeColor = 'bg-rose-950/60 text-rose-300 border-rose-800';
            iconColor = 'text-rose-400';
            indicator = <AlertCircle className="w-3.5 h-3.5 text-rose-400" />;
          }

          return (
            <div
              key={stg.id}
              className={`p-3 rounded-lg border flex flex-col items-center justify-between text-center transition-all ${badgeColor}`}
            >
              <div className="flex items-center justify-between w-full mb-2">
                <span className="text-[10px] font-mono text-slate-400">0{idx + 1}</span>
                {indicator || <span className="w-2 h-2 rounded-full bg-slate-700"></span>}
              </div>
              <Icon className={`w-5 h-5 mb-2 ${iconColor}`} />
              <span className="text-[11px] font-medium leading-tight">{stg.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
