import React, { useEffect, useState, useCallback } from 'react';
import { FolderOpen, Download, RefreshCw, FileArchive, FileText, CheckCircle2 } from 'lucide-react';

interface GcsFile {
  name: string;
  size: string | number;
  updated: string;
  contentType: string;
}

interface GcsExplorerProps {
  promptId: string;
}

export default function GcsExplorer({ promptId }: GcsExplorerProps) {
  const [files, setFiles] = useState<GcsFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadGcsFiles = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/gcs-files?promptId=${promptId}`);
      const data = await res.json();
      if (data.status === 'success') {
        setFiles(data.files || []);
      }
    } catch (err) {
      console.error('Failed to query GCS file catalog:', err);
    } finally {
      setIsLoading(false);
    }
  }, [promptId]);

  useEffect(() => {
    loadGcsFiles();
  }, [loadGcsFiles, promptId]);

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-6 border-b border-zinc-800 pb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <FolderOpen className="w-5 h-5 text-amber-400" />
          Google Cloud Storage Release Artifacts Explorer
        </h2>
        <button
          onClick={loadGcsFiles}
          className="p-1.5 rounded hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-zinc-200"
          title="Refresh Bucket"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading ? (
        <div className="py-8 text-center text-zinc-400 font-mono text-sm">
          ⏳ Listing blobs in gs://agentproject/prompts/{promptId}/...
        </div>
      ) : files.length === 0 ? (
        <div className="py-8 text-center text-zinc-500 text-xs">
          No GCS release artifacts found. Execute the pipeline to build and upload artifacts.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-zinc-800/80 text-zinc-500 font-mono uppercase">
                <th className="py-3 px-4">Artifact File Path</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Size</th>
                <th className="py-3 px-4">Last Updated</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file, idx) => {
                const isZip = file.name.endsWith('.zip');
                const isMd = file.name.endsWith('.md');
                const Icon = isZip ? FileArchive : FileText;

                // Format Size
                const sizeKb = (Number(file.size) / 1024).toFixed(1);
                
                // Format Date
                const dateStr = new Date(file.updated).toLocaleString();

                return (
                  <tr key={idx} className="border-b border-zinc-800/40 hover:bg-zinc-950/40 transition-colors">
                    <td className="py-3 px-4 font-mono text-zinc-300 flex items-center gap-2">
                      <Icon className={`w-4 h-4 shrink-0 ${isZip ? 'text-sky-400' : 'text-zinc-400'}`} />
                      <span className="truncate max-w-[350px] lg:max-w-[450px]" title={file.name}>
                        {file.name}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {isZip ? 'Package ZIP' : isMd ? 'Markdown Doc' : 'Data File'}
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono">
                      {sizeKb} KB
                    </td>
                    <td className="py-3 px-4 text-zinc-500 font-mono">
                      {dateStr}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <a
                        href={`/api/gcs-files?downloadPath=${encodeURIComponent(file.name)}`}
                        download
                        className="inline-flex items-center gap-1 bg-zinc-800 border border-zinc-700 hover:bg-zinc-700 text-zinc-200 hover:text-white px-2.5 py-1 rounded transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        Download
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
