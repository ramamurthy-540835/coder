'use client';

import React, { useState, useEffect, useMemo, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

// Strict TypeScript Types
interface Chunk {
  id: string;
  title: string;
  content: string;
  order: number;
  rawContent: string;
}

interface PromptPackage {
  promptId: string;
  project: string;
  region: string;
  masterMd: string;
  chunks: Chunk[];
  rawJson: Record<string, unknown>;
}

interface DiagnosticLog {
  timestamp: string;
  level: 'info' | 'warn' | 'error';
  message: string;
  metadata?: Record<string, unknown>;
}

interface ExecutionPlan {
  steps: string[];
  status: 'pending' | 'running' | 'completed';
}

interface ReasoningSummary {
  summary: string;
  deterministic: boolean;
}

// Strict React Error Boundary
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.props.onError?.(error);
    console.error('PRISM Diagnostic:', { error: error.message, stack: errorInfo.componentStack });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 bg-red-50 border border-red-200 rounded-lg">
          <h2 className="text-xl font-bold text-red-700">PRISM Agent Error Boundary</h2>
          <p className="mt-2 text-red-600">An unexpected error occurred. Check diagnostic logs.</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Custom Diagnostic Logging Hook with structured audit trail
function useDiagnosticLogger() {
  const [logs, setLogs] = useState<DiagnosticLog[]>([]);

  const logDiagnostic = useCallback((level: DiagnosticLog['level'], message: string, metadata?: Record<string, unknown>) => {
    const entry: DiagnosticLog = {
      timestamp: new Date().toISOString(),
      level,
      message,
      metadata: { ...metadata, project: 'ctoteam', region: 'us-central1' },
    };
    setLogs(prev => [...prev, entry]);
    console.log(`[PRISM-${level.toUpperCase()}]`, entry);
    // Production: send to Cloud Logging
  }, []);

  return { logs, logDiagnostic };
}

// Optimized Fuzzy Search (Fuse.js ready - replace with real Fuse for production)
function fuzzySearch(chunks: Chunk[], query: string): Chunk[] {
  if (!query.trim()) return [...chunks];
  const lowerQuery = query.toLowerCase();
  return chunks
    .map(chunk => {
      const titleMatch = chunk.title.toLowerCase().includes(lowerQuery) ? 0.6 : 0;
      const contentMatch = chunk.content.toLowerCase().includes(lowerQuery) ? 0.4 : 0;
      const score = titleMatch + contentMatch;
      return { chunk, score };
    })
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(item => item.chunk);
}

// Fully realized mock export handlers (MD & PDF)
function exportToMarkdown(packageData: PromptPackage, log: (msg: string) => void) {
  const mdContent = `# Prompt Package ${packageData.promptId}

## Master.md
${packageData.masterMd}

## Chunks
${packageData.chunks
    .sort((a, b) => a.order - b.order)
    .map(c => `### ${c.title}
${c.content}

Raw: ${c.rawContent}`)
    .join('\n\n')}`;
  const blob = new Blob([mdContent], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `prompt-${packageData.promptId}.md`;
  a.click();
  URL.revokeObjectURL(url);
  log(`Exported MD for prompt ${packageData.promptId}`);
}

function exportToPdf(packageData: PromptPackage, log: (msg: string) => void) {
  // Production: import jsPDF from 'jspdf' and render real PDF
  const pdfContent = `PRISM Prompt Package\nID: ${packageData.promptId}\nProject: ${packageData.project}\nRegion: ${packageData.region}\nChunks: ${packageData.chunks.length}\n\n${packageData.masterMd}`;
  const blob = new Blob([pdfContent], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `prompt-${packageData.promptId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
  log(`Exported PDF for prompt ${packageData.promptId}`);
}

// Main Page Component
function PRISMPromptViewerContent() {
  const searchParams = useSearchParams();
  const promptId = searchParams.get('promptId') || '3381323161097207808';
  const { logs, logDiagnostic } = useDiagnosticLogger();

  const [promptPackage, setPromptPackage] = useState<PromptPackage | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeChunkId, setActiveChunkId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [executionPlan, setExecutionPlan] = useState<ExecutionPlan>({ steps: ['Accept prompt ID', 'Create master.md', 'Strip binaries', 'Generate chunk_001.md'], status: 'pending' });
  const [reasoningSummary, setReasoningSummary] = useState<ReasoningSummary>({ summary: 'Deterministic mock package built from saved_prompts/3381323161097207808. No AI rewrite of source.', deterministic: true });

  // Config-driven architecture (ctoteam, us-central1, Gemini 2.5 Flash)
  const PROMPT_CONFIG = {
    project: 'ctoteam',
    region: 'us-central1',
    defaultModel: 'Gemini 2.5 Flash',
    fallbackRegion: 'us-central1',
  } as const;

  // Build Prompt Package - concise execution summary, no /gcloud_run, preserves order & source
  const buildPromptPackage = useCallback((id: string): PromptPackage => {
    const mockChunks: Chunk[] = [
      {
        id: 'chunk_001',
        title: 'Master Prompt - Build Prompt Package',
        content: 'Accept prompt ID as argument. Create saved_prompts/<prompt_id>/master.md. Preserve ordering of source content. Strip binary/image/pdf payloads into placeholders. Use Gemini 2.5 Flash (us-central1 fallback).',
        order: 1,
        rawContent: 'raw source for chunk_001.md from saved_prompts/3381323161097207808',
      },
    ];

    const masterMd = mockChunks.map(c => c.content).join('\n\n');
    const rawJson = { promptId: id, created: new Date().toISOString(), chunks: 1, source: 'saved_prompts/' + id + '/raw.json' };

    return {
      promptId: id,
      project: PROMPT_CONFIG.project,
      region: PROMPT_CONFIG.region,
      masterMd,
      chunks: mockChunks,
      rawJson,
    };
  }, []);

  // Initialize with execution summary + plan
  useEffect(() => {
    logDiagnostic('info', 'PRISM Agent initialized', { promptId, execution: 'concise_summary' });
    const pkg = buildPromptPackage(promptId);
    setPromptPackage(pkg);
    setExecutionPlan(prev => ({ ...prev, status: 'completed' }));
    setIsLoading(false);
    logDiagnostic('info', 'Prompt package built', { chunks: pkg.chunks.length, source: 'saved_prompts/' + promptId });
  }, [promptId, buildPromptPackage, logDiagnostic]);

  // Optimized Fuzzy Search
  const filteredChunks = useMemo(() => {
    if (!promptPackage) return [];
    return fuzzySearch(promptPackage.chunks, searchQuery);
  }, [promptPackage, searchQuery]);

  // Table of Contents scrolling
  const scrollToChunk = (chunkId: string) => {
    const element = document.getElementById(chunkId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveChunkId(chunkId);
      logDiagnostic('info', 'TOC navigation', { chunkId });
    }
  };

  // Mock script execution (run_prompt_id.sh + start_aider.sh)
  const runPromptIdScript = () => {
    logDiagnostic('info', 'Executing ./scripts/run_prompt_id.sh', { promptId });
    setExecutionPlan({ steps: ['Launch Aider', 'Generate master.md', 'Create chunk_001.md'], status: 'running' });
    alert(`Simulated: ./scripts/run_prompt_id.sh ${promptId} (Aider launched via start_aider.sh)`);
    setTimeout(() => setExecutionPlan(prev => ({ ...prev, status: 'completed' })), 800);
  };

  // Export actions
  const handleExport = (format: 'md' | 'pdf') => {
    if (!promptPackage) return;
    if (format === 'md') {
      exportToMarkdown(promptPackage, (msg) => logDiagnostic('info', msg));
    } else {
      exportToPdf(promptPackage, (msg) => logDiagnostic('info', msg));
    }
  };

  if (isLoading || !promptPackage) {
    return <div className="p-8">Loading PRISM Prompt Package...</div>;
  }

  return (
    <ErrorBoundary onError={(e) => logDiagnostic('error', 'Boundary caught error', { error: e.message })}>
      <div className="min-h-screen bg-gray-50 p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold">PRISM Coder Agent - Prompt Viewer</h1>
          <p className="text-gray-600">Project: {promptPackage.project} | ID: {promptPackage.promptId} | Region: {promptPackage.region}</p>
          <div className="mt-4 flex gap-3">
            <button onClick={runPromptIdScript} className="px-4 py-2 bg-blue-600 text-white rounded">Run Prompt ID Script</button>
            <button onClick={() => handleExport('md')} className="px-4 py-2 bg-green-600 text-white rounded">Export MD</button>
            <button onClick={() => handleExport('pdf')} className="px-4 py-2 bg-purple-600 text-white rounded">Export PDF</button>
          </div>
        </header>

        {/* Execution Plan & Reasoning Summary */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded shadow">
            <h2 className="font-semibold mb-2">Execution Plan</h2>
            <div className="text-sm">Status: {executionPlan.status}</div>
            <ul className="mt-2 text-sm list-disc pl-5">
              {executionPlan.steps.map((step, i) => <li key={i}>{step}</li>)}
            </ul>
          </div>
          <div className="p-4 bg-white rounded shadow">
            <h2 className="font-semibold mb-2">Reasoning Summary</h2>
            <p className="text-sm">{reasoningSummary.summary}</p>
            <div className="text-xs mt-1 text-gray-500">Deterministic: {reasoningSummary.deterministic ? 'Yes' : 'No'}</div>
          </div>
        </div>

        {/* TOC */}
        <nav className="mb-6 p-4 bg-white rounded shadow">
          <h2 className="font-semibold mb-2">Table of Contents</h2>
          <ul>
            {promptPackage.chunks.map((chunk) => (
              <li key={chunk.id}>
                <button
                  onClick={() => scrollToChunk(chunk.id)}
                  className={`text-left hover:underline ${activeChunkId === chunk.id ? 'font-bold text-blue-600' : ''}`}
                >
                  {chunk.title}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Fuzzy Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Fuzzy search chunks (Fuse.js ready)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full p-3 border rounded"
          />
        </div>

        {/* Chunks Display (preserve order) */}
        <div className="space-y-6">
          {filteredChunks.map((chunk) => (
            <div key={chunk.id} id={chunk.id} className="bg-white p-6 rounded shadow">
              <h3 className="text-xl font-semibold mb-2">{chunk.title}</h3>
              <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-4 rounded">{chunk.content}</pre>
              <div className="mt-2 text-xs text-gray-500">Raw source preserved: {chunk.rawContent}</div>
            </div>
          ))}
        </div>

        {/* Diagnostic Logs */}
        <div className="mt-8 p-4 bg-gray-900 text-green-400 font-mono text-xs rounded">
          <h3 className="text-white mb-2">Structured Diagnostic Logs (Audit Trail)</h3>
          {logs.slice(-6).map((log, idx) => (
            <div key={idx}>[{log.timestamp}] {log.level}: {log.message} {log.metadata ? JSON.stringify(log.metadata) : ''}</div>
          ))}
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default function PRISMPromptViewer() {
  return (
    <Suspense fallback={<div className="p-8 text-zinc-400 text-center font-mono">Initializing PRISM Viewer...</div>}>
      <PRISMPromptViewerContent />
    </Suspense>
  );
}