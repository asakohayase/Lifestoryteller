import { buildApiUrl } from '@/app/lib/config';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const limit = Number(searchParams.get('limit')) || 4;

  try {
    const response = await fetch(buildApiUrl(`/recent-photos?limit=${limit}`));
    const data = await response.json();
    return NextResponse.json(data.photos);
  } catch (error) {
    console.error('Error fetching recent photos:', error);
    return NextResponse.json({ error: 'Failed to fetch recent photos' }, { status: 500 });
  }
}