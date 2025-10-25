import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const dataScript = path.join(process.cwd(), '..', 'AI', 'tomorrow', 'data.py');
    const tempScript = path.join(process.cwd(), '..', 'AI', 'tomorrow', 'temp.py');

    return new Promise((resolve) => {
      const env = { ...process.env };
      let combinedStdout = '';
      let combinedStderr = '';

      // data.pyを実行
      const dataProcess = spawn('python', [dataScript], {
        env,
        cwd: path.join(process.cwd(), '..', 'AI'),
      });

      dataProcess.stdout.on('data', (data) => {
        combinedStdout += data.toString();
      });

      dataProcess.stderr.on('data', (data) => {
        combinedStderr += data.toString();
      });

      dataProcess.on('close', (dataCode) => {
        // temp.pyを実行
        const tempProcess = spawn('python', [tempScript], {
          env,
          cwd: path.join(process.cwd(), '..', 'AI'),
        });

        tempProcess.stdout.on('data', (data) => {
          combinedStdout += '\n--- TEMP STDOUT ---\n' + data.toString();
        });

        tempProcess.stderr.on('data', (data) => {
          combinedStderr += '\n--- TEMP STDERR ---\n' + data.toString();
        });

        tempProcess.on('close', (tempCode) => {
          const returncode = Math.max(dataCode || 0, tempCode || 0);
          resolve(
            NextResponse.json({
              status: returncode === 0 ? 'ok' : 'error',
              stdout: combinedStdout,
              stderr: combinedStderr,
              returncode,
            })
          );
        });
      });
    });
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 });
  }
}
