import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query;
  const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
  const fullUrl = `${backendUrl}/albums/${id}`;

  try {
    const response = await fetch(fullUrl);
 
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Fetch error:', error);
    res.status(500).json({ error: 'Failed to fetch album from backend' });
  }
}