"use client";

import { Camera, Image as ImageIcon, Trash2 } from 'lucide-react';
import { RecentPhotoProps } from '@/typing';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Button } from './ui/button';
import { Checkbox } from "@/components/ui/checkbox"
import { deleteMultiplePhotos } from '@/utils/api';
import Link from 'next/link';

export default function RecentPhotos({ photos, onPhotoDeleted }: RecentPhotoProps) {
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);


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
        onPhotoDeleted();
        setSelectedPhotos([]);
      } catch (error) {
        console.error('Error deleting photos:', error);
        alert('Failed to delete some photos. Please try again.');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="mb-8">
     <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-black">Recent Photos</h2>
        <div className="flex-grow"></div>
        <div className="flex items-center space-x-4">
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
          {photos.length > 0 && (
          <Link href="/photos" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300">
            View All Photos
          </Link>
          )}
        </div>
      </div>
    {photos.length === 0 ? (
      <div className="bg-white overflow-hidden p-6 text-center">
        <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-semibold text-gray-600 mb-2">Time to capture some memories!</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
       {photos.map((photo) => ( 
          <div key={photo.id} className="aspect-square relative rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
            {photo.url ? (
              <Image 
                src={photo.url} 
                alt="Uploaded photo" 
                fill
                sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                style={{
                  objectFit: 'cover',
                }}
                unoptimized={true}
              />
            ) : (
              <ImageIcon className="h-full w-full text-gray-400 p-4" />
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
    )}
  </div>
  );
}