import React from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert, FileText, Bookmark, PieChart, Activity } from 'lucide-react';

interface Candidate {
  requirement_category: string;
  line_text: string;
}

interface Trace {
  requirement_id: string;
  requirement_text: string;
  implementation_file: string | null;
  status: string;
  gap_text: string | null;
  risk_level: string;
}

interface TraceabilityMatrixProps {
  candidates: Candidate[];
  traces: Trace[];
  isLoading: boolean;
}

export default function TraceabilityMatrix({ candidates, traces, isLoading }: TraceabilityMatrixProps) {
  // Compute category distribution statistics dynamically
  const stats = React.useMemo(() => {
    const counts: Record<string, number> = {
      Functional: 0,
      Infrastructure: 0,
      Security: 0,
      Orchestration: 0,
      Data: 0,
    };
    let total = 0;
    candidates.forEach((cand) => {
      const cat = cand.requirement_category || 'Functional';
      if (counts[cat] !== undefined) {
        counts[cat]++;
        total++;
      }
    });
    return { counts, total };
  }, [candidates]);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-6 border-b border-zinc-800/80 pb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Bookmark className="w-5 h-5 text-indigo-400" />
          Enterprise Requirement Traceability Matrix (BigQuery-Mapped)
        </h2>
        <span className="text-[11px] font-mono text-zinc-500">Source: ctoteam.prism_sentinel_audit</span>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-zinc-400 font-mono text-sm">
          <span className="inline-block animate-spin mr-2">⏳</span> Loading requirements and traceability indices from BigQuery...
        </div>
      ) : (
        <div className="space-y-6">
          {/* Visual Category Distribution Ratios */}
          <div className="bg-zinc-950 border border-zinc-800/60 rounded-lg p-5">
            <h3 className="text-xs font-semibold text-zinc-400 font-mono uppercase mb-4 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-zinc-400" />
              BigQuery Extracted Requirement Category Distribution
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.keys(stats.counts).map((category) => {
                const count = stats.counts[category];
                const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;

                // Color mappings based on category type
                let barColor = 'bg-zinc-700';
                let textColor = 'text-zinc-400';

                if (category === 'Functional') {
                  barColor = 'bg-indigo-500';
                  textColor = 'text-indigo-400';
                } else if (category === 'Infrastructure') {
                  barColor = 'bg-teal-500';
                  textColor = 'text-teal-400';
                } else if (category === 'Security') {
                  barColor = 'bg-red-500';
                  textColor = 'text-red-400';
                } else if (category === 'Orchestration') {
                  barColor = 'bg-amber-500';
                  textColor = 'text-amber-400';
                } else if (category === 'Data') {
                  barColor = 'bg-sky-500';
                  textColor = 'text-sky-400';
                }

                return (
                  <div key={category} className="space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-zinc-300 font-medium">{category}</span>
                      <span className={`font-mono font-semibold ${textColor}`}>{count} ({percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden border border-zinc-800/40">
                      <div className={`h-full rounded-full ${barColor}`} style={{ width: `${percentage}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Grid Panel for Candidates and Traces */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Candidates */}
            <div className="border border-zinc-800 rounded-lg bg-zinc-950 p-4">
              <h3 className="text-sm font-semibold text-zinc-300 mb-4 flex items-center gap-2">
                <FileText className="w-4 h-4 text-zinc-400" />
                BigQuery Extracted Requirement Candidates
              </h3>
              
              <div className="max-h-[350px] overflow-y-auto space-y-2 pr-1">
                {candidates.length === 0 ? (
                  <div className="text-xs text-zinc-500 py-4 text-center">No requirement candidates found.</div>
                ) : (
                  candidates.map((cand, idx) => (
                    <div key={idx} className="p-3 rounded bg-zinc-900 border border-zinc-800 text-xs flex gap-2 items-start">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-mono shrink-0 ${
                        cand.requirement_category === 'Functional' ? 'bg-indigo-950/40 text-indigo-400 border border-indigo-900/30' :
                        cand.requirement_category === 'Security' ? 'bg-red-950/40 text-red-400 border border-red-900/30' :
                        cand.requirement_category === 'Infrastructure' ? 'bg-teal-950/40 text-teal-400 border border-teal-900/30' :
                        cand.requirement_category === 'Orchestration' ? 'bg-amber-950/40 text-amber-400 border border-amber-900/30' :
                        'bg-sky-950/40 text-sky-400 border border-sky-900/30'
                      }`}>
                        {cand.requirement_category}
                      </span>
                      <p className="text-zinc-300 leading-relaxed">{cand.line_text}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Traces */}
            <div className="border border-zinc-800 rounded-lg bg-zinc-950 p-4">
              <h3 className="text-sm font-semibold text-zinc-300 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Active Traceability Mapping (Compliance Auditing)
              </h3>

              <div className="max-h-[350px] overflow-y-auto space-y-2 pr-1">
                {traces.length === 0 ? (
                  <div className="text-xs text-zinc-500 py-4 text-center">No traceability mappings loaded.</div>
                ) : (
                  traces.map((trace, idx) => (
                    <div key={idx} className="p-3 rounded bg-zinc-900 border border-zinc-800 text-xs">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-mono text-[10px] text-zinc-400 font-semibold">{trace.requirement_id}</span>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-mono shrink-0 font-semibold ${
                          trace.status === 'Implemented' ? 'bg-emerald-950/40 text-emerald-400' : 'bg-red-950/40 text-red-400'
                        }`}>
                          {trace.status}
                        </span>
                      </div>
                      <p className="text-zinc-300 leading-relaxed mb-2 font-mono text-[11px]">{trace.requirement_text}</p>
                      <div className="flex justify-between items-center text-[10px] text-zinc-500 font-mono mt-2 pt-2 border-t border-zinc-800/60">
                        <span>File: {trace.implementation_file || 'None'}</span>
                        <span className={`uppercase text-[9px] ${
                          trace.risk_level === 'high' ? 'text-red-400' : 'text-zinc-500'
                        }`}>Risk: {trace.risk_level}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
