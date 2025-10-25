import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const filePath = path.join(process.cwd(), '..', 'AI', ...params.path);
    
    // ファイルの存在確認
    if (!fs.existsSync(filePath)) {
      return new NextResponse('File not found', { status: 404 });
    }

    // ファイルの読み込み
    const fileBuffer = await readFile(filePath);
    
    // Content-Typeの判定
    let contentType = 'application/octet-stream';
    if (filePath.endsWith('.png')) {
      contentType = 'image/png';
    } else if (filePath.endsWith('.csv')) {
      contentType = 'text/csv';
    } else if (filePath.endsWith('.json')) {
      contentType = 'application/json';
    }

    return new NextResponse(fileBuffer, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
      },
    });
  } catch (error) {
    return new NextResponse(
      error instanceof Error ? error.message : 'Unknown error',
      { status: 500 }
    );
  }
}
