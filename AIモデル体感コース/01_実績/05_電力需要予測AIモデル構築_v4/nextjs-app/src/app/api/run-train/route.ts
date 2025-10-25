import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const model = body.model || 'LightGBM';
    const years = body.years || [];

    const scriptMap: { [key: string]: string } = {
      LightGBM: path.join(process.cwd(), '..', 'AI', 'train', 'LightGBM', 'LightGBM_train.py'),
      Keras: path.join(process.cwd(), '..', 'AI', 'train', 'Keras', 'Keras_train.py'),
      PyCaret: path.join(process.cwd(), '..', 'AI', 'train', 'Pycaret', 'Pycaret_train.py'),
      RandomForest: path.join(process.cwd(), '..', 'AI', 'train', 'RandomForest', 'RandomForest_train.py'),
    };

    const scriptPath = scriptMap[model] || scriptMap.LightGBM;

    return new Promise((resolve) => {
      const env = { ...process.env };
      if (years.length > 0) {
        env.AI_TARGET_YEARS = years.join(',');
      }

      // データ処理を先に実行
      const dataScriptPath = path.join(process.cwd(), '..', 'AI', 'data', 'data.py');
      const dataProcess = spawn('python', [dataScriptPath], {
        env,
        cwd: path.join(process.cwd(), '..', 'AI'),
      });

      let combinedStdout = '';
      let combinedStderr = '';

      dataProcess.stdout.on('data', (data) => {
        combinedStdout += data.toString();
      });

      dataProcess.stderr.on('data', (data) => {
        combinedStderr += data.toString();
      });

      dataProcess.on('close', (dataCode) => {
        if (dataCode !== 0) {
          resolve(
            NextResponse.json({
              status: 'error',
              stdout: combinedStdout,
              stderr: combinedStderr,
              returncode: dataCode,
            })
          );
          return;
        }

        // データ処理が成功したら学習を実行
        const trainProcess = spawn('python', [scriptPath], {
          env,
          cwd: path.join(process.cwd(), '..', 'AI'),
        });

        trainProcess.stdout.on('data', (data) => {
          combinedStdout += '\n--- TRAIN STDOUT ---\n' + data.toString();
        });

        trainProcess.stderr.on('data', (data) => {
          combinedStderr += '\n--- TRAIN STDERR ---\n' + data.toString();
        });

        trainProcess.on('close', (trainCode) => {
          resolve(
            NextResponse.json({
              status: trainCode === 0 ? 'ok' : 'error',
              stdout: combinedStdout,
              stderr: combinedStderr,
              returncode: trainCode,
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
