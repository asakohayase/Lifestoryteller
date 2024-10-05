export interface Photo {
    id: string;
    url: string;
  }

export interface UploadPhotoProps {
    onUpload: (formData: FormData) => Promise<void>;
  }