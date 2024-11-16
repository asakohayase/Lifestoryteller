import { buildApiUrl } from '@/app/lib/config';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const skip = Number(searchParams.get('skip')) || 0;
  const limit = Number(searchParams.get('limit')) || 20;

  try {
    const response = await fetch(buildApiUrl(`/all-albums?skip=${skip}&limit=${limit}`));
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return NextResponse.json(data.albums);
  } catch (error) {
    console.error('Error fetching albums:', error);
    return NextResponse.json({ error: 'Failed to fetch albums' }, { status: 500 });
  }
}