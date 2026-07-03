'use client';
import React from 'react';

interface Props { value: string; onChange: (v: string) => void; }
export default function SearchBar({ value, onChange }: Props) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Search specification..."
      className="w-full rounded-md border border-zinc-700 bg-zinc-900 px-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-zinc-500"
    />
  );
}