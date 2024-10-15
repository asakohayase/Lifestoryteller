import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' })
  }

  const { photoIds } = req.body

  if (!photoIds || !Array.isArray(photoIds)) {
    return res.status(400).json({ message: 'Invalid photoIds provided' })
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/photos/bulk-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ photo_ids: photoIds }),
    })

    if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response from backend:', response.status, errorText)
        throw new Error(`Failed to delete photos: ${response.status} ${errorText}`)
      }

    const result = await response.json()
    res.status(200).json(result)
  } catch (error) {
    console.error('Error deleting photos:', error)
    res.status(500).json({ message: 'Failed to delete photos' })
  }
}