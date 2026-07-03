'use client';
import React, { useState, useMemo } from 'react';
import Fuse from 'fuse.js';
import { Chunk } from '@/lib/chunks';
import SearchBar from './SearchBar';
import TableOfContents from './TableOfContents';
import MarkdownRenderer from './MarkdownRenderer';
import ExportButtons from './ExportButtons';

interface Props { initialChunks: Chunk[]; }

export default function SpecViewer({ initialChunks }: Props) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeChunk, setActiveChunk] = useState<string | null>(null);

  const fuse = useMemo(() => new Fuse(initialChunks, {
    keys: ['title', 'content'],
    threshold: 0.3,
    includeScore: true,
  }), [initialChunks]);

  const filteredChunks = useMemo(() => {
    if (!searchTerm) return initialChunks;
    return fuse.search(searchTerm).map(r => r.item);
  }, [searchTerm, fuse, initialChunks]);

  const mergedContent = useMemo(() => {
    return filteredChunks.map(c => c.content).join('\n\n---\n\n');
  }, [filteredChunks]);

  const mergedHtml = useMemo(() => {
    return filteredChunks.map(c => c.html).join('<hr class="my-8 border-zinc-800" />');
  }, [filteredChunks]);

  const allHeadings = useMemo(() => {
    return filteredChunks.flatMap(c => c.headings.map(h => ({ ...h, chunkSlug: c.slug })));
  }, [filteredChunks]);

  return (
    <div className="flex h-screen flex-col">
      <header className="border-b border-zinc-800 p-4 flex items-center justify-between bg-zinc-950">
        <h1 className="text-2xl font-semibold">Spec Documentation Viewer</h1>
        <ExportButtons chunks={filteredChunks} mergedContent={mergedContent} />
      </header>
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 border-r border-zinc-800 p-4 overflow-y-auto">
          <SearchBar value={searchTerm} onChange={setSearchTerm} />
          <TableOfContents headings={allHeadings} onSelect={(slug) => setActiveChunk(slug)} />
        </aside>
        <main className="flex-1 overflow-y-auto p-8">
          <MarkdownRenderer html={mergedHtml} activeChunk={activeChunk} />
        </main>
      </div>
    </div>
  );
}