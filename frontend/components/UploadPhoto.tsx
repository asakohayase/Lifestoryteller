// components/UploadPhoto.tsx
import React, { useRef, useState } from 'react';
import { Upload } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

interface UploadPhotoProps {
  onUpload: (formData: FormData) => Promise<void>;
  isUploading: boolean;
}

export default function UploadPhoto({ onUpload, isUploading }: UploadPhotoProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileSelected, setFileSelected] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      console.error('No file selected');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      await onUpload(formData);
      if (formRef.current) {
        formRef.current.reset();
      }
      setFileSelected(false);
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFileSelected(event.target.files !== null && event.target.files.length > 0);
  };
  
  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <form ref={formRef} onSubmit={handleSubmit}>
        <CardContent className="p-6">
          <Label htmlFor="file" className="text-xl font-semibold mb-4 text-black block">
            Upload a Photo
          </Label>
          <div className="flex items-center space-x-2">
            <Input 
              id="file" 
              name="file" 
              type="file" 
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className="bg-white text-black focus:ring-blue2 flex-grow" 
            />
            <Button 
              type="submit"
              className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
              disabled={isUploading || !fileSelected}
            >
              {isUploading ? (
                <div className="flex items-center">
                  <div className="animate-pulse bg-gradient-to-r from-gray-300 to-gray-400 h-4 w-4 rounded-full mr-2"></div>
                  Uploading...
                </div>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" /> Upload
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </form>
    </Card>
  );
}