import { buildApiUrl } from '@/app/lib/config';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const response = await fetch(buildApiUrl(`/albums/${params.id}`));
    
    if (!response.ok) {
      console.error('Backend response not OK:', response.status, response.statusText);
      return NextResponse.json(
        { error: `Failed to fetch album: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Validate that we have images array
    if (!data.images || !Array.isArray(data.images)) {
      console.error('Invalid album data - missing or invalid images array:', data);
      return NextResponse.json(
        { error: 'Album data is invalid' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching album:', error);
    return NextResponse.json(
      { error: 'Failed to fetch album from backend' },
      { status: 500 }
    );
  }
}