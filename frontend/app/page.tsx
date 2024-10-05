"use client";

import React, { useEffect, useState } from 'react';
import UploadPhoto from '@/components/UploadPhoto';
import GenerateAlbum from '@/components/GenerateAlbum';
import RecentPhotos from '@/components/RecentPhotos';
import AlbumList from '@/components/AlbumList';
import { fetchRecentPhotos, generateAlbum, uploadPhoto } from '@/utils/api';
import { Photo } from '@/typing';

const FamilyPhotoAlbum = () => {
  const [recentPhotos, setRecentPhotos] = useState<Photo[]>([]);
  const [albums, setAlbums] = useState<{ album_name: string; photoCount: number }[]>([]);

  const fetchLatestPhotos = () => {
    fetchRecentPhotos(8)
      .then(setRecentPhotos)
      .catch(error => console.error('Error fetching recent photos:', error));
  };

  useEffect(() => {
    fetchLatestPhotos();
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
      const result = await generateAlbum(theme);
      if (result.album_name && result.image_ids) {
        setAlbums(prevAlbums => [...prevAlbums, { album_name: result.album_name, photoCount: result.image_ids.length }]);
      } else {
        console.error("Unexpected album generation result:", result);
      }
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