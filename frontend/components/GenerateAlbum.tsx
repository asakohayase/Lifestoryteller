import { ChangeEvent, FormEvent } from 'react';
import { Album } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface GenerateAlbumProps {
  albumTheme: string;
  onThemeChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export default function GenerateAlbum({ albumTheme, onThemeChange, onSubmit }: GenerateAlbumProps) {
  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4 text-blue2">Generate Album</h2>
        <form className="flex flex-col space-y-3" onSubmit={onSubmit}>
          <Input
            type="text"
            placeholder="Enter the Most Epic Theme Ever (Or Just Go With ‘Vacation’ Again)"
            value={albumTheme}
            onChange={onThemeChange}
            className="bg-white text-black focus:ring-blue2"
          />
          <Button 
            type="submit"
            className="bg-blue2 hover:bg-blue1 text-white font-semibold py-2 px-4 rounded-md transition duration-300 shadow-md"
          >
            <Album className="mr-2 h-4 w-4" /> Generate
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}