'use client';

import React, { useState, useEffect, useCallback } from 'react';
import PipelineMonitor from '../components/PipelineMonitor';
import TraceabilityMatrix from '../components/TraceabilityMatrix';
import LogConsole from '../components/LogConsole';
import GcsExplorer from '../components/GcsExplorer';
import { Play, RotateCw, Activity, Terminal, CloudLightning, Award } from 'lucide-react';

export default function PipelineDashboard() {
  const [promptId, setPromptId] = useState('3381323161097207808');
  const [availablePromptIds, setAvailablePromptIds] = useState<string[]>(['3381323161097207808']);
  const [isPromptsLoading, setIsPromptsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  const [candidates, setCandidates] = useState([]);
  const [traces, setTraces] = useState([]);
  const [isBqLoading, setIsBqLoading] = useState(true);

  const [currentStage, setCurrentStage] = useState(0);
  const [stagesStatus, setStagesStatus] = useState<Record<string, 'pending' | 'running' | 'success' | 'failed'>>({
    discovery: 'pending',
    design: 'pending',
    audit: 'pending',
    compile: 'pending',
    release: 'pending',
  });

  // Fetch list of distinct prompt IDs from BigQuery
  useEffect(() => {
    async function loadPrompts() {
      try {
        const res = await fetch('/api/prompts');
        const data = await res.json();
        if (data.status === 'success' && data.promptIds && data.promptIds.length > 0) {
          setAvailablePromptIds(data.promptIds);
          setPromptId(data.promptIds[0]);
        }
      } catch (err) {
        console.error('Failed to load available prompt IDs:', err);
      } finally {
        setIsPromptsLoading(false);
      }
    }
    loadPrompts();
  }, []);

  // Fetch requirement mapping from BigQuery
  const loadBigQueryMapping = useCallback(async (id: string) => {
    setIsBqLoading(true);
    try {
      const res = await fetch(`/api/trace-mapping?promptId=${id}`);
      const data = await res.json();
      if (data.status === 'success') {
        setCandidates(data.candidates || []);
        setTraces(data.traces || []);
      }
    } catch (err) {
      console.error('Failed to load BQ requirements:', err);
    } finally {
      setIsBqLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadBigQueryMapping(promptId);
  }, [loadBigQueryMapping, promptId]);

  // Execute the 5-Agent parallel pipeline via streaming endpoint
  const executePipeline = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setLogs([]);
    setCurrentStage(1);
    setStagesStatus({
      discovery: 'running',
      design: 'pending',
      audit: 'pending',
      compile: 'pending',
      release: 'pending',
    });

    try {
      const response = await fetch(`/api/pipeline-run?promptId=${promptId}`);
      if (!response.body) throw new Error('ReadableStream not supported by browser.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        const lines = buffer.split('\n');
        // Keep the last partial line in buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          setLogs(prev => [...prev, line]);

          // Dynamically parsing logs to update pipeline visual steps
          if (line.includes('[AGENT 1]')) {
            setStagesStatus(prev => ({ ...prev, discovery: 'running' }));
          } else if (line.includes('[AGENT 2]')) {
            setStagesStatus(prev => ({ ...prev, discovery: 'success', design: 'running' }));
          } else if (line.includes('[AGENT 3]')) {
            setStagesStatus(prev => ({ ...prev, design: 'success', audit: 'running' }));
          } else if (line.includes('[AGENT 4]')) {
            setStagesStatus(prev => ({ ...prev, audit: 'success', compile: 'running' }));
          } else if (line.includes('[AGENT 5]')) {
            setStagesStatus(prev => ({ ...prev, compile: 'success', release: 'running' }));
          } else if (line.includes('Pipeline Complete') || line.includes('Finished') || line.includes('ZIP')) {
            setStagesStatus(prev => ({
              discovery: 'success',
              design: 'success',
              audit: 'success',
              compile: 'success',
              release: 'success',
            }));
          } else if (line.includes('failed') || line.includes('FAILED') || line.includes('Failure')) {
            // Find active running and set to failed
            setStagesStatus(prev => {
              const updated = { ...prev };
              if (updated.release === 'running') updated.release = 'failed';
              else if (updated.compile === 'running') updated.compile = 'failed';
              else if (updated.audit === 'running') updated.audit = 'failed';
              else if (updated.design === 'running') updated.design = 'failed';
              else if (updated.discovery === 'running') updated.discovery = 'failed';
              return updated;
            });
          }
        }
      }
    } catch (err: any) {
      setLogs(prev => [...prev, `[STDERR] Failed to execute pipeline: ${err.message}`]);
    } finally {
      setIsRunning(false);
      // Reload mappings after completion to pull newly committed traces
      loadBigQueryMapping(promptId);
    }
  };

  return (
    <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header Panel */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-200 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="bg-indigo-100 text-indigo-700 border border-indigo-200/60 text-xs px-2.5 py-0.5 rounded-full font-semibold flex items-center gap-1">
              <CloudLightning className="w-3.5 h-3.5" />
              GCP Serverless Architecture
            </span>
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-zinc-900 to-zinc-600 bg-clip-text text-transparent">
            PRISM 5-Agent Cooperative Coding orchestrator
          </h1>
          <p className="text-xs text-gray-500">
            Automating multi-step Tech Discovery, System Design, Security Audit, Polyglot Compilation, and GCS Release Management.
          </p>
        </div>

        {/* Input & Execution Wrapper */}
        <div className="flex items-center gap-3 bg-gray-50 border border-gray-200/80 rounded-xl p-3 shadow-sm shrink-0">
          <div className="space-y-1">
            <label className="text-[10px] font-semibold text-gray-500 font-mono uppercase block">Prompt Spec ID</label>
            {isPromptsLoading ? (
              <div className="bg-gray-100 border border-gray-200 rounded px-3 py-1.5 text-xs text-gray-500 font-mono w-[200px]">
                Loading IDs...
              </div>
            ) : (
              <select
                value={promptId}
                onChange={(e) => setPromptId(e.target.value)}
                className="bg-white border border-gray-300 rounded px-3 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-indigo-500 w-[200px] font-mono cursor-pointer"
              >
                {availablePromptIds.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="flex flex-col gap-1">
            <span className="h-4"></span>
            <button
              onClick={executePipeline}
              disabled={isRunning}
              className={`px-4 py-2 rounded text-xs font-semibold flex items-center gap-1.5 transition-all ${
                isRunning
                  ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-[0_4px_12px_rgba(16,185,129,0.2)]'
              }`}
            >
              {isRunning ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  Execute Pipeline
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Pipeline Progression Monitor */}
      <section>
        <PipelineMonitor currentStage={currentStage} stagesStatus={stagesStatus} />
      </section>

      {/* Middle Grid: Console Logs & BQ Traces */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <LogConsole logs={logs} />
        </div>
        <div>
          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-6 h-full flex flex-col justify-between">
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
                <Award className="w-4.5 h-4.5 text-amber-500" />
                Audit Trail and GCP Release Spec
              </h2>
              <p className="text-xs text-gray-600 leading-relaxed">
                Upon pipeline completion, all compiled code, design files, DevSecOps audit metrics, and requirement tracing schemas are fully archived in **Google Cloud Storage**.
              </p>
              
              <div className="space-y-2 border-t border-gray-200/60 pt-4 text-xs font-mono">
                <div className="flex justify-between">
                  <span className="text-gray-500">Destination Bucket:</span>
                  <span className="text-gray-800 font-medium">agentproject</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Telemetry Engine:</span>
                  <span className="text-gray-800 font-medium">BigQuery Storage</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">GCP Location:</span>
                  <span className="text-gray-800 font-medium">us-central1</span>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200/60 text-xs text-gray-500 leading-relaxed">
              *Full logs, trace details, and packages can be loaded by clicking &quot;Execute Pipeline&quot;. Output streams live through Next.js server-side process forks.*
            </div>
          </div>
        </div>
      </section>

      {/* GCS Artifact Explorer */}
      <section>
        <GcsExplorer promptId={promptId} />
      </section>

      {/* Bottom Panel: Traceability Matrices */}
      <section>
        <TraceabilityMatrix candidates={candidates} traces={traces} isLoading={isBqLoading} />
      </section>
    </main>
  );
}
