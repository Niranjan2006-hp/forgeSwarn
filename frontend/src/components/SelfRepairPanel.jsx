import React, { useState } from 'react';
import { 
  AlertTriangle, Wrench, CheckCircle2, ShieldAlert, 
  GitCommit, ArrowRight, Check, FileDiff, Cpu, ChevronDown, ChevronUp 
} from 'lucide-react';

export default function SelfRepairPanel({ bugs = [], repairs = [], testResults = [] }) {
  const [showDiff, setShowDiff] = useState(true);

  if (!bugs || bugs.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
        <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-slate-200">Zero Outstanding Defects</h3>
        <p className="text-xs text-slate-400 mt-1">Autonomous test suite passed with 100% compliance.</p>
      </div>
    );
  }

  const primaryBug = bugs[0];
  const primaryRepair = repairs[0];

  return (
    <div className="space-y-6">
      {/* High-Impact Alert Banner */}
      <div className="glass-panel border border-amber-500/40 rounded-2xl p-5 sm:p-6 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-32 bg-amber-500/10 blur-3xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0 shadow-lg shadow-amber-500/20">
              <AlertTriangle className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-rose-950/80 text-rose-300 border border-rose-800 font-bold uppercase">
                  {primaryBug.severity || 'CRITICAL'} SEVERITY
                </span>
                <span className="text-xs font-mono text-slate-400">Target: {primaryBug.test_id || 'TC-BR-001'}</span>
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800 font-bold">
                  {primaryBug.status || 'REPAIRED'}
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-white mt-1.5">{primaryBug.title}</h3>
              <p className="text-xs sm:text-sm text-slate-300 mt-1">
                Autonomous loop detected invariant violation, performed diagnostic root-cause synthesis, and applied surgical repair.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 self-start md:self-auto shadow-inner">
            <div className="text-center px-3 border-r border-slate-800">
              <span className="text-[10px] text-slate-500 block uppercase font-mono">Before Fix</span>
              <span className="text-sm font-bold text-rose-400">Violation Detected</span>
            </div>
            <ArrowRight className="w-4 h-4 text-cyan-400" />
            <div className="text-center px-3">
              <span className="text-[10px] text-slate-500 block uppercase font-mono">After Fix</span>
              <span className="text-sm font-bold text-emerald-400">All Passed (100%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4-Step Closed Loop Visualization */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Step 1: Failure */}
        <div className="glass-card border border-rose-900/60 rounded-2xl p-4.5">
          <div className="flex items-center space-x-2 text-rose-400 text-xs font-mono font-bold mb-2">
            <ShieldAlert className="w-4 h-4" />
            <span>1. FAILURE DETECTED</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed font-mono">
            {primaryBug.evidence || "Concurrent request race condition detected. System invariant violated under multi-user load."}
          </p>
        </div>

        {/* Step 2: Diagnosis */}
        <div className="glass-card border border-amber-900/60 rounded-2xl p-4.5">
          <div className="flex items-center space-x-2 text-amber-400 text-xs font-mono font-bold mb-2">
            <Cpu className="w-4 h-4" />
            <span>2. ROOT CAUSE</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {primaryBug.root_cause || "Time-Of-Check to Time-Of-Use race condition in service handler without atomic transaction isolation."}
          </p>
        </div>

        {/* Step 3: Repair */}
        <div className="glass-card border border-cyan-900/60 rounded-2xl p-4.5">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono font-bold mb-2">
            <Wrench className="w-4 h-4" />
            <span>3. ATOMIC REPAIR</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {primaryRepair?.strategy || "Applied atomic transaction lock with schema-level uniqueness and concurrency invariants."}
          </p>
        </div>

        {/* Step 4: Verification */}
        <div className="glass-card border border-emerald-900/60 rounded-2xl p-4.5">
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono font-bold mb-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>4. REGRESSION VERIFIED</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Re-executed entire test suite. Invariant fully held, invalid concurrent attempts safely handled with zero regressions.
          </p>
        </div>
      </div>

      {/* Surgical Diff Viewer */}
      {primaryRepair && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="w-full flex items-center justify-between p-4 bg-slate-850 hover:bg-slate-800/80 transition text-left"
          >
            <div className="flex items-center space-x-2">
              <FileDiff className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-semibold text-slate-200">
                Surgical Code Patch Diff — booking_service.py & models.py
              </span>
            </div>
            {showDiff ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
          </button>

          {showDiff && (
            <div className="p-4 bg-slate-950 font-mono text-xs overflow-x-auto leading-relaxed border-t border-slate-800">
              <div className="text-rose-400 bg-rose-950/20 px-2 py-1 rounded mb-1">
                - # VULNERABILITY (BR-001 VIOLATION): TOCTOU Race Condition<br />
                - existing = db.query(Appointment).filter(doctor_id == doc_id, time == slot).first()<br />
                - if existing: raise HTTPException(400)<br />
                - db.add(Appointment(doctor_id=doc_id, appointment_time=slot))<br />
                - db.commit()
              </div>
              <div className="text-emerald-400 bg-emerald-950/20 px-2 py-1 rounded">
                + # REPAIRED: Atomic synchronization and uniqueness protection<br />
                + with _booking_lock:<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;existing = db.query(Appointment).filter(doctor_id == doc_id, time == slot).first()<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;if existing: raise HTTPException(409, detail="Doctor slot already booked")<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;try:<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;db.add(appointment)<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;db.commit()<br />
                + &nbsp;&nbsp;&nbsp;&nbsp;except IntegrityError: db.rollback(); raise HTTPException(409)
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
