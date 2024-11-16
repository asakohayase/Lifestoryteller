import { buildApiUrl } from '@/app/lib/config';
import { NextResponse } from 'next/server';

export async function GET(req: Request, { params }: { params: { id: string } }) {
  const { id } = params;

  try {
   const response = await fetch(buildApiUrl(`/download-video/${id}`));

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Failed to get video download URL');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error getting video download URL:', error);
    return NextResponse.json({ error: 'Failed to get video download URL' }, { status: 500 });
  }
}