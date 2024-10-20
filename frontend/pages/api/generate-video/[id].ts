import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { id } = req.query;

    try {
      const response = await fetch(`http://127.0.0.1:8000/generate-video/${id}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to start video generation');
      }

      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      console.error('Error generating video:', error);
      res.status(500).json({ error: 'Failed to generate video' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}