import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { promisify } from 'util';

const readdir = promisify(fs.readdir);

export async function GET(request: NextRequest) {
  try {
    const dataDir = path.join(process.cwd(), '..', 'AI', 'data');
    
    const powerFiles = (await readdir(dataDir))
      .filter(f => f.startsWith('juyo-') && f.endsWith('.csv'))
      .map(f => f.slice(5, 9));
    
    const tempFiles = (await readdir(dataDir))
      .filter(f => f.startsWith('temperature-') && f.endsWith('.csv'))
      .map(f => f.slice(12, 16));
    
    const commonYears = [...new Set(powerFiles.filter(y => tempFiles.includes(y)))].sort();
    
    return NextResponse.json({ years: commonYears });
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Unknown error',
      years: [],
    }, { status: 500 });
  }
}
