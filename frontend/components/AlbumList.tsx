"use client"

import { BookOpen, Image as ImageIcon, Plus, Trash2, X } from 'lucide-react';
import { Card, CardContent} from "@/components/ui/card"
import { AlbumListProps } from '@/typing';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { deleteMultipleAlbums } from '@/utils/api';
import { useState } from 'react';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';

export default function AlbumList({ albums,  onAlbumsDeleted }: AlbumListProps) {
  const [selectedAlbums, setSelectedAlbums] = useState<string[]>([]);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const router = useRouter();

  const handleAlbumClick = (albumId: string) => {
    router.push(`/albums/${albumId}`);
  };


  const handleSelectAlbum = (albumId: string, event: React.MouseEvent) => {
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
        onAlbumsDeleted();
        setSelectedAlbums([]);
      } catch (error) {
        console.error('Error deleting albums:', error);
        alert('Failed to delete some albums. Please try again.');
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-black">Albums</h2>
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
      {albums.length === 0 ? (
        <div className="bg-white overflow-hidden p-6 text-center">
          <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-semibold text-gray-600 mb-2">Your album shelf is looking a bit lonely!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {albums.map((album) => (
            <Card 
              key={album.id} 
              className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden cursor-pointer"
              onClick={() => handleAlbumClick(album.id)}
            >
              <CardContent className="p-2 relative">
                <div className="aspect-square bg-gray-200 rounded-md overflow-hidden relative">
                  {album.cover_image ? (
                    <Image 
                      src={album.cover_image.url}
                      alt={`Cover of ${album.album_name}`}
                      fill
                      sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                      style={{
                        objectFit: 'cover',
                      }}
                    />
                  ) : (
                    <ImageIcon className="h-full w-full text-gray-400 p-4" />
                  )}
                  <div className="absolute top-2 left-2 z-10" onClick={(e) => handleSelectAlbum(album.id, e)}>
                    <Checkbox
                      checked={selectedAlbums.includes(album.id)}
                      onCheckedChange={() => {}}
                    />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-blue2 truncate mt-2">{album.album_name}</h3>
                <p className="text-sm text-gray-600">{album.images.length} photos</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}