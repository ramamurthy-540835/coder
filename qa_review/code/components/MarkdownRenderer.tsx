'use client';
import React from 'react';

interface Props { html: string; activeChunk: string | null; }
export default function MarkdownRenderer({ html, activeChunk }: Props) {
  return (
    <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
  );
}