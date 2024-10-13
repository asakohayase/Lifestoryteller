import { Camera, Image as ImageIcon } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card"
import { Photo } from '@/typing';
import { useState } from 'react';
import Image from 'next/image';


export default function RecentPhotos({ photos }: { photos: Photo[] }) {
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});

  const handleImageError = (photoId: string) => {
    setImageErrors(prev => ({ ...prev, [photoId]: true }));
  };

  return (
    <div className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-blue2">Recent Photos</h2>
      {photos.length === 0 ? (
        <div className="bg-white overflow-hidden p-6 text-center">
          <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-semibold text-gray-600 mb-2">Time to capture some memories!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {photos.map((photo) => (
            <Card key={photo.id} className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden">
              <CardContent className="p-2">
                <div className="aspect-square bg-gray-200 rounded-md overflow-hidden relative">
                  {photo.url && !imageErrors[photo.id] ? (
                    <Image 
                      src={photo.url} 
                      alt="Uploaded photo" 
                      fill
                      sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                      style={{
                        objectFit: 'cover',
                      }}
                      onError={() => handleImageError(photo.id)}
                    />
                  ) : (
                    <ImageIcon className="h-full w-full text-gray-400 p-4" />
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}