"use client";

import React, { useEffect, useState } from 'react';
import UploadPhoto from '@/components/UploadPhoto';
import GenerateAlbum from '@/components/GenerateAlbum';
import RecentPhotos from '@/components/RecentPhotos';
import AlbumList from '@/components/AlbumList';
import { fetchAlbums, fetchRecentPhotos, generateAlbum, uploadPhoto } from '@/utils/api';
import { Album, Photo } from '@/typing';

const FamilyPhotoAlbum = () => {
  const [recentPhotos, setRecentPhotos] = useState<Photo[]>([]);
  const [albums, setAlbums] = useState<Album[]>([]);

  const fetchLatestPhotos = () => {
    fetchRecentPhotos(8)
      .then(setRecentPhotos)
      .catch(error => console.error('Error fetching recent photos:', error));
  };

  const fetchLatestAlbums = () => {
    fetchAlbums()
    .then(fetchedAlbums => {
      const formattedAlbums = fetchedAlbums.map(album => ({
        id: album.id,
        album_name: album.album_name,
        description: album.description ?? '',
        images: album.images.map(img => ({ id: img.id, url: img.url })),
        cover_image: album.cover_image ? { id: album.cover_image.id, url: album.cover_image.url } : undefined
      }));
      console.log(formattedAlbums[0].images)
      setAlbums(formattedAlbums);
    })
    .catch(error => console.error('Error fetching albums:', error));
};

  useEffect(() => {
    fetchLatestPhotos();
    fetchLatestAlbums();
  }, []);



  const handlePhotoUpload = async (formData: FormData) => {
    try {
      await uploadPhoto(formData);
      fetchLatestPhotos(); // Refetch photos after successful upload
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  const handleAlbumSubmit = async (theme: string) => {
    try {
      console.log("Handling album submit in page.tsx");
      const newAlbum = await generateAlbum(theme);
      setAlbums(prevAlbums => [...prevAlbums, newAlbum]);
    } catch (error) {
      console.error('Error generating album:', error);
    }
  };

  return (
    <div className="container mx-auto p-6 bg-white min-h-screen font-poppins">
      <h1 className="text-4xl font-bold mb-8 text-blue1">Family Photo Album</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <UploadPhoto onUpload={handlePhotoUpload} />
        <GenerateAlbum onSubmit={handleAlbumSubmit} />
      </div>
      
      <RecentPhotos photos={recentPhotos} />
      <AlbumList albums={albums} />
    </div>
  );
};

export default FamilyPhotoAlbum;