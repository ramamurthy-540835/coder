import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Spec Documentation Viewer',
  description: 'Merge, search and view specification chunks',
};
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-zinc-950 text-zinc-200">{children}</body>
    </html>
  );
}