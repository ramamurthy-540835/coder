import './globals.css';
import React from 'react';

export const metadata = {
  title: '5-Agent Cooperative Coding Pipeline Dashboard',
  description: 'GCP-native, LangGraph-audited multi-agent orchestrator dashboard.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-zinc-900 min-h-screen">
        {children}
      </body>
    </html>
  );
}
