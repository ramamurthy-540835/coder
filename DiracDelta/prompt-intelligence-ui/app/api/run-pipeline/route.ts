import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(request: Request) {
  try {
    const { action, promptId } = await request.json();
    
    if (!promptId) {
      return NextResponse.json({ success: false, error: 'Missing promptId parameter' }, { status: 400 });
    }
    
    const gcloudRunPath = process.env.GCLOUD_RUN_ROOT || path.resolve(process.env.CODER_ROOT || path.resolve(process.cwd(), '../..'), 'gcloud_run');

    let command = '';
    if (action === 'refresh') {
      command = `./scripts/extract_store_prompt.sh ${promptId} --force`;
    } else if (action === 'estimate') {
      command = `./scripts/run_ai_development_estimator.sh ${promptId} ../coder`;
    } else {
      return NextResponse.json({ success: false, error: 'Invalid action specified' }, { status: 400 });
    }

    const { stdout, stderr } = await execAsync(command, {
      cwd: gcloudRunPath,
      env: { 
        ...process.env, 
        PATH: `${process.env.PATH}:/snap/bin:/usr/bin:${gcloudRunPath}/venv/bin` 
      }
    });

    return NextResponse.json({
      success: true,
      stdout,
      stderr
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
      stdout: error.stdout,
      stderr: error.stderr
    }, { status: 500 });
  }
}
