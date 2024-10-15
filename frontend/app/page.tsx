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
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchLatestPhotos = () => {
    fetchRecentPhotos(8)
      .then(setRecentPhotos)
      .catch(error => console.error('Error fetching recent photos:', error))
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
        setAlbums(formattedAlbums);
      })
      .catch(error => console.error('Error fetching albums:', error))
  };

  useEffect(() => {
    fetchLatestPhotos();
    fetchLatestAlbums();
  }, []);



  const handlePhotoUpload = async (formData: FormData) => {
    setIsUploading(true);
    try {
      await uploadPhoto(formData);
      fetchLatestPhotos();
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAlbumSubmit = async (theme: string) => {
    setIsGenerating(true);
    try {
      const newAlbum = await generateAlbum(theme);
      setAlbums(prevAlbums => [...prevAlbums, newAlbum]);
    } catch (error) {
      console.error('Error generating album:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-full py-8 px-12 lg:px-24 bg-white min-h-screen font-poppins">
      <div className="bg-white rounded-lg mb-8 p-4">
        <h1 className="text-4xl font-extrabold text-gray-800 text-center tracking-tight">LifeStoryteller</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <UploadPhoto onUpload={handlePhotoUpload} isUploading={isUploading} />
        <GenerateAlbum onSubmit={handleAlbumSubmit} isGenerating={isGenerating} />
      </div>
      
      <RecentPhotos photos={recentPhotos} onPhotoDeleted={fetchLatestPhotos} />
      <AlbumList albums={albums} onAlbumsDeleted={fetchLatestAlbums} />
    </div>
  );
};

export default FamilyPhotoAlbum;