'use client';
import React from 'react';
import { Chunk } from '@/lib/chunks';

interface Props { chunks: Chunk[]; mergedContent: string; }
export default function ExportButtons({ chunks, mergedContent }: Props) {
  const exportMarkdown = () => {
    const blob = new Blob([mergedContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'merged-spec.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPdf = () => {
    window.print();
  };

  return (
    <div className="flex gap-2">
      <button onClick={exportMarkdown} className="rounded bg-zinc-800 px-4 py-2 text-sm hover:bg-zinc-700">Export MD</button>
      <button onClick={exportPdf} className="rounded bg-zinc-800 px-4 py-2 text-sm hover:bg-zinc-700">Print / PDF</button>
    </div>
  );
}