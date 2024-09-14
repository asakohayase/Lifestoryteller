import { ChangeEvent } from 'react';
import { Upload } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

interface UploadPhotoProps {
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
}

export default function UploadPhoto({ onFileChange }: UploadPhotoProps) {
  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4 text-blue2">Upload a Photo</h2>
        <div className="grid w-full items-center gap-3">
          <Label htmlFor="picture" className="text-black font-medium">Picture</Label>
          <Input id="picture" type="file" className="bg-white text-black focus:ring-blue2" onChange={onFileChange} />
        </div>
      </CardContent>
      <CardFooter className="bg-white1 p-4">
        <Button 
          className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
        >
          <Upload className="mr-2 h-4 w-4" /> Upload
        </Button>
      </CardFooter>
    </Card>
  );
}