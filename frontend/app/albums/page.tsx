'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getAllAlbums, deleteMultipleAlbums } from '@/utils/api';
import { ArrowLeft, ImageIcon, Trash2 } from 'lucide-react';
import { Album } from '@/typing';
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

export default function AllAlbums() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [selectedAlbums, setSelectedAlbums] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchAlbums();
  }, []);

  async function fetchAlbums() {
    try {
      const fetchedAlbums = await getAllAlbums();
      setAlbums(fetchedAlbums);
    } catch (err) {
      console.error('Error fetching albums:', err);
      setError('Failed to load albums. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  const handleSelectAlbum = (albumId: string, event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setSelectedAlbums(prev => 
      prev.includes(albumId) 
        ? prev.filter(id => id !== albumId)
        : [...prev, albumId]
    );
  };

  const handleDeleteSelectedAlbums = async () => {
    if (selectedAlbums.length === 0) return;
    
    if (confirm(`Are you sure you want to delete ${selectedAlbums.length} album(s)? This action cannot be undone.`)) {
      setIsDeleting(true);
      try {
        await deleteMultipleAlbums(selectedAlbums);
        await fetchAlbums();
        setSelectedAlbums([]);
      } catch (error) {
        console.error('Error deleting albums:', error);
        alert('Failed to delete some albums. Please try again.');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return (
      <div className="w-full mx-auto p-6 bg-white min-h-screen font-poppins">
        <h1 className="text-4xl font-bold mb-4 text-red-500">Error</h1>
        <p className="text-lg mb-4 text-black">{error}</p>
        <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300">
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="w-full mx-auto p-12 lg:p-24 bg-white min-h-screen font-poppins">
      <div className="flex justify-between items-center mb-6">
        <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300">
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back to Home
        </Link>
        {selectedAlbums.length > 0 && (
          <Button
            variant="destructive"
            onClick={handleDeleteSelectedAlbums}
            disabled={isDeleting}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            {isDeleting ? 'Deleting...' : `Delete Selected (${selectedAlbums.length})`}
          </Button>
        )}
      </div>
      <h1 className="text-4xl font-bold mb-4 text-blue1">All Albums</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {albums.map((album) => (
          <Link key={album.id} href={`/albums/${album.id}`}>
            <div className="aspect-square relative rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
              {album.cover_image ? (
                <Image 
                  src={album.cover_image.url}
                  alt={`Cover of ${album.album_name}`}
                  fill
                  sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                  style={{ objectFit: 'cover' }}
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <ImageIcon className="h-1/2 w-1/2 text-gray-400" />
                </div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-70"></div>
              <div className="absolute top-2 left-2 z-10" onClick={(e) => handleSelectAlbum(album.id, e)}>
                <Checkbox
                  checked={selectedAlbums.includes(album.id)}
                  onCheckedChange={() => {}}
                  className="bg-white bg-opacity-70 hover:bg-opacity-100 transition-opacity duration-200"
                />
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                <h3 className="text-xl font-semibold truncate">{album.album_name}</h3>
                <p className="text-sm">{album.images.length} {album.images.length === 1 ? 'photo' : 'photos'}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}