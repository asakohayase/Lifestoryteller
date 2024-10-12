from pydantic import BaseModel
from typing import List, Optional


class Photo(BaseModel):
    id: str
    url: str


class Album(BaseModel):
    id: str
    album_name: str
    description: Optional[str] = None
    cover_image: Optional[Photo] = None
    images: List[Photo]


class AlbumData(BaseModel):
    album_name: str
    description: str
    image_ids: List[str]


class ImageMetadata(BaseModel):
    s3_object_name: str


class ImageDocument(BaseModel):
    metadata: ImageMetadata
