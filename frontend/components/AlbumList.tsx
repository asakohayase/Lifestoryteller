import { Image as ImageIcon, Plus } from 'lucide-react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"

interface Album {
  name: string;
  photoCount: number;
}

interface AlbumListProps {
  albums: Album[];
}

export default function AlbumList({ albums }: AlbumListProps) {
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4 text-blue2">Albums</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {albums.map((album, index) => (
          <Card key={index} className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden">
            <CardContent className="p-4">
              <div className="aspect-w-1 aspect-h-1 bg-gray-200 rounded-md overflow-hidden mb-2">
                <ImageIcon className="h-full w-full text-gray-400 p-4" />
              </div>
              <h3 className="text-lg font-semibold text-blue2 truncate">{album.name}</h3>
              <p className="text-sm text-gray-600">{album.photoCount} photos</p>
            </CardContent>
            <CardFooter className="bg-white1 p-2 flex justify-center">
              <Button variant="ghost" className="text-blue2 hover:text-blue1">
                <Plus className="h-4 w-4 mr-1" /> View Album
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}