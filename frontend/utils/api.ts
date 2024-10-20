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


export async function generateAlbum(input: FormData | { theme: string }): Promise<Album> {
  console.log('Generating album');

  let formData: FormData;

  if (input instanceof FormData) {
    console.log('Sending image-based request');
    formData = input;
  } else {
    console.log('Sending theme-based request');
    formData = new FormData();
    formData.append('theme', input.theme);
  }

  const response = await fetch('/api/generate-album', {
    method: 'POST',
    body: formData,
  });


  if (!response.ok) {
    const errorText = await response.text();
    console.error(`Error response from server: ${response.status} ${errorText}`);
    throw new Error(`Failed to generate album: ${response.status} ${errorText}`);
  }

  const data = await response.json();
  
  // Ensure the response contains the expected fields
  if (!data.id || !data.album_name || !data.description || !Array.isArray(data.images) || !data.createdAt) {
    console.error('Invalid album data format:', data);
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

export async function getAllPhotos(skip: number = 0, limit: number = 20): Promise<Photo[]> {
  const response = await fetch(`/api/all-photos?skip=${skip}&limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch photos');
  }
  return response.json();
}


export async function getAllAlbums(skip: number = 0, limit: number = 20): Promise<Album[]> {
  const response = await fetch(`/api/all-albums?skip=${skip}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch albums: ${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  if (!Array.isArray(data)) {
    throw new Error('Invalid response format');
  }
  return data;
}

export async function getRecentPhotos(limit: number = 4): Promise<Photo[]> {
  const response = await fetch(`/api/recent-photos?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to fetch recent photos');
  }
  return await response.json();
}

export const getRecentAlbums = async (limit: number = 4): Promise<Album[]> => {
  const response = await fetch('/api/recent-albums');
  if (!response.ok) {
    throw new Error('Failed to fetch albums');
  }
  return response.json();
};

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
    createdAt: data.createdAt,
    video_url: data.video_url
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

export async function generateVideo(albumId: string): Promise<void> {
  const response = await fetch(`/api/generate-video/${albumId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to start video generation');
  }

  const data = await response.json();
  console.log('Video generation started:', data);
}

export async function getVideoDownloadUrl(albumId: string): Promise<string> {
  const response = await fetch(`/api/download-video/${albumId}`);
  if (!response.ok) {
    throw new Error('Failed to get video download URL');
  }
  const data = await response.json();
  return data.download_url;
}




