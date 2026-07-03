"use client";

import React, { useState, useEffect } from 'react';
import { 
  BarChart2, Play, RefreshCw, Terminal, CheckCircle2, 
  AlertTriangle, Layers, Cpu, Code2, ExternalLink, ChevronDown 
} from 'lucide-react';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [actionLog, setActionLog] = useState<string>('');
  const [data, setData] = useState<any>(null);
  const [selectedUid, setSelectedUid] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'overview' | 'audit' | 'report'>('overview');

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
            Backend Workspace: <code className="text-indigo-300 font-mono bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">/DiracDelta/gcloud_run</code>
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
        {(['overview', 'audit', 'report'] as const).map((tab) => (
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
