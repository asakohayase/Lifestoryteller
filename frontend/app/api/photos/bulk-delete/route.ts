import { buildApiUrl } from '@/app/lib/config';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { photoIds } = await req.json();

  if (!photoIds || !Array.isArray(photoIds)) {
    return NextResponse.json({ message: 'Invalid photoIds provided' }, { status: 400 });
  }

  try {
    const response = await fetch(buildApiUrl('/photos/bulk-delete'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ photo_ids: photoIds }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to delete photos: ${response.status} ${errorText}`);
    }

    const result = await response.json();
    return NextResponse.json(result, { status: 200 });
  } catch (error) {
    return NextResponse.json({ message: 'Failed to delete photos' }, { status: 500 });
  }
}