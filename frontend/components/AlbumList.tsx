import { Image as ImageIcon, Plus, X } from 'lucide-react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Album, AlbumListProps, Photo } from '@/typing';
import { useState } from 'react';
import Image from 'next/image';
import { Dialog, DialogClose, DialogContent, DialogTitle } from '@radix-ui/react-dialog';
import { DialogHeader } from './ui/dialog';

export default function AlbumList({ albums }: AlbumListProps) {
  const [selectedAlbum, setSelectedAlbum] = useState<Album | null>(null);

  const handleAlbumClick = (album: Album) => {
    setSelectedAlbum(album);
  };

  const closeAlbumView = () => {
    setSelectedAlbum(null);
  };

  return (
    <div>
    <h2 className="text-2xl font-semibold mb-4 text-blue2">Albums</h2>
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {albums.map((album) => (
        <Card 
          key={album.id} 
          className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden cursor-pointer"
        >
           <CardContent className="p-2">
              <div className="aspect-square bg-gray-200 rounded-md overflow-hidden relative">
                {album.cover_image  ? (
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
              </div>
              <h3 className="text-lg font-semibold text-blue2 truncate">{album.album_name}</h3>
              <p className="text-sm text-gray-600">{album.images.length} photos</p>
            </CardContent>
          <CardFooter className="bg-white1 p-2 flex justify-center">
            <Button variant="ghost" className="text-blue2 hover:text-blue1" onClick={() => handleAlbumClick(album)}>
              <Plus className="h-4 w-4 mr-1" /> View Album
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>

    {selectedAlbum && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
          <h3 className="text-2xl font-semibold mb-4">{selectedAlbum.album_name}</h3>
          <p className="mb-4">{selectedAlbum.description}</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {selectedAlbum.images.map((photo: Photo) => (
              <div key={photo.id} className="aspect-w-1 aspect-h-1">
                <Image 
                  src={photo.url}
                  alt={`Photo in ${selectedAlbum.album_name}`}
                  layout="fill"
                  objectFit="cover"
                  className="rounded-md"
                />
              </div>
            ))}
          </div>
          <Button className="mt-4" onClick={() => setSelectedAlbum(null)}>Close</Button>
        </div>
      </div>
    )}
  </div>
  );
}