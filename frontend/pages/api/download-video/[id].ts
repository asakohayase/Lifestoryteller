import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const { id } = req.query;

    try {
      const response = await fetch(`http://127.0.0.1:8000/download-video/${id}`);

      if (!response.ok) {
        throw new Error('Failed to get video download URL');
      }

      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      console.error('Error getting video download URL:', error);
      res.status(500).json({ error: 'Failed to get video download URL' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}