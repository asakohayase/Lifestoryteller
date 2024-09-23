// pages/api/generate-album.ts

import type { NextApiRequest, NextApiResponse } from 'next'
import fetch from 'node-fetch'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { theme } = req.body;

      const response = await fetch('http://127.0.0.1:8000/generate-album', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ theme }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

    const result = await response.json()
    console.log("Result", result);
    if (result.imageId && typeof result.imageId === 'object' && result.imageId.raw) {
    console.error("Error from FastAPI:", result.imageId.raw);
    return res.status(500).json({ error: result.imageId.raw });
    }
res.status(200).json(result)
      res.status(200).json(result);
    } catch (error) {
      console.error('Error generating album:', error);
      res.status(500).json({ error: 'Error generating album' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}