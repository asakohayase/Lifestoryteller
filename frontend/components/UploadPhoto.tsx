import { useRef } from 'react';
import { Upload } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { UploadPhotoProps } from '@/typing';

export default function UploadPhoto({ onUpload, isUploading }: UploadPhotoProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (formRef.current) {
      const formData = new FormData(formRef.current);

      if (fileInputRef.current?.files?.[0]) {
        formData.set('file', fileInputRef.current.files[0]);
      } else {
        console.error('No file selected');
        return;
      }

      try {
        await onUpload(formData);
        formRef.current.reset();
      } catch (error) {
        console.error('Error uploading image:', error);
      }
    }
  };
  
  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <form ref={formRef} onSubmit={handleSubmit}>
        <CardContent className="p-6">
          <Label htmlFor="file" className="text-xl font-semibold mb-4 text-black block">Upload a Photo</Label>
          <Input id="file" name="file" type="file" ref={fileInputRef} className="bg-white text-black focus:ring-blue2" />
        </CardContent>
        <CardFooter className="bg-white1 p-4">
          <Button 
            type="submit"
            className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
            disabled={isUploading}
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
        </CardFooter>
      </form>
    </Card>
  );
}