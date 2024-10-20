'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { generateVideo, getAlbumById, getVideoDownloadUrl } from '@/utils/api';
import { ArrowLeft, Calendar, Download, ImageIcon, Video } from 'lucide-react';
import { Album } from '@/typing';
import { formatDate } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export default function AlbumDetail({ params }: { params: { id: string } }) {
  const [album, setAlbum] = useState<Album | null>(null);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [downloadingVideo, setDownloadingVideo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isVideoProcessed, setIsVideoProcessed] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    fetchAlbum();
  }, [params.id]);

  useEffect(() => {
    if (videoRef.current && album?.video_url) {
      const videoElement = videoRef.current;

      const handleCanPlay = () => {
        setIsVideoProcessed(true);
      };

      const handleError = (e: Event) => {
        const target = e.target as HTMLVideoElement;
        setVideoError(target.error?.message || 'An error occurred while loading the video.');
        setIsVideoProcessed(false);
      };

      videoElement.addEventListener('canplay', handleCanPlay);
      videoElement.addEventListener('error', handleError);

      return () => {
        videoElement.removeEventListener('canplay', handleCanPlay);
        videoElement.removeEventListener('error', handleError);
      };
    }
  }, [album?.video_url]);

  const fetchAlbum = async () => {
    try {
      const fetchedAlbum = await getAlbumById(params.id);
      console.log('Fetched album:', fetchedAlbum);
      setAlbum(fetchedAlbum);
    } catch (err) {
      console.error('Error fetching album:', err);
      setError('Failed to load album. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (!album) return;
    
    setGeneratingVideo(true);
    try {
      await generateVideo(album.id);
      alert('Video generation started. The page will update shortly.');
      
      // Wait for a short period to allow the backend to process
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // Re-fetch the album data
      await fetchAlbum();
    } catch (err) {
      console.error('Error generating video:', err);
      alert('Failed to start video generation. Please try again later.');
    } finally {
      setGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = async () => {
    if (!album) return;

    setDownloadingVideo(true);
    try {
      const downloadUrl = await getVideoDownloadUrl(album.id);
      window.open(downloadUrl, '_blank');
    } catch (err) {
      console.error('Error getting video download URL:', err);
      alert('Failed to get video download link. Please try again later.');
    } finally {
      setDownloadingVideo(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
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
            className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generatingVideo ? (
              <div className="flex items-center">
                <div className="animate-pulse bg-gradient-to-r from-gray-300 to-gray-400 h-4 w-4 rounded-full mr-2"></div>
                Generating...
              </div>
            ) : (
              <>
                <Video className="mr-2 h-4 w-4" /> Generate Video
              </>
            )}
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
          <h2 className="text-2xl font-semibold mb-4 text-black">Moments in Motion</h2>
          <video 
            ref={videoRef}
            controls 
            className="w-full max-w-3xl mx-auto mb-4"
            onCanPlay={() => setIsVideoProcessed(true)}
            onError={() => setVideoError('An error occurred while loading the video.')}
          >
            <source src={album.video_url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          {!isVideoProcessed && !videoError && (
            <p className="text-center text-gray-600">Video is still processing...</p>
          )}
          {videoError && (
            <p className="text-center text-red-500">Error: {videoError}</p>
          )}
          <Button 
            onClick={handleDownloadVideo}
            disabled={downloadingVideo || !isVideoProcessed}
            className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {downloadingVideo ? (
              <div className="flex items-center">
                <div className="animate-pulse bg-gradient-to-r from-gray-300 to-gray-400 h-4 w-4 rounded-full mr-2"></div>
                Downloading...
              </div>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" /> Download Video
              </>
            )}
          </Button>
        </div>
      )}

      <h2 className="text-2xl font-semibold mb-4 text-black">Photo Moments</h2>
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