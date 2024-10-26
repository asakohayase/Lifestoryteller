import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const skip = Number(searchParams.get('skip')) || 0;
  const limit = Number(searchParams.get('limit')) || 20;

  try {
    const response = await fetch(`http://127.0.0.1:8000/all-photos?skip=${skip}&limit=${limit}`);
    const data = await response.json();
    return NextResponse.json(data.photos);
  } catch (error) {
    console.error('Error fetching photos:', error);
    return NextResponse.json({ error: 'Failed to fetch photos' }, { status: 500 });
  }
}