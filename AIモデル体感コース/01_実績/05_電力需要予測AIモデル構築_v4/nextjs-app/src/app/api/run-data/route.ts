import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const years = body.years || [];

    const scriptPath = path.join(process.cwd(), '..', 'AI', 'data', 'data.py');
    
    return new Promise((resolve) => {
      const env = { ...process.env };
      if (years.length > 0) {
        env.AI_TARGET_YEARS = years.join(',');
      }

      const pythonProcess = spawn('python', [scriptPath], {
        env,
        cwd: path.join(process.cwd(), '..', 'AI'),
      });

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        resolve(
          NextResponse.json({
            status: code === 0 ? 'ok' : 'error',
            stdout,
            stderr,
            returncode: code,
          })
        );
      });
    });
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
  }
}
