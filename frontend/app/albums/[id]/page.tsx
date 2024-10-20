'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { generateVideo, getAlbumById, getVideoDownloadUrl } from '@/utils/api';
import { ArrowLeft, Calendar, Download, ImageIcon, Video } from 'lucide-react';
import { Album } from '@/typing';
import { formatDate } from '@/lib/utils';
import { Button } from '@/components/ui/button';


export default function AlbumDetail({ params }: { params: { id: string } }) {
  const [album, setAlbum] = useState<Album| null>(null);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  console.log(album)
 
  useEffect(() => {
    async function fetchAlbum() {
      try {
        const fetchedAlbum = await getAlbumById(params.id);
        setAlbum(fetchedAlbum);
        console.log('Fetched album:', fetchedAlbum);
      } catch (err) {
        console.error('Error fetching album:', err);
        setError('Failed to load album. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    fetchAlbum();
  }, [params.id]);

  const handleGenerateVideo = async () => {
    if (!album) return;
    
    setGeneratingVideo(true);
    try {
      await generateVideo(album.id);
      alert('Video generation started. Please refresh the page in a few minutes to see the video.');
    } catch (err) {
      console.error('Error generating video:', err);
      alert('Failed to start video generation. Please try again later.');
    } finally {
      setGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = async () => {
    if (!album) return;

    try {
      const downloadUrl = await getVideoDownloadUrl(album.id);
      window.open(downloadUrl, '_blank');
    } catch (err) {
      console.error('Error getting video download URL:', err);
      alert('Failed to get video download link. Please try again later.');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
    <div className="w-full mx-auto px-12 py-8 lg:px-24 bg-white min-h-screen">
        <h1 className="text-4xl font-bold mb-4 text-red-500">Error</h1>
        <p className="text-lg mb-4 text-black">{error}</p>
        <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300">
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back to Home
        </Link>
      </div>
    );
  }

  if (!album) {
    return null;
  }

  return (
    <div className="w-full mx-auto px-12 py-8 lg:px-24 bg-white min-h-screen">
    <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300 mb-6">
      <ArrowLeft className="mr-2 h-5 w-5" />
      Back to Home
    </Link>
    <div className="flex justify-between items-center mb-4">
      <h1 className="text-4xl font-bold text-blue1">{album.album_name}</h1>
      {!album.video_url && (
        <Button 
          onClick={handleGenerateVideo}
          disabled={generatingVideo}
          className="flex items-center"
        >
          <Video className="mr-2 h-4 w-4" />
          {generatingVideo ? 'Generating...' : 'Generate Video'}
        </Button>
      )}
    </div>
    <p className="text-lg mb-2 text-gray-600">{album.description}</p>
    {album.createdAt && (
      <p className="text-sm mb-8 text-gray-500 flex items-center">
        <Calendar className="mr-2 h-4 w-4" />
        Created on: {formatDate(album.createdAt)} 
      </p>
    )}
    
    {album.video_url && (
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-black">Album Video</h2>
        <video controls className="w-full max-w-3xl mx-auto mb-4">
          <source src={album.video_url} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <Button onClick={handleDownloadVideo} className="flex items-center">
          <Download className="mr-2 h-4 w-4" />
          Download Video
        </Button>
      </div>
    )}

    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {album.images.map((photo) => (
        <div key={photo.id} className="aspect-square relative rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
          {photo.url ? (
            <Image 
              src={photo.url}
              alt={`Photo in ${album.album_name}`}
              fill
              sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
              style={{ objectFit: 'cover' }}
            />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <ImageIcon className="h-1/2 w-1/2 text-gray-400" />
            </div>
          )}
        </div>
      ))}
    </div>
  </div>
  );
}