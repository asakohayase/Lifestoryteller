"use client"

import React, { ChangeEvent, FormEvent, useState } from 'react';
import UploadPhoto from '@/components/UploadPhoto';
import GenerateAlbum from '@/components/GenerateAlbum';
import RecentPhotos from '@/components/RecentPhotos';
import AlbumList from '@/components/AlbumList';

const FamilyPhotoAlbum = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [albumTheme, setAlbumTheme] = useState('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      // setUploadedFile(e.target.files[0]);
    }
  };
  
  const handleThemeChange = (e: ChangeEvent<HTMLInputElement>) => setAlbumTheme(e.target.value);
  
  const handleAlbumSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle album generation logic here
  };

  // Placeholder data
  const recentPhotos = Array(4).fill(null);
  const albums = [
    { name: "Summer Vacation", photoCount: 10 },
    { name: "Family Reunion", photoCount: 6 },
    { name: "Christmas 2023", photoCount: 8 },
    { name: "Baby's First Year", photoCount: 9 },
  ];

  return (
    <div className="container mx-auto p-6 bg-white min-h-screen font-poppins">
      <h1 className="text-4xl font-bold mb-8 text-blue1">Family Photo Album</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <UploadPhoto onFileChange={handleFileChange} />
        <GenerateAlbum 
          albumTheme={albumTheme} 
          onThemeChange={handleThemeChange}
          onSubmit={handleAlbumSubmit}
        />
      </div>
      
      <RecentPhotos photos={recentPhotos} />
      <AlbumList albums={albums} />
    </div>
  );
};

export default FamilyPhotoAlbum;