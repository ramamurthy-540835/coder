'use client';
import React from 'react';

interface Heading { level: number; text: string; id: string; chunkSlug: string; }
interface Props { headings: Heading[]; onSelect: (slug: string) => void; }
export default function TableOfContents({ headings, onSelect }: Props) {
  return (
    <div className="mt-6">
      <div className="mb-2 text-xs uppercase tracking-widest text-zinc-500">Table of Contents</div>
      <nav className="space-y-1 text-sm">
        {headings.map((h, i) => (
          <a
            key={i}
            href={`#${h.id}`}
            onClick={() => onSelect(h.chunkSlug)}
            className="block text-zinc-400 hover:text-zinc-100 transition-colors"
            style={{ paddingLeft: `${(h.level - 1) * 12}px` }}
          >
            {h.text}
          </a>
        ))}
      </nav>
    </div>
  );
}