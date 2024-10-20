export interface Photo {
    id: string;
    url: string;
    createdAt: string;
  }

  export interface UploadPhotoProps {
    onUpload: (formData: FormData) => Promise<void>;
    isUploading: boolean;
  }

  export interface RecentPhotoProps {
    photos: Photo[];
    onPhotoDeleted: () => void 
  }

  export interface GenerateAlbumProps {
    onSubmit: (data: FormData) => Promise<void>;
    isGenerating: boolean;
  }

  export interface Album {
    id: string;
    album_name: string;
    description?: string;
    cover_image?: Photo;
    images: Photo[];
    createdAt: string;
  }
  
export interface AlbumListProps {
    albums: Album[];
    onAlbumsDeleted: () => void;
  }
  