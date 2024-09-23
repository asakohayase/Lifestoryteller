import { useRef } from 'react';
import { Album } from 'lucide-react';
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface GenerateAlbumProps {
  onSubmit: (theme: string) => Promise<void>;
}

export default function GenerateAlbum({ onSubmit }: GenerateAlbumProps) {
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (formRef.current) {
      const formData = new FormData(formRef.current);
      const theme = formData.get('theme') as string;
      await onSubmit(theme);
      formRef.current.reset();
    }
  };

  return (
    <Card className="bg-white shadow-lg rounded-lg overflow-hidden">
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4 text-blue2">Generate Album</h2>
        <form ref={formRef} className="flex flex-col space-y-3" onSubmit={handleSubmit}>
          <Input
            name="theme"
            type="text"
            placeholder="Enter the Most Epic Theme Ever (Or Just Go With 'Vacation' Again)"
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