import { useRef } from 'react';
import { Upload } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { uploadPhoto } from '@/utils/api';

// interface UploadPhotoProps {
//   onUpload: (formData: FormData) => Promise<void>;
// }

// export default function UploadPhoto({ onUpload }: UploadPhotoProps) {
//   const formRef = useRef<HTMLFormElement>(null);
//   const fileInputRef = useRef<HTMLInputElement>(null);

//   const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
//     event.preventDefault();
//     if (formRef.current) {
//       const formData = new FormData(formRef.current);

//        // Log FormData contents
//        console.log('FormData contents (UploadPhoto):');
//        formData.forEach((value, key) => {
//          console.log(key, typeof value, value instanceof File ? value.name : value);
//        });
 
//        if (fileInputRef.current?.files?.[0]) {
//          formData.set('file', fileInputRef.current.files[0]);
//        } else {
//          console.error('No file selected');
//          return;
//        }

//       await onUpload(formData);
//       formRef.current.reset();
//     }
//   };


interface UploadPhotoProps {
  onUpload: (imageId: string) => void;
}

export default function UploadPhoto({ onUpload }: UploadPhotoProps) {
  const formRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (formRef.current) {
      const formData = new FormData(formRef.current);

      console.log('FormData contents (UploadPhoto):');
      formData.forEach((value, key) => {
        console.log(key, typeof value, value instanceof File ? value.name : value);
      });

      if (fileInputRef.current?.files?.[0]) {
        formData.set('file', fileInputRef.current.files[0]);
      } else {
        console.error('No file selected');
        return;
      }

      try {
        const result = await uploadPhoto(formData);
        if (result.imageId && result.imageId.raw) {
          onUpload(result.imageId.raw);
        } else {
          console.error("No imageId in response:", result);
        }
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
          <h2 className="text-xl font-semibold mb-4 text-blue2">Upload a Photo</h2>
          <div className="grid w-full items-center gap-3">
            <Label htmlFor="file" className="text-black font-medium">Picture</Label>
            <Input  id="file"  name="file" type="file"  ref={fileInputRef} className="bg-white text-black focus:ring-blue2" />
          </div>
        </CardContent>
        <CardFooter className="bg-white1 p-4">
          <Button 
            type="submit"
            className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
          >
            <Upload className="mr-2 h-4 w-4" /> Upload
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}