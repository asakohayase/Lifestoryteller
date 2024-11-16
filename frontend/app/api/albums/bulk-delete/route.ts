import { buildApiUrl } from '@/app/lib/config';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { albumIds } = body;

    if (!albumIds || !Array.isArray(albumIds)) {
      console.error('Invalid albumIds:', albumIds);
      return NextResponse.json(
        { error: 'Invalid albumIds provided' },
        { status: 400 }
      );
    }

    const response = await fetch(buildApiUrl('/albums/bulk-delete'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ album_ids: albumIds }),
    });

    const responseText = await response.text();

    if (!response.ok) {
      console.error('Backend delete failed:', response.status, responseText);
      return NextResponse.json(
        { error: `Failed to delete albums: ${response.statusText}` },
        { status: response.status }
      );
    }

    let result;
    try {
      result = responseText ? JSON.parse(responseText) : {};
    } catch (e) {
      console.error('Error parsing response:', e);
      result = { message: 'Albums deleted' };
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error in bulk delete:', error);
    return NextResponse.json(
      { error: 'Failed to delete albums', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
