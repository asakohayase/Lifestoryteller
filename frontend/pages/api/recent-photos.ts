import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const limit = Number(req.query.limit) || 8;
      const response = await fetch(`http://127.0.0.1:8000/recent-photos?limit=${limit}`);
      const data = await response.json();
      res.status(200).json(data.photos);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch recent photos' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}