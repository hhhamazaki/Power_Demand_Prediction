import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const model = body.model || 'LightGBM';
    const years = body.years || [];

    const scriptMap: { [key: string]: string } = {
      LightGBM: path.join(process.cwd(), '..', 'AI', 'tomorrow', 'LightGBM', 'LightGBM_tomorrow.py'),
      Keras: path.join(process.cwd(), '..', 'AI', 'tomorrow', 'Keras', 'Keras_tomorrow.py'),
      PyCaret: path.join(process.cwd(), '..', 'AI', 'tomorrow', 'Pycaret', 'Pycaret_tomorrow.py'),
      RandomForest: path.join(process.cwd(), '..', 'AI', 'tomorrow', 'RandomForest', 'RandomForest_tomorrow.py'),
    };

    const scriptPath = scriptMap[model] || scriptMap.LightGBM;

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
