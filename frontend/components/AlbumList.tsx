import { Image as ImageIcon, Plus, X } from 'lucide-react';
import { Card, CardContent} from "@/components/ui/card"
import { AlbumListProps } from '@/typing';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

export default function AlbumList({ albums }: AlbumListProps) {
  const router = useRouter();

  const handleAlbumClick = (albumId: string) => {
    router.push(`/albums/${albumId}`);
  };

  return (
    <div>
    <h2 className="text-2xl font-semibold mb-4 text-blue2">Albums</h2>
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {albums.map((album) => (
        <Card 
          key={album.id} 
          className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden cursor-pointer"
          onClick={() => handleAlbumClick(album.id)}
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
        </Card>
      ))}
    </div>
  </div>
  );
}