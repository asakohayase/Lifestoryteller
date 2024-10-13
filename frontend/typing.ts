export interface Photo {
    id: string;
    url: string;
  }

  export interface UploadPhotoProps {
    onUpload: (formData: FormData) => Promise<void>;
    isUploading: boolean;
  }

  export interface RecentPhotoProps {
    photos: Photo[];
  }

  export interface GenerateAlbumProps {
    onSubmit: (theme: string) => Promise<void>;
    isGenerating: boolean;
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
  