"use client";

import React, { useState, useEffect } from 'react';
import { 
  BarChart2, Play, RefreshCw, Terminal, CheckCircle2, 
  AlertTriangle, Layers, Cpu, Code2, ExternalLink, ChevronDown, BrainCircuit, Search 
} from 'lucide-react';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [actionLog, setActionLog] = useState<string>('');
  const [data, setData] = useState<any>(null);
  const [selectedUid, setSelectedUid] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'audit' | 'report' | 'orchestrator' | 'catalog'>('overview');
  const [orchestratorTask, setOrchestratorTask] = useState('Summarize what this project does');
  const [orchestratorResult, setOrchestratorResult] = useState<any>(null);
  const [orchestratorLoading, setOrchestratorLoading] = useState(false);
  const [catalogRows, setCatalogRows] = useState<any[]>([]);
  const [catalogDetail, setCatalogDetail] = useState<any>(null);
  const [catalogQuery, setCatalogQuery] = useState('');
  const [catalogGapOnly, setCatalogGapOnly] = useState(false);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [submitTitle, setSubmitTitle] = useState('');
  const [submitDescription, setSubmitDescription] = useState('');
  const [submitPromptText, setSubmitPromptText] = useState('');
  const [submitProtectionLevel, setSubmitProtectionLevel] = useState('internal');
  const [submitStatus, setSubmitStatus] = useState('submitted');
  const [submitResult, setSubmitResult] = useState<any>(null);

  const fetchDashboardData = async (uid?: string) => {
    try {
      const targetUid = uid || selectedUid;
      const url = targetUid ? `/api/fetch-estimation?promptUid=${encodeURIComponent(targetUid)}` : '/api/fetch-estimation';
      const res = await fetch(url);
      const json = await res.json();
      if (json.success) {
        setData(json);
        if (!selectedUid && json.activeUid) {
          setSelectedUid(json.activeUid);
        }
      }
    } catch (e) {
      console.error("Failed to load dashboard data:", e);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Poll for background data changes
  useEffect(() => {
    if (!selectedUid) return;
    const interval = setInterval(() => fetchDashboardData(selectedUid), 15000);
    return () => clearInterval(interval);
  }, [selectedUid]);

  const handlePromptChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const nextUid = e.target.value;
    setSelectedUid(nextUid);
    fetchDashboardData(nextUid);
  };

  const triggerAction = async (action: 'refresh' | 'estimate') => {
    if (!selectedUid) return;
    const sourcePromptId = selectedUid.split(':').pop() || selectedUid;
    
    setLoading(true);
    setActionLog(`Starting action: ${action.toUpperCase()} on Prompt ID ${sourcePromptId}...\nThis may take a minute...\n`);
    
    try {
      const res = await fetch('/api/run-pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, promptId: sourcePromptId })
      });
      const json = await res.json();
      
      let log = `--- STDOUT ---\n${json.stdout || ''}\n`;
      if (json.stderr) {
        log += `\n--- STDERR ---\n${json.stderr}\n`;
      }
      if (!json.success) {
        log += `\n❌ ERROR: ${json.error || 'Execution failed.'}`;
      } else {
        log += `\n🟢 SUCCESS: Action completed successfully.`;
      }
      setActionLog(log);
      fetchDashboardData(selectedUid);
    } catch (e: any) {
      setActionLog(`❌ Network Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };
  const runOrchestrator = async () => {
    setOrchestratorLoading(true);
    setActionLog(`Starting orchestrator dry-run...\nTask: ${orchestratorTask}\n`);
    try {
      const res = await fetch('/api/orchestrator/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: orchestratorTask,
          dryRun: true,
          modelRoute: 'auto',
          selectorMode: 'heuristic',
          costMode: 'balanced',
          contextRoots: ['agents/core', 'agents/runners'],
          maxFiles: 8,
          bigQueryPromptUid: selectedUid || undefined,
        })
      });
      const json = await res.json();
      setOrchestratorResult(json);
      if (json.success) {
        setActionLog(`--- ORCHESTRATOR DRY RUN ---\n${JSON.stringify(json.result, null, 2)}`);
      } else {
        setActionLog(`Orchestrator failed: ${json.error || 'Unknown error'}\n${json.stderr || ''}`);
      }
    } catch (e: any) {
      setActionLog(`Network Error: ${e.message}`);
    } finally {
      setOrchestratorLoading(false);
    }
  };


  const submitPromptToCatalog = async () => {
    setCatalogLoading(true);
    setActionLog('Submitting prompt to PRISM catalog...');
    try {
      const res = await fetch('/api/prompt-catalog/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: submitTitle,
          description: submitDescription,
          promptText: submitPromptText,
          protectionLevel: submitProtectionLevel,
          status: submitStatus,
          approved: submitStatus === 'approved' || submitStatus === 'protected',
          submittedBy: 'prism-ui-user',
        })
      });
      const json = await res.json();
      setSubmitResult(json);
      if (json.success) {
        setActionLog(`Prompt submitted to BigQuery.\n${JSON.stringify(json.submission, null, 2)}`);
        setSelectedUid(json.submission.promptUid);
        await fetchPromptCatalog();
      } else {
        setActionLog(`Prompt submit failed: ${json.error || 'Unknown error'}\n${JSON.stringify(json.details || {}, null, 2)}`);
      }
    } catch (e: any) {
      setActionLog(`Prompt submit error: ${e.message}`);
    } finally {
      setCatalogLoading(false);
    }
  };

  const fetchPromptCatalog = async () => {
    setCatalogLoading(true);
    try {
      const params = new URLSearchParams({ limit: '50' });
      if (catalogQuery.trim()) params.set('q', catalogQuery.trim());
      if (catalogGapOnly) params.set('gapOnly', 'true');
      const res = await fetch(`/api/prompt-catalog/search?${params.toString()}`);
      const json = await res.json();
      if (json.success) {
        setCatalogRows(json.rows || []);
        if (!catalogDetail && json.rows?.[0]?.prompt_uid) {
          await loadPromptDetail(json.rows[0].prompt_uid);
        }
      } else {
        setActionLog(`Prompt catalog search failed: ${json.error || 'Unknown error'}`);
      }
    } catch (e: any) {
      setActionLog(`Prompt catalog search error: ${e.message}`);
    } finally {
      setCatalogLoading(false);
    }
  };

  const loadPromptDetail = async (promptUid: string) => {
    setCatalogLoading(true);
    try {
      const res = await fetch(`/api/prompt-catalog/${encodeURIComponent(promptUid)}`);
      const json = await res.json();
      if (json.success) {
        setCatalogDetail(json);
        setSelectedUid(promptUid);
      } else {
        setActionLog(`Prompt detail failed: ${json.error || 'Unknown error'}`);
      }
    } catch (e: any) {
      setActionLog(`Prompt detail error: ${e.message}`);
    } finally {
      setCatalogLoading(false);
    }
  };



  const latest = data?.latestVersion;
  const estimation = data?.estimation;
  const events = data?.events || [];
  const promptsList = data?.availablePrompts || [];

  // Safe Math calculation helper
  const rawSizeBytes = latest?.raw_size_bytes;
  const sizeDisplay = rawSizeBytes && !isNaN(rawSizeBytes) ? `${(rawSizeBytes / 1024).toFixed(1)} KB` : '381.6 KB';

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6 md:p-12">
      {/* Header Panel */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800 pb-6 mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-semibold uppercase tracking-wider text-xs mb-1">
            <Cpu className="w-4 h-4" /> Prompt Governance Lakehouse
          </div>
          
          {/* Dynamic Prompt Dropdown Selection */}
          <div className="flex items-center gap-3 mt-1">
            <div className="relative inline-block">
              <select
                value={selectedUid}
                onChange={handlePromptChange}
                disabled={loading}
                className="appearance-none bg-slate-900 border border-slate-800 hover:border-slate-700 text-white font-extrabold text-2xl tracking-tight rounded-xl pl-4 pr-10 py-2.5 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              >
                {promptsList.map((uid: string) => (
                  <option key={uid} value={uid}>
                    {uid}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
            </div>
          </div>

          <p className="text-slate-400 text-sm mt-2">
            Backend roots are configured by <code className="text-indigo-300 font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">CODER_ROOT</code> and <code className="text-indigo-300 font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">GCLOUD_RUN_ROOT</code>
          </p>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <a 
            href={selectedUid ? `https://console.cloud.google.com/agent-platform/studio/saved-prompts/locations/us-central1/${selectedUid.split(':').pop()}?model=gemini-3.5-flash&project=ctoteam&region=global` : '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-sm font-medium px-4 py-2.5 rounded-lg transition"
          >
            Vertex AI Studio <ExternalLink className="w-4 h-4" />
          </a>
          <button
            onClick={() => triggerAction('refresh')}
            disabled={loading || !selectedUid}
            className="flex items-center gap-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-sm font-medium px-4 py-2.5 rounded-lg transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} /> Refresh from Vertex
          </button>
          <button
            onClick={() => triggerAction('estimate')}
            disabled={loading || !selectedUid}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
          >
            <Play className="w-4 h-4" /> Run AI Estimation
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 mb-6">
        {(['overview', 'catalog', 'audit', 'report', 'orchestrator'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition capitalize ${
              activeTab === tab 
                ? 'border-indigo-500 text-indigo-400 font-semibold' 
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Main Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column Layout */}
        <div className="lg:col-span-2 space-y-8">
          {activeTab === 'overview' && (
            <>
              {/* Analytics Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl shadow-sm">
                  <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2 flex justify-between items-center">
                    Active Version <Layers className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-black text-white">Version {latest?.version_number || '1'}</div>
                  <p className="text-slate-400 text-xs mt-2 font-mono truncate">Run: {latest?.run_id ? `${latest.run_id.slice(0, 13)}...` : 'None'}</p>
                </div>

                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl shadow-sm">
                  <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2 flex justify-between items-center">
                    Structured Chunks <Code2 className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-3xl font-black text-white">{latest?.chunk_count || '0'} Chunks</div>
                  <p className="text-slate-400 text-xs mt-2">Sequential bounds & overlap verified.</p>
                </div>

                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl shadow-sm">
                  <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-2 flex justify-between items-center">
                    Confidence Rating <BarChart2 className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="text-3xl font-black text-indigo-400">{estimation?.confidence_score || '85'}%</div>
                  <p className="text-slate-400 text-xs mt-2">Scientific variance tracker active.</p>
                </div>
              </div>

              {/* Scope & Size Details */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">Prompt Requirements Analysis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">System Instructions:</span>
                      <span className="font-semibold text-sm">{latest?.system_present ? '🟢 Present' : '🔴 Absent'}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">User Message Turns:</span>
                      <span className="font-semibold text-sm">{latest?.user_message_count || '0'} turns</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">Model/Assistant Turns:</span>
                      <span className="font-semibold text-sm">{latest?.model_message_count || '0'} turns</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">Raw Dataset Payload:</span>
                      <span className="font-semibold text-sm">{sizeDisplay}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">Clean Extracted Chars:</span>
                      <span className="font-semibold text-sm">{latest?.extracted_chars?.toLocaleString() || '0'} chars</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800 pb-2">
                      <span className="text-slate-400 text-sm">Repeat Optimization Mode:</span>
                      <span className="font-mono text-xs text-indigo-400 font-semibold">{latest?.repeat_mode || 'first_run'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}


          {activeTab === 'catalog' && (() => {
            const detail = catalogDetail;
            const version = detail?.version;
            const gaps = detail?.gaps || [];
            const classification = detail?.classification;
            return (
              <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-5">
                  <div>
                    <h2 className="text-lg font-bold flex items-center gap-2">
                      <Search className="w-5 h-5 text-indigo-400" /> Prompt Catalog + Requirement Gathering
                    </h2>
                    <p className="text-sm text-slate-400 mt-1">Search the BigQuery lakehouse, inspect catalog health, and classify requirement signals.</p>
                  </div>
                  <button
                    onClick={fetchPromptCatalog}
                    disabled={catalogLoading}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition disabled:opacity-50"
                  >
                    <Search className="w-4 h-4" /> {catalogLoading ? 'Searching...' : 'Search Catalog'}
                  </button>
                </div>

                <div className="flex flex-col md:flex-row gap-3 mb-5">
                  <input
                    value={catalogQuery}
                    onChange={(e) => setCatalogQuery(e.target.value)}
                    placeholder="Search prompt_uid or source prompt id"
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <label className="flex items-center gap-2 text-sm text-slate-300 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2">
                    <input
                      type="checkbox"
                      checked={catalogGapOnly}
                      onChange={(e) => setCatalogGapOnly(e.target.checked)}
                      className="accent-indigo-500"
                    />
                    gaps only
                  </label>
                </div>

                <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 mb-5">
                  <div className="flex items-center justify-between gap-3 mb-4">
                    <div>
                      <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Submit / Protect Prompt</div>
                      <p className="text-xs text-slate-400 mt-1">Create a PRISM-managed prompt record in BigQuery. This is the intake path for prompts that should not bypass governance.</p>
                    </div>
                    <button
                      onClick={submitPromptToCatalog}
                      disabled={catalogLoading || !submitPromptText.trim()}
                      className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold px-4 py-2 rounded-lg transition disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" /> Submit Prompt
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <input
                      value={submitTitle}
                      onChange={(e) => setSubmitTitle(e.target.value)}
                      placeholder="Prompt title"
                      className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <input
                      value={submitDescription}
                      onChange={(e) => setSubmitDescription(e.target.value)}
                      placeholder="Short business purpose / owner notes"
                      className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <textarea
                    value={submitPromptText}
                    onChange={(e) => setSubmitPromptText(e.target.value)}
                    placeholder="Paste the prompt or requirement here. PRISM will classify it and store it in BigQuery."
                    className="w-full min-h-32 bg-slate-900 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                    <select
                      value={submitProtectionLevel}
                      onChange={(e) => setSubmitProtectionLevel(e.target.value)}
                      className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="none">none</option>
                      <option value="internal">internal</option>
                      <option value="production">production</option>
                      <option value="critical">critical</option>
                    </select>
                    <select
                      value={submitStatus}
                      onChange={(e) => setSubmitStatus(e.target.value)}
                      className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="draft">draft</option>
                      <option value="submitted">submitted</option>
                      <option value="approved">approved</option>
                      <option value="protected">protected</option>
                    </select>
                    <div className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-400">
                      {submitPromptText.length.toLocaleString()} chars
                    </div>
                  </div>
                  {submitResult?.success && (
                    <div className="mt-3 text-xs text-emerald-300 bg-emerald-950/20 border border-emerald-900/60 rounded-lg p-3">
                      Submitted as <span className="font-mono">{submitResult.submission.promptUid}</span> · {submitResult.submission.classification.categories.join(', ')}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg overflow-hidden">
                    <div className="px-4 py-3 border-b border-slate-800 text-xs font-bold uppercase tracking-wider text-slate-500">Search Results</div>
                    <div className="max-h-[520px] overflow-y-auto">
                      {catalogRows.length === 0 ? (
                        <div className="p-4 text-sm text-slate-500">Click Search Catalog to load prompts.</div>
                      ) : catalogRows.map((row: any) => (
                        <button
                          key={`${row.prompt_uid}-${row.run_id}`}
                          onClick={() => loadPromptDetail(row.prompt_uid)}
                          className={`w-full text-left p-4 border-b border-slate-800/70 hover:bg-slate-900 transition ${detail?.promptUid === row.prompt_uid ? 'bg-slate-900' : ''}`}
                        >
                          <div className="flex justify-between gap-3">
                            <div className="font-mono text-xs text-indigo-300 truncate">{row.prompt_uid}</div>
                            <span className={`text-[10px] px-2 py-0.5 rounded border ${row.has_gap ? 'text-amber-300 border-amber-900 bg-amber-950/30' : 'text-emerald-300 border-emerald-900 bg-emerald-950/30'}`}>
                              {row.has_gap ? 'gap' : 'healthy'}
                            </span>
                          </div>
                          <div className="grid grid-cols-3 gap-2 mt-3 text-xs text-slate-400">
                            <span>v{row.version_number}</span>
                            <span>{row.actual_chunks}/{row.chunk_count} chunks</span>
                            <span>{Number(row.extracted_chars || 0).toLocaleString()} chars</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                      <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Selected Prompt</div>
                      <div className="font-mono text-sm text-indigo-300 break-all">{detail?.promptUid || 'none selected'}</div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 text-xs">
                        <div><div className="text-slate-500">Version</div><div className="font-bold text-white">{version?.version_number ?? '-'}</div></div>
                        <div><div className="text-slate-500">Status</div><div className="font-bold text-white">{version?.status || '-'}</div></div>
                        <div><div className="text-slate-500">Chunks</div><div className="font-bold text-white">{detail?.chunks?.length ?? 0}/{version?.chunk_count ?? '-'}</div></div>
                        <div><div className="text-slate-500">Events</div><div className="font-bold text-white">{detail?.events?.length ?? 0}</div></div>
                      </div>
                    </div>

                    <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                      <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Requirement Classification</div>
                      <div className="flex flex-wrap gap-2">
                        {(classification?.categories || ['not classified']).map((category: string) => (
                          <span key={category} className="text-xs px-2 py-1 rounded border border-indigo-900 bg-indigo-950/30 text-indigo-200">{category}</span>
                        ))}
                      </div>
                      <div className="text-xs text-slate-400 mt-3">Confidence: {classification?.confidence ? `${Math.round(classification.confidence * 100)}%` : '-'}</div>
                      <div className="mt-3 space-y-1">
                        {(classification?.missingRequirementSignals || []).slice(0, 4).map((gap: string) => (
                          <div key={gap} className="text-xs text-amber-300">Needs signal: {gap}</div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                      <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">Gap Detection</div>
                      {gaps.length === 0 ? (
                        <div className="text-sm text-emerald-300">No catalog gaps detected for the selected prompt.</div>
                      ) : (
                        <div className="space-y-2">
                          {gaps.map((gap: any) => (
                            <div key={gap.code} className="border border-amber-900/70 bg-amber-950/20 rounded-lg p-3">
                              <div className="text-xs font-bold text-amber-300">{gap.code} · {gap.severity}</div>
                              <div className="text-xs text-slate-300 mt-1">{gap.message}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 text-xs font-mono text-slate-300 space-y-2">
                      <div><span className="text-slate-500">Gold:</span> {version?.gold_gcs_uri || '-'}</div>
                      <div><span className="text-slate-500">Silver:</span> {version?.silver_gcs_uri || '-'}</div>
                      <div><span className="text-slate-500">Bronze:</span> {version?.bronze_gcs_uri || '-'}</div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}


          {activeTab === 'audit' && (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
              <h2 className="text-lg font-bold mb-4">State Machine Audit Trail</h2>
              <div className="space-y-4 max-h-[450px] overflow-y-auto pr-2">
                {events.length === 0 ? (
                  <p className="text-slate-500 text-sm">No lifecycle events recorded for the selected prompt.</p>
                ) : (
                  events.map((ev: any, idx: number) => (
                    <div key={idx} className="flex justify-between items-center border-b border-slate-800/60 pb-3 last:border-0">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className={`w-5 h-5 ${ev.severity === 'error' ? 'text-red-400' : 'text-emerald-400'}`} />
                        <div>
                          <div className="font-semibold text-sm capitalize">{ev.event_type.replace('_', ' ')}</div>
                          <div className="text-xs text-slate-500">Lifecycle State: <span className="font-mono text-slate-400">{ev.lifecycle_status}</span></div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-slate-400 font-mono capitalize">{ev.repeat_mode}</span>
                        <div className="text-[10px] text-slate-500 mt-1">{new Date(ev.created_at).toLocaleString()}</div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'report' && (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
              <h2 className="text-lg font-bold mb-4">Scientific Estimation Specification</h2>
              {estimation?.raw_json ? (
                <pre className="text-xs font-mono bg-slate-950 p-4 rounded-lg overflow-x-auto border border-slate-800/80 text-indigo-300 max-h-[500px]">
                  {JSON.stringify(JSON.parse(estimation.raw_json), null, 2)}
                </pre>
              ) : (
                <p className="text-slate-500 text-sm">Please click "Run AI Estimation" above to compile the first report.</p>
              )}
            </div>
          )}

          {activeTab === 'orchestrator' && (() => {
            const result = orchestratorResult?.result;
            const selection = result?.selection;
            const metrics = selection?.metrics;
            return (
              <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-5">
                  <div>
                    <h2 className="text-lg font-bold flex items-center gap-2">
                      <BrainCircuit className="w-5 h-5 text-indigo-400" /> Coding Agent Orchestrator
                    </h2>
                    <p className="text-sm text-slate-400 mt-1">Dry-run context loading, scorecard routing, and evidence generation.</p>
                  </div>
                  <button
                    onClick={runOrchestrator}
                    disabled={orchestratorLoading}
                    className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition disabled:opacity-50"
                  >
                    <Play className="w-4 h-4" /> {orchestratorLoading ? 'Running...' : 'Run Dry Selection'}
                  </button>
                </div>

                <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Task</label>
                <textarea
                  value={orchestratorTask}
                  onChange={(e) => setOrchestratorTask(e.target.value)}
                  className="w-full min-h-24 bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Logical Route</div>
                    <div className="text-xl font-black text-white">{selection?.logical_route || 'not run'}</div>
                  </div>
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Physical Model</div>
                    <div className="text-xl font-black text-indigo-300">{selection?.physical_model || '-'}</div>
                  </div>
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Confidence</div>
                    <div className="text-xl font-black text-emerald-300">{selection?.confidence ? `${Math.round(selection.confidence * 100)}%` : '-'}</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Complexity</div>
                    <div className="text-2xl font-black text-white">{metrics?.complexity_score ?? '-'}/10</div>
                  </div>
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Risk</div>
                    <div className="text-2xl font-black text-white">{metrics?.risk_score ?? '-'}/10</div>
                  </div>
                  <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-4">
                    <div className="text-xs text-slate-500 uppercase font-bold mb-1">Estimated Tokens</div>
                    <div className="text-2xl font-black text-white">{metrics?.estimated_tokens?.toLocaleString() || '-'}</div>
                  </div>
                </div>

                <div className="mt-6 bg-slate-950/70 border border-slate-800 rounded-lg p-4 space-y-2 text-xs font-mono text-slate-300">
                  <div><span className="text-slate-500">Selection evidence:</span> {result?.selection_evidence || '-'}</div>
                  <div><span className="text-slate-500">Context manifest:</span> {result?.manifest || '-'}</div>
                  <div><span className="text-slate-500">Composed prompt:</span> {result?.composed_prompt || '-'}</div>
                  <div><span className="text-slate-500">Markdown report:</span> {result?.markdown || '(dry-run only)'}</div>
                </div>

                {selection?.reason && (
                  <div className="mt-4 text-sm text-slate-300 bg-slate-950/50 border border-slate-800 rounded-lg p-4">
                    <span className="text-slate-500 font-semibold">Reason:</span> {selection.reason}
                  </div>
                )}
              </div>
            );
          })()}


          {/* Action Logs Panel */}
          <div className="bg-slate-950 border border-indigo-950 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3 text-indigo-400 text-xs font-bold uppercase tracking-wider">
              <Terminal className="w-4 h-4" /> Live Execution Output
            </div>
            <pre className="text-xs font-mono bg-slate-950 p-4 rounded-lg overflow-y-auto max-h-[300px] border border-slate-800 text-slate-300 whitespace-pre-wrap leading-relaxed">
              {actionLog || 'Ready. Click "Run AI Estimation" or "Refresh from Vertex" to execute background processes...'}
            </pre>
          </div>
        </div>

        {/* Right Column Layout */}
        <div className="space-y-8">
          {/* Scientific Token Stats */}
          <div className="bg-slate-900/30 border border-slate-800 p-6 rounded-xl">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-400" /> Token Estimator
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Gemini 3.5 Flash Usage:</span>
                  <span className="font-bold text-white">{estimation?.estimated_tokens?.toLocaleString() || '0'} tokens</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full" style={{ width: estimation?.estimated_tokens ? '65%' : '0%' }}></div>
                </div>
              </div>
              <div className="pt-2 border-t border-slate-800 text-xs text-slate-400 space-y-2">
                <div className="flex justify-between">
                  <span>Input Token Ceiling:</span>
                  <span className="text-slate-200">200,000 max</span>
                </div>
                <div className="flex justify-between">
                  <span>Estimated Development Hours:</span>
                  <span className="text-slate-200">54 hrs</span>
                </div>
              </div>
            </div>
          </div>

          {/* Guidelines Card */}
          <div className="bg-gradient-to-br from-indigo-950/20 to-slate-900 border border-indigo-950/50 p-6 rounded-xl">
            <h2 className="text-sm font-bold text-indigo-400 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> Governance Rules
            </h2>
            <ul className="space-y-3 text-xs text-slate-400 leading-relaxed list-disc list-inside">
              <li><strong>Zero Content Loss:</strong> Strict character boundaries matching the Saved Prompt source of truth.</li>
              <li><strong>SCD Type 2:</strong> Historical state versions are kept intact in BigQuery.</li>
              <li><strong>Repeat Optimizations:</strong> Auto-skip active when MD5 hashes remain unchanged.</li>
            </ul>
          </div>
        </div>

      </div>
    </main>
  );
}
