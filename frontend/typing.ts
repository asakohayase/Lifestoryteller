export interface Photo {
    id: string;
    url: string;
  }

export interface UploadPhotoProps {
    onUpload: (formData: FormData) => Promise<void>;
  }

  export interface Album {
    id: string;
    album_name: string;
    description?: string;
    cover_image?: Photo;
    images: Photo[];
  }
  
export interface AlbumListProps {
    albums: Album[];
  }
  