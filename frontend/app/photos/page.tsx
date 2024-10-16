'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getAllPhotos, deleteMultiplePhotos } from '@/utils/api';
import { ArrowLeft, ImageIcon, Trash2 } from 'lucide-react';
import { Photo } from '@/typing';
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

export default function AllPhotos() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchPhotos();
  }, []);

  async function fetchPhotos() {
    try {
      const fetchedPhotos = await getAllPhotos();
      setPhotos(fetchedPhotos);
    } catch (err) {
      console.error('Error fetching photos:', err);
      setError('Failed to load photos. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  const handleSelectPhoto = (photoId: string) => {
    setSelectedPhotos(prev => 
      prev.includes(photoId) 
        ? prev.filter(id => id !== photoId)
        : [...prev, photoId]
    );
  };

  const handleDeleteSelectedPhotos = async () => {
    if (selectedPhotos.length === 0) return;
    
    if (confirm(`Are you sure you want to delete ${selectedPhotos.length} photo(s)? This action cannot be undone.`)) {
      setIsDeleting(true);
      try {
        await deleteMultiplePhotos(selectedPhotos);
        await fetchPhotos();
        setSelectedPhotos([]);
      } catch (error) {
        console.error('Error deleting photos:', error);
        alert('Failed to delete some photos. Please try again.');
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
        {selectedPhotos.length > 0 && (
          <Button
            variant="destructive"
            onClick={handleDeleteSelectedPhotos}
            disabled={isDeleting}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            {isDeleting ? 'Deleting...' : `Delete Selected (${selectedPhotos.length})`}
          </Button>
        )}
      </div>
      <h1 className="text-4xl font-bold mb-4 text-blue1">All Photos</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {photos.map((photo) => (
          <div key={photo.id} className="aspect-square relative rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
            {photo.url ? (
              <Image 
                src={photo.url}
                alt={`Photo ${photo.id}`}
                fill
                sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                style={{ objectFit: 'cover' }}
              />
            ) : (
              <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                <ImageIcon className="h-1/2 w-1/2 text-gray-400" />
              </div>
            )}
            <div className="absolute top-2 left-2 z-10">
              <Checkbox
                checked={selectedPhotos.includes(photo.id)}
                onCheckedChange={() => handleSelectPhoto(photo.id)}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}