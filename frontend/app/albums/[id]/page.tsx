import Image from 'next/image';
import Link from 'next/link';
import { getAlbumById } from '@/utils/api';
import { ArrowLeft } from 'lucide-react'; 

export default async function AlbumDetail({ params }: { params: { id: string } }) {
  try {
    const album = await getAlbumById(params.id);

    return (
      <div className="w-full mx-auto p-12 lg:p-24 bg-white min-h-screen font-poppins">
        <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300 mb-6">
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back to Home
        </Link>
        <h1 className="text-4xl font-bold mb-4 text-blue1">{album.album_name}</h1>
        <p className="text-lg mb-8 text-gray-600">{album.description}</p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {album.images.map((photo) => (
            <div key={photo.id} className="aspect-square relative rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
              <Image 
                src={photo.url}
                alt={`Photo in ${album.album_name}`}
                fill
                sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                style={{ objectFit: 'cover' }}
              />
            </div>
          ))}
        </div>
      </div>
    );
  } catch (error) {
    console.error('Error fetching album:', error);
    return (
      <div className="w-full mx-auto p-6 bg-white min-h-screen font-poppins">
        <h1 className="text-4xl font-bold mb-4 text-red-500">Error</h1>
        <p className="text-lg mb-4 text-black">Failed to load album. Please try again later.</p>
        <Link href="/" className="inline-flex items-center text-blue2 hover:text-blue1 font-semibold transition duration-300">
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back to Home
        </Link>
      </div>
    );
  }
}