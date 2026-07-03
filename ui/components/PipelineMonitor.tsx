import React from 'react';
import { Cpu, FileCode2, ShieldAlert, CheckCircle, PackageOpen, HelpCircle, Activity } from 'lucide-react';

interface StageProps {
  id: number;
  label: string;
  agent: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  description: string;
  icon: React.ComponentType<any>;
}

interface PipelineMonitorProps {
  currentStage: number;
  stagesStatus: Record<string, 'pending' | 'running' | 'success' | 'failed'>;
}

export default function PipelineMonitor({ currentStage, stagesStatus }: PipelineMonitorProps) {
  const stages: StageProps[] = [
    {
      id: 1,
      label: 'Tech Stack Discovery',
      agent: 'Agent 1: Discovery',
      status: stagesStatus['discovery'] || 'pending',
      description: 'Dynamically analyzes the specification to discover the best languages, frameworks, and core project structures.',
      icon: Cpu,
    },
    {
      id: 2,
      label: 'System Design',
      agent: 'Agent 2: Architect',
      status: stagesStatus['design'] || 'pending',
      description: 'Generates detailed architecture documents, ASCII component diagrams, boundaries, and schema schemas.',
      icon: FileCode2,
    },
    {
      id: 3,
      label: 'Security & QA Audit',
      agent: 'Agent 3: DevSecOps',
      status: stagesStatus['audit'] || 'pending',
      description: 'Inspects architectural artifacts for critical vulnerabilities, standards, and issues a compliance report.',
      icon: ShieldAlert,
    },
    {
      id: 4,
      label: 'Polyglot Compiler',
      agent: 'Agent 4: Compiler',
      status: stagesStatus['compile'] || 'pending',
      description: 'Compiles the full design spec, and generates complete, production-ready, multi-file codebase layout.',
      icon: Activity,
    },
    {
      id: 5,
      label: 'Release Manager',
      agent: 'Agent 5: Release',
      status: stagesStatus['release'] || 'pending',
      description: 'Packages all code layers into an optimized zip file, generating auditable artifact mappings for GCS storage.',
      icon: PackageOpen,
    },
  ];

  return (
    <div className="bg-gray-100 border border-gray-200 rounded-xl p-6">
      <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        Cooperative 5-Agent Pipeline Progression
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          
          // Color coding based on status
          let statusColor = 'border-gray-200 bg-white text-zinc-500';
          let badgeColor = 'bg-gray-200 text-zinc-400';
          let statusLabel = 'Idle';

          if (stage.status === 'running') {
            statusColor = 'border-blue-300 bg-blue-50 text-blue-800 shadow-[0_0_15px_rgba(59,130,246,0.1)]';
            badgeColor = 'bg-blue-100 text-blue-700 animate-pulse';
            statusLabel = 'Running';
          } else if (stage.status === 'success') {
            statusColor = 'border-emerald-300 bg-emerald-50 text-emerald-800';
            badgeColor = 'bg-emerald-100 text-emerald-700';
            statusLabel = 'Completed';
          } else if (stage.status === 'failed') {
            statusColor = 'border-red-300 bg-red-50 text-red-800';
            badgeColor = 'bg-red-100 text-red-700';
            statusLabel = 'Failed';
          }

          return (
            <div
              key={stage.id}
              className={`border rounded-lg p-5 flex flex-col justify-between transition-all duration-300 ${statusColor}`}
            >
              <div>
                <div className="flex justify-between items-start mb-3">
                  <div className="p-2 rounded-md bg-gray-100 border border-gray-200">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${badgeColor}`}>
                    {statusLabel}
                  </span>
                </div>
                <h3 className="font-semibold text-gray-800 text-sm mb-1">{stage.label}</h3>
                <p className="text-[11px] text-gray-500 font-mono mb-3">{stage.agent}</p>
                <p className="text-xs text-gray-600 leading-relaxed">{stage.description}</p>
              </div>

              {idx < 4 && (
                <div className="hidden md:block absolute top-1/2 -translate-y-1/2 right-[calc(100%/5*idx)] pointer-events-none">
                  {/* arrow marker */}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
