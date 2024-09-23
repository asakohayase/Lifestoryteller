import { Image as ImageIcon } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card"

interface RecentPhotosProps {
  photos: string[];
}

export default function RecentPhotos({ photos }: RecentPhotosProps) {
  return (
    <div className="mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-blue2">Recent Photos</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {photos.map((_, index) => (
          <Card key={index} className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden">
            <CardContent className="p-2">
              <div className="aspect-w-1 aspect-h-1 bg-gray-200 rounded-md overflow-hidden">
                <ImageIcon className="h-full w-full text-gray-400 p-4" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}