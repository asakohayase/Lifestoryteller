import { NextResponse } from 'next/server';

export async function GET(req: Request, { params }: { params: { id: string } }) {
  const { id } = params;

  try {
    const response = await fetch(`http://127.0.0.1:8000/download-video/${id}`);

    if (!response.ok) {
      throw new Error('Failed to get video download URL');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting video download URL:', error);
    return NextResponse.json({ error: 'Failed to get video download URL' }, { status: 500 });
  }
}