import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const limit = Number(searchParams.get('limit')) || 4;

  try {
    const response = await fetch(`http://127.0.0.1:8000/recent-albums?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    // Validate the response data
    if (!data.albums || !Array.isArray(data.albums)) {
      throw new Error('Invalid response format from backend');
    }

    return NextResponse.json(data.albums);
  } catch (error) {
    console.error('Error fetching recent albums:', error);
    return NextResponse.json(
      { error: 'Failed to fetch recent albums' }, 
      { status: 500 }
    );
  }
}