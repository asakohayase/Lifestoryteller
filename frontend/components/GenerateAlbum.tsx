import { useRef, useState } from 'react';
import { Album, Upload } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { GenerateAlbumProps } from '@/typing';

export default function GenerateAlbum({ onSubmit, isGenerating }: GenerateAlbumProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (formRef.current) {
      const formData = new FormData(formRef.current);
      const theme = formData.get('theme') as string;
      
      if (!theme && !selectedFile) {
        alert('Please enter a theme or upload an image.');
        return;
      }
  
      const requestFormData = new FormData();
      if (selectedFile) {
        requestFormData.append('image', selectedFile);
      } else if (theme) {
        requestFormData.append('theme', theme);
      }
  
      await onSubmit(requestFormData);
  
      formRef.current.reset();
      setSelectedFile(null);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleGenerateClick = () => {
    formRef.current?.requestSubmit();
  };

  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4 text-black">Generate Album</h2>
        <form ref={formRef} onSubmit={handleSubmit}>
          <Input
            name="theme"
            type="text"
            placeholder="Enter theme or upload an image"
            className="bg-white text-black focus:ring-blue2 mb-2"
          />
          <Input
            name="image"
            type="file"
            onChange={handleFileChange}
            accept="image/*"
            className="bg-white text-black focus:ring-blue2"
          />
        </form>
      </CardContent>
      <CardFooter className="bg-white1 p-4">
        <Button 
          onClick={handleGenerateClick}
          className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
          disabled={isGenerating}
        >
          {isGenerating ? (
            <div className="flex items-center">
              <div className="animate-pulse bg-gradient-to-r from-gray-300 to-gray-400 h-4 w-4 rounded-full mr-2"></div>
              Generating...
            </div>
          ) : (
            <>
              {selectedFile ? <Upload className="mr-2 h-4 w-4" /> : <Album className="mr-2 h-4 w-4" />} Generate
            </>
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
