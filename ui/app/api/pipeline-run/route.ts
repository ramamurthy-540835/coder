import { spawn } from 'child_process';
import { NextRequest } from 'next/server';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const promptId = searchParams.get('promptId') || '3381323161097207808';

  // In container: script is at /app/agents/coding_agent.py (since WORKDIR is /app)
  // In local development: script is in parent agents/ folder
  const isContainer = process.env.NODE_ENV === 'production';
  const scriptPath = isContainer ? 'agents/coding_agent.py' : path.join(process.cwd(), 'agents', 'coding_agent.py');
  const runCwd = isContainer ? '/app' : process.cwd();

  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      log('🚀 Spawning 5-Agent Cooperative Pipeline for Prompt ' + promptId + '...\n');
      
      const child = spawn('python3', [scriptPath, promptId], {
        cwd: runCwd,
        env: { 
          ...process.env, 
          PYTHONUNBUFFERED: '1',
          PATH: isContainer ? `/opt/venv/bin:${process.env.PATH}` : process.env.PATH
        }
      });

      child.stdout.on('data', (data) => {
        controller.enqueue(encoder.encode(data.toString()));
      });

      child.stderr.on('data', (data) => {
        controller.enqueue(encoder.encode(`[STDERR] ${data.toString()}`));
      });

      child.on('close', (code) => {
        log(`\n🎉 Pipeline execution finished with exit code ${code}.\n`);
        controller.close();
      });

      child.on('error', (err) => {
        log(`\n❌ Failed to spawn pipeline script: ${err.message}\n`);
        controller.close();
      });

      function log(msg: string) {
        controller.enqueue(encoder.encode(msg));
      }
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
