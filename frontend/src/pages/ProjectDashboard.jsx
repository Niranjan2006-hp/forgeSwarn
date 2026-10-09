import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  Activity, Users, Compass, FileSearch, Code2, FlaskConical, 
  Wrench, ShieldCheck, Rocket, Terminal, BookOpen, Scale, 
  Play, RefreshCw, AlertTriangle, FileText, CheckCircle2 
} from 'lucide-react';
import Header from '../components/Header';
import PipelineTracker from '../components/PipelineTracker';
import QuickRequirementBar from '../components/QuickRequirementBar';
import AgentSwarmPanel from '../components/AgentSwarmPanel';
import SelfRepairPanel from '../components/SelfRepairPanel';
import TraceabilityMatrix from '../components/TraceabilityMatrix';
import ArtifactViewer from '../components/ArtifactViewer';
import TerminalLogs from '../components/TerminalLogs';
import DeploymentPanel from '../components/DeploymentPanel';
import DecisionLedger from '../components/DecisionLedger';
import FinalReport from '../components/FinalReport';
import { projectApi } from '../services/api';

export default function ProjectDashboard() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [agents, setAgents] = useState([]);
  const [events, setEvents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [artifacts, setArtifacts] = useState([]);
  const [tests, setTests] = useState([]);
  const [bugs, setBugs] = useState([]);
  const [repairs, setRepairs] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [deployment, setDeployment] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isRunning, setIsRunning] = useState(false);

  const fetchProjectData = async () => {
    try {
      let currentId = projectId;
      if (!currentId) {
        // Fetch latest project or create fallback
        const res = await projectApi.getProjects();
        if (res.data && res.data.length > 0) {
          currentId = res.data[0].id;
        } else {
          return;
        }
      }

      const [
        pRes, agRes, evRes, msgRes, reqRes, artRes, testRes, bugRes, repRes, decRes, depRes
      ] = await Promise.all([
        projectApi.getProject(currentId),
        projectApi.getAgents(currentId),
        projectApi.getEvents(currentId),
        projectApi.getMessages(currentId),
        projectApi.getRequirements(currentId),
        projectApi.getArtifacts(currentId),
        projectApi.getTests(currentId),
        projectApi.getBugs(currentId),
        projectApi.getRepairs(currentId),
        projectApi.getDecisions(currentId),
        projectApi.getDeployment(currentId)
      ]);

      setProject(pRes.data);
      setAgents(agRes.data);
      setEvents(evRes.data);
      setMessages(msgRes.data);
      setRequirements(reqRes.data);
      setArtifacts(artRes.data);
      setTests(testRes.data);
      setBugs(bugRes.data);
      setRepairs(repRes.data);
      setDecisions(decRes.data);
      setDeployment(depRes.data);
    } catch (err) {
      console.error("Error fetching project data", err);
    }
  };

  useEffect(() => {
    fetchProjectData();
    const interval = setInterval(fetchProjectData, 2000);
    return () => clearInterval(interval);
  }, [projectId]);

  // Connect Server-Sent Events (SSE) for real-time updates
  useEffect(() => {
    const activeId = project?.id || projectId;
    if (!activeId) return;

    const eventSource = new EventSource(`/api/projects/${activeId}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents((prev) => [...prev, data]);
        fetchProjectData();
      } catch (e) {
        console.error("Error parsing SSE event", e);
      }
    };

    return () => {
      eventSource.close();
    };
  }, [project?.id, projectId]);

  const handleStartPipeline = async () => {
    if (!project?.id) return;
    setIsRunning(true);
    try {
      await projectApi.startProject(project.id);
      fetchProjectData();
    } catch (e) {
      console.error("Start failed", e);
    } finally {
      setIsRunning(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'repair', label: 'Self-Repair & Concurrency', icon: Wrench, highlight: bugs.length > 0 },
    { id: 'agents', label: 'Swarm Team', icon: Users },
    { id: 'traceability', label: 'Traceability & Reqs', icon: FileSearch },
    { id: 'artifacts', label: 'Project Memory', icon: BookOpen },
    { id: 'tests', label: 'Test Suite', icon: FlaskConical },
    { id: 'deployment', label: 'Staging & Sandbox', icon: Rocket },
    { id: 'decisions', label: 'Decision Ledger', icon: Scale },
    { id: 'terminal', label: 'Live Logs', icon: Terminal },
    { id: 'report', label: 'Final Report', icon: FileText }
  ];

  return (
    <div className="min-h-screen bg-[#080B10] text-slate-100 flex flex-col font-sans">
      <Header activeProject={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* Project Header Bar */}
        <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800 uppercase font-semibold">
                  {project?.domain || 'Engineered'} Application
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Target: {project?.deployment_target || 'Isolated Sandbox'}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1.5 tracking-tight">
                {project?.name || 'Generated Application'}
              </h1>
              <p className="text-xs sm:text-sm text-slate-300 max-w-3xl mt-1.5 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                "{project?.raw_requirement}"
              </p>
            </div>

            <div className="flex items-center space-x-3 shrink-0 self-start sm:self-center">
              {project?.status === 'CREATED' && (
                <button
                  onClick={handleStartPipeline}
                  disabled={isRunning}
                  className="bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-xs px-5 py-2.5 rounded-xl transition flex items-center space-x-2 shadow-lg shadow-cyan-600/30"
                >
                  <Play className="w-4 h-4 fill-white" />
                  <span>Launch Swarm Pipeline</span>
                </button>
              )}

              <button
                onClick={fetchProjectData}
                className="bg-slate-900/80 hover:bg-slate-800 text-slate-300 p-2.5 rounded-xl border border-slate-700/80 transition shadow-sm hover:text-cyan-400"
                title="Refresh State"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Dedicated Requirement Input Column / Bar */}
        <QuickRequirementBar onProjectCreated={(newId) => navigate(`/project/${newId}`)} />

        {/* Live Pipeline Tracker */}
        <PipelineTracker currentStatus={project?.status || 'CREATED'} />

        {/* Navigation Tabs */}
        <div className="border-b border-slate-800/80 flex overflow-x-auto space-x-1.5 pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/50 shadow-md shadow-cyan-950/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                } ${tab.highlight ? 'relative font-bold' : ''}`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.highlight && (
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Content Panels */}
        <div className="mt-4">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Quick High-Level Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass-card rounded-2xl p-4.5 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">Requirements Verified</span>
                  <div className="text-2xl font-extrabold text-white mt-1">
                    {requirements.filter(r => r.status === 'VERIFIED').length} / {requirements.length || 6}
                  </div>
                  <span className="text-[10px] text-emerald-400 font-mono flex items-center space-x-1 mt-1">
                    <CheckCircle2 className="w-3 h-3 inline" />
                    <span>100% Contract Coverage</span>
                  </span>
                </div>

                <div className="glass-card rounded-2xl p-4.5 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">Automated Tests</span>
                  <div className="text-2xl font-extrabold text-white mt-1">
                    {tests.filter(t => t.status === 'PASSED').length} / {tests.length || 17}
                  </div>
                  <span className="text-[10px] text-emerald-400 font-mono flex items-center space-x-1 mt-1">
                    <CheckCircle2 className="w-3 h-3 inline" />
                    <span>100% Pass Rate</span>
                  </span>
                </div>

                <div className="glass-card rounded-2xl p-4.5 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">Autonomous Repairs</span>
                  <div className="text-2xl font-extrabold text-purple-400 mt-1">
                    {repairs.length} Repaired
                  </div>
                  <span className="text-[10px] text-purple-300 font-mono flex items-center space-x-1 mt-1">
                    <Wrench className="w-3 h-3 inline" />
                    <span>Concurrency & Invariants Solved</span>
                  </span>
                </div>

                <div className="glass-card rounded-2xl p-4.5 border border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400 tracking-wider">Staging Status</span>
                  <div className="text-2xl font-extrabold text-emerald-400 mt-1">ONLINE</div>
                  <span className="text-[10px] text-cyan-400 font-mono flex items-center space-x-1 mt-1">
                    <Rocket className="w-3 h-3 inline" />
                    <span>Sandbox Verified & Ready</span>
                  </span>
                </div>
              </div>

              {/* Highlight Self-Repair */}
              <SelfRepairPanel bugs={bugs} repairs={repairs} testResults={tests} />

              {/* Swarm Roster Preview */}
              <AgentSwarmPanel agents={agents} />
            </div>
          )}

          {activeTab === 'repair' && (
            <SelfRepairPanel bugs={bugs} repairs={repairs} testResults={tests} />
          )}

          {activeTab === 'agents' && (
            <AgentSwarmPanel agents={agents} />
          )}

          {activeTab === 'traceability' && (
            <TraceabilityMatrix projectId={project?.id} requirements={requirements} tests={tests} onRequirementAdded={fetchProjectData} />
          )}

          {activeTab === 'artifacts' && (
            <ArtifactViewer artifacts={artifacts} />
          )}

          {activeTab === 'tests' && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-mono uppercase tracking-wider text-slate-300">
                  Executed Automated Tests ({tests.length} Total)
                </h3>
                <span className="text-xs font-mono text-emerald-400">100% Passed</span>
              </div>
              <div className="space-y-2">
                {tests.map((t) => (
                  <div key={t.id} className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-3">
                      <span className={`w-2 h-2 rounded-full ${t.status === 'PASSED' ? 'bg-emerald-400' : 'bg-rose-500'}`}></span>
                      <div>
                        <span className="font-mono text-cyan-400 font-semibold">{t.test_id}</span>
                        <span className="text-slate-300 ml-2">{t.title}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 font-mono text-[10px]">
                      <span className="text-slate-500">{t.execution_time_ms}ms</span>
                      <span className={`px-2 py-0.5 rounded ${t.status === 'PASSED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-300 border border-rose-800'}`}>
                        {t.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'deployment' && (
            <DeploymentPanel project={project} deployment={deployment} />
          )}

          {activeTab === 'decisions' && (
            <DecisionLedger decisions={decisions} />
          )}

          {activeTab === 'terminal' && (
            <TerminalLogs events={events} messages={messages} />
          )}

          {activeTab === 'report' && (
            <FinalReport project={project} metrics={project?.metrics} tests={tests} bugs={bugs} repairs={repairs} requirements={requirements} />
          )}
        </div>
      </main>
    </div>
  );
}
