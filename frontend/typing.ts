export interface Photo {
    id: string;
    url: string;
  }

export interface UploadPhotoProps {
    onUpload: (formData: FormData) => Promise<void>;
  }

export interface Album {
    album_name: string;
    photoCount: number;
  }
  
export interface AlbumListProps {
    albums: Album[];
  }
  