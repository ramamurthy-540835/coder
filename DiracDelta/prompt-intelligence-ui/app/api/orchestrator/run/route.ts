import { NextResponse } from 'next/server';
import { execFile } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execFileAsync = promisify(execFile);

const DEFAULT_CONTEXT_ROOTS = ['agents/core', 'agents/runners'];
const ALLOWED_MODEL_ROUTES = new Set(['auto', 'fast_code', 'balanced_code', 'hard_reasoning', 'large_context', 'data_report', 'grok43', 'glm5', 'grok420_reasoning', 'grok420_non_reasoning']);
const ALLOWED_SELECTOR_MODES = new Set(['heuristic', 'gemini']);
const ALLOWED_COST_MODES = new Set(['low', 'balanced', 'best']);

function coderRoot() {
  return process.env.CODER_ROOT || path.resolve(process.cwd(), '../..');
}

function pythonBinary(root: string) {
  if (process.env.PYTHON_BIN) return process.env.PYTHON_BIN;
  const venvPython = path.join(root, '.venv', 'bin', 'python');
  return fs.existsSync(venvPython) ? venvPython : 'python3';
}

function cleanList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === 'string')
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((item) => !path.isAbsolute(item) && !item.includes('..'));
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const task = typeof body.task === 'string' && body.task.trim()
      ? body.task.trim()
      : 'Review the PRISM coding agent orchestrator and summarize model selection evidence.';
    const dryRun = body.dryRun !== false;
    const allowLiveModel = body.allowLiveModel === true;

    if (!dryRun && !allowLiveModel) {
      return NextResponse.json(
        { success: false, error: 'Live model calls require allowLiveModel=true.' },
        { status: 400 }
      );
    }

    const modelRoute = ALLOWED_MODEL_ROUTES.has(body.modelRoute) ? body.modelRoute : 'auto';
    const selectorMode = ALLOWED_SELECTOR_MODES.has(body.selectorMode) ? body.selectorMode : 'heuristic';
    const costMode = ALLOWED_COST_MODES.has(body.costMode) ? body.costMode : 'balanced';
    const contextRoots = cleanList(body.contextRoots).length ? cleanList(body.contextRoots) : DEFAULT_CONTEXT_ROOTS;
    const maxFiles = Number.isFinite(Number(body.maxFiles)) ? String(Math.max(1, Math.min(80, Number(body.maxFiles)))) : '8';

    const args = [
      'agents/core/orchestrator.py',
      '--task', task,
      '--model-route', modelRoute,
      '--selector-mode', selectorMode,
      '--cost-mode', costMode,
      '--max-files', maxFiles,
    ];

    if (dryRun) args.push('--dry-run');
    if (typeof body.promptFile === 'string' && body.promptFile.trim() && !path.isAbsolute(body.promptFile) && !body.promptFile.includes('..')) {
      args.push('--prompt-file', body.promptFile.trim());
    }
    if (typeof body.bigQueryPromptUid === 'string' && body.bigQueryPromptUid.trim()) {
      args.push('--bigquery-prompt-uid', body.bigQueryPromptUid.trim());
    }
    for (const root of contextRoots) {
      args.push('--context-root', root);
    }

    const cwd = coderRoot();
    const python = pythonBinary(cwd);
    const { stdout, stderr } = await execFileAsync(python, args, {
      cwd,
      env: {
        ...process.env,
        GOOGLE_CLOUD_PROJECT: process.env.GCP_PROJECT_ID || process.env.GOOGLE_CLOUD_PROJECT || 'ctoteam',
        VERTEX_LOCATION: process.env.GOOGLE_CLOUD_LOCATION || process.env.VERTEX_LOCATION || 'global',
      },
      timeout: dryRun ? 60_000 : 240_000,
      maxBuffer: 10 * 1024 * 1024,
    });

    let parsed: unknown = null;
    try {
      parsed = JSON.parse(stdout);
    } catch {
      parsed = null;
    }

    return NextResponse.json({
      success: true,
      cwd,
      python,
      args,
      dryRun,
      result: parsed,
      stdout,
      stderr,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
      stdout: error.stdout,
      stderr: error.stderr,
    }, { status: 500 });
  }
}
