import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method === 'GET') {
      const skip = Number(req.query.skip) || 0;
      const limit = Number(req.query.limit) || 20;
  
      try {
        const response = await fetch(`http://127.0.0.1:8000/all-photos?skip=${skip}&limit=${limit}`);
        const data = await response.json();
        res.status(200).json(data.photos);
      } catch (error) {
        console.error('Error fetching photos:', error);
        res.status(500).json({ error: 'Failed to fetch photos' });
      }
    } else {
      res.setHeader('Allow', ['GET']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
    }
  }