import { Photo } from "@/typing";

export async function uploadPhoto(formData: FormData) {
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload image');
  }

  return await response.json();
}

export async function fetchRecentPhotos(limit: number = 8): Promise<Photo[]> {
  const response = await fetch(`/api/recent-photos?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch recent photos');
  }
  return await response.json();
}


export async function generateAlbum(theme: string) {
  const response = await fetch('/api/generate-album', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ theme }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate album');
  }

  return await response.json();
}