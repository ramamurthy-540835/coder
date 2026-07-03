import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: Request) {
  try {
    const { action, promptId } = await request.json();
    
    if (!promptId) {
      return NextResponse.json({ success: false, error: 'Missing promptId parameter' }, { status: 400 });
    }
    
    const gcloudRunPath = '/home/appadmin/projects/Ram_Projects/DiracDelta/gcloud_run';

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
        PATH: `${process.env.PATH}:/snap/bin:/usr/bin:/home/appadmin/projects/Ram_Projects/DiracDelta/gcloud_run/venv/bin` 
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
