"use client"

import React, { useState } from 'react';
import { Upload, Search, Image as ImageIcon } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

const FamilyPhotoAlbum = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [searchResults, setSearchResults] = useState([]);

  return (
    <div className="container mx-auto p-6 bg-white min-h-screen font-poppins">
      <h1 className="text-4xl font-bold mb-8 text-[#1B264F]">Family Photo Album</h1>
      
      <Card className="mb-8 bg-white shadow-lg  rounded-lg overflow-hidden">
        <CardContent className="p-6">
          <h2 className="text-2xl font-semibold mb-4 text-[#274690]">Upload a Photo</h2>
          <div className="grid w-full max-w-sm items-center gap-3">
            <Label htmlFor="picture" className="text-black font-medium">Picture</Label>
            <Input id="picture" type="file" className="bg-white text-black focus:ring-[#274690]" />
          </div>
        </CardContent>
        <CardFooter className="bg-[#F5F3F5] p-4">
          <Button 
            disabled={!uploadedFile} 
            className="bg-[#274690] hover:bg-[#1B264F] text-white font-semibold py-2 px-6 rounded-md transition duration-300 shadow-md"
          >
            <Upload className="mr-2 h-5 w-5" /> Upload
          </Button>
        </CardFooter>
      </Card>
      
      <Card className="mb-8 bg-white shadow-lg  rounded-lg overflow-hidden">
        <CardContent className="p-6">
          <h2 className="text-2xl font-semibold mb-4 text-[#274690]">Search Photos</h2>
          <form className="flex space-x-3">
            <Input
              type="text"
              placeholder="Search by tags (e.g., 'family', 'vacation')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-grow bg-white text-black  focus:ring-[#274690]"
            />
            <Button 
              type="submit"
              className="bg-[#274690] hover:bg-[#1B264F] text-white font-semibold py-2 px-6 rounded-md transition duration-300 shadow-md"
            >
              <Search className="mr-2 h-5 w-5" /> Search
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <div>
        <h2 className="text-2xl font-semibold mb-6 text-[#274690]">Photo Gallery</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300 rounded-lg overflow-hidden">
              <CardContent className="p-4">
                <Dialog>
                  <DialogTrigger asChild>
                    <div className="aspect-w-4 aspect-h-3 mb-3 cursor-pointer bg-[#F5F3F5] rounded-md overflow-hidden">
                      {/* Placeholder for image */}
                      <div className="flex items-center justify-center h-full group">
                        <ImageIcon className="h-16 w-16 text-[#576CA8] group-hover:text-[#274690] transition-colors duration-300" />
                      </div>
                    </div>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px] bg-white rounded-lg">
                    <DialogHeader>
                      <DialogTitle className="text-[#1B264F]">Photo Details</DialogTitle>
                      <DialogDescription className="text-black">
                        View the full-size image and its tags.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      {/* Placeholder for full-size image and tags */}
                    </div>
                  </DialogContent>
                </Dialog>
              </CardContent>
              <CardFooter className="bg-[#F5F3F5] p-4">
                <div className="flex flex-wrap gap-2">
                  {/* Placeholder for tags */}
                  <span className="bg-[#274690] text-white text-xs font-medium px-2.5 py-1 rounded-full">#FamilyTime</span>
                  <span className="bg-[#576CA8] text-white text-xs font-medium px-2.5 py-1 rounded-full">#Memories</span>
                </div>
              </CardFooter>
            </Card>
        </div>
      </div>
    </div>
  );
};

export default FamilyPhotoAlbum;