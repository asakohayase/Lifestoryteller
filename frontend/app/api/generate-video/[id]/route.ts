import { NextResponse } from 'next/server';

export async function POST(req: Request, { params }: { params: { id: string } }) {
  const { id } = params;

  try {
    const response = await fetch(`http://127.0.0.1:8000/generate-video/${id}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to start video generation');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to generate video' }, { status: 500 });
  }
}