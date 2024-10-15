import { Album, Photo } from "../typing";


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

export const fetchAlbums = async (): Promise<Album[]> => {
  const response = await fetch('/api/albums');
  if (!response.ok) {
    throw new Error('Failed to fetch albums');
  }
  return response.json();
};



export async function generateAlbum(theme: string): Promise<Album> {
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

  const data = await response.json();
  
  // Ensure the response contains the expected fields
  if (!data.id || !data.album_name || !data.description || !Array.isArray(data.images)) {
    throw new Error('Invalid album data format');
  }

  return {
    id: data.id,
    album_name: data.album_name,
    description: data.description,
    images: data.images,
    cover_image: data.cover_image
  };
}

export async function getAlbumById(id: string): Promise<Album> {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';
  const url = `${baseUrl}/api/albums/${id}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch album');
  }
  const data = await response.json();
  
  if (!data.id || !data.album_name || !data.description || !Array.isArray(data.images)) {
    throw new Error('Invalid album data format');
  }

  return {
    id: data.id,
    album_name: data.album_name,
    description: data.description,
    images: data.images,
    cover_image: data.cover_image,
    createdAt: data.createdAt
  };
}

export async function deleteMultiplePhotos(photoIds: string[]): Promise<void> {
  const response = await fetch('/api/photos/bulk-delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ photoIds }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Error deleting photos:', response.status, errorText);
    throw new Error(`Failed to delete photos: ${response.status} ${errorText}`);
  }

  const result = await response.json();
  console.log('Deletion result:', result);

  if (result.failed && result.failed.length > 0) {
    console.warn('Some photos failed to delete:', result.failed);
  }
}

export async function deleteMultipleAlbums(albumIds: string[]): Promise<void> {
  const response = await fetch('/api/albums/bulk-delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ albumIds }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Error deleting albums:', response.status, errorText);
    throw new Error(`Failed to delete albums: ${response.status} ${errorText}`);
  }
}