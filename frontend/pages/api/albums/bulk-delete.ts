import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' })
  }

  const { albumIds } = req.body

  if (!albumIds || !Array.isArray(albumIds)) {
    return res.status(400).json({ message: 'Invalid albumIds provided' })
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/albums/bulk-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ album_ids: albumIds }),
    })

    if (!response.ok) {
      throw new Error('Failed to delete albums')
    }

    const result = await response.json()
    res.status(200).json(result)
  } catch (error) {
    console.error('Error deleting albums:', error)
    res.status(500).json({ message: 'Failed to delete albums' })
  }
}