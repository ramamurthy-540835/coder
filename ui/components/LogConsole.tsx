import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface LogConsoleProps {
  logs: string[];
}

export default function LogConsole({ logs }: LogConsoleProps) {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Automatically scroll console down when logs arrive
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
      <div className="bg-zinc-900 px-4 py-3 border-b border-zinc-800/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-semibold font-mono text-zinc-300">Live Orchestrator Output Console</span>
        </div>
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500/80"></span>
          <span className="w-3 h-3 rounded-full bg-yellow-500/80"></span>
          <span className="w-3 h-3 rounded-full bg-green-500/80"></span>
        </div>
      </div>

      <div className="p-4 font-mono text-xs text-zinc-300 leading-relaxed overflow-y-auto max-h-[350px] min-h-[200px] space-y-1 bg-black/60 scrollbar-thin">
        {logs.length === 0 ? (
          <div className="text-zinc-500 animate-pulse py-4">
            System idle. Click &quot;Execute Pipeline&quot; to begin 5-Agent parallel compilation.
          </div>
        ) : (
          logs.map((log, index) => {
            let textColor = 'text-zinc-300';
            if (log.includes('[STDERR]')) {
              textColor = 'text-amber-400/90';
            } else if (log.includes('🎉') || log.includes('SUCCESS') || log.includes('Complete')) {
              textColor = 'text-emerald-400 font-semibold';
            } else if (log.includes('🚀') || log.includes('Starting')) {
              textColor = 'text-sky-400 font-semibold';
            } else if (log.includes('❌') || log.includes('FAILED') || log.includes('failed')) {
              textColor = 'text-red-400 font-semibold';
            }

            return (
              <div key={index} className={`whitespace-pre-wrap break-all ${textColor}`}>
                {log}
              </div>
            );
          })
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
