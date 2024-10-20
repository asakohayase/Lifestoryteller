from io import BytesIO
from typing import Any, List, Optional
from PIL import Image
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Batch
from langchain.tools import BaseTool
import requests
import torch
from transformers import CLIPProcessor, CLIPModel

from db import generate_presigned_url
from utils.log_config import setup_logger


logger = setup_logger(__name__)

# Qdrant setup
qdrant_client = QdrantClient("localhost", port=6333)
collection_name = "family_book_images"


def ensure_qdrant_collection():
    logger.info("ensure_qdrant_collection() function called")
    try:
        collection_info = qdrant_client.get_collection(collection_name)
        if collection_info.config.params.vectors.size != 512:
            logger.info(
                f"Recreating collection {collection_name} with correct vector size"
            )
            qdrant_client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )
            logger.info(f"Collection {collection_name} checked/created successfully")
        else:
            logger.info(
                f"Collection {collection_name} already exists with correct configuration"
            )
    except Exception as e:
        logger.error(f"Error checking collection: {str(e)}")
        logger.info(f"Attempting to create collection {collection_name}")
        try:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )
            logger.info(f"Collection {collection_name} created successfully")
        except Exception as create_error:
            logger.error(f"Failed to create collection: {str(create_error)}")
            raise


try:
    collection_info = qdrant_client.get_collection(collection_name)
    if collection_info.config.params.vectors.size != 512:
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )
except Exception:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE),
    )


class ImageUploadInput(BaseModel):
    filename: str = Field(..., description="Name of the image file to upload")
    image_id: str = Field(..., description="Unique ID for the image")


class ImageUploadTool(BaseTool):
    name: str = "image_upload"
    description: str = "Processes and stores image embeddings in Qdrant"
    args_schema: type[BaseModel] = ImageUploadInput
    qdrant_client: QdrantClient = Field(
        description="Qdrant client for vector operations"
    )
    model: Any = Field(default=None, description="CLIP model for image processing")
    processor: Any = Field(
        default=None, description="CLIP processor for image preprocessing"
    )

    def __init__(self, qdrant_client):
        super().__init__()
        self.qdrant_client = qdrant_client
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _run(self, filename: str, image_id: str) -> str:
        try:
            with Image.open(filename) as image:
                # Process the image
                inputs = self.processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_embedding = (
                        self.model.get_image_features(**inputs).numpy().tolist()
                    )

            # Store the embedding in Qdrant
            self.qdrant_client.upsert(
                collection_name="family_book_images",
                points=Batch(
                    ids=[image_id],
                    vectors=image_embedding,
                    payloads=[{"image_id": image_id, "filename": filename}],
                ),
            )

            return f"Image uploaded and stored with ID: {image_id}"
        except Exception as e:
            return f"Error uploading image: {str(e)}"


class ImageRetrievalInput(BaseModel):
    text_query: str = Field(None, description="Text description for image retrieval")
    uploaded_image_path: str = Field(None, description="Path to image file for image-based retrieval")

class ImageRetrievalTool(BaseTool):
    name: str = "image_retrieval"
    description: str = "Retrieves similar images based on text descriptions or image input"
    args_schema: type[BaseModel] = ImageRetrievalInput
    qdrant_client: QdrantClient = Field(description="Qdrant client for vector operations")
    model: Any = Field(default=None, description="CLIP model for processing")
    processor: Any = Field(default=None, description="CLIP processor for preprocessing")

    def __init__(self, qdrant_client):
        super().__init__()
        self.qdrant_client = qdrant_client
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        ensure_qdrant_collection()

    def _run(self, text_query: Optional[str] = None, uploaded_image_path: Optional[str] = None) -> List[str]:
        try:
            if text_query:
                logger.info(f"Processing text query: {text_query}")
                inputs = self.processor(text=[text_query], return_tensors="pt", padding=True)
                with torch.no_grad():
                    embedding = self.model.get_text_features(**inputs).numpy().tolist()
            elif uploaded_image_path:
                logger.info(f"Processing image from URL: {uploaded_image_path}")
                
                # Extract the S3 object name from the URL
                s3_object_name = uploaded_image_path.split('com/')[-1]
                
                # Generate a pre-signed URL
                presigned_url = generate_presigned_url(s3_object_name)
                
                response = requests.get(presigned_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                inputs = self.processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    embedding = self.model.get_image_features(**inputs).numpy().tolist()
            else:
                raise ValueError("Either text_query or uploaded_image_path must be provided")
            search_results = self.qdrant_client.search(
                collection_name="family_book_images",
                query_vector=embedding[0],
                limit=20,
                score_threshold=0.2
            )

            for result in search_results:
                logger.info(f"Image ID: {result.payload['image_id']}, Score: {result.score}")

            filtered_results = [
                result.payload["image_id"]
                for result in search_results
                if result.score > 0.2 
            ]

            return filtered_results[:10]  # Return top 10 filtered results
        except requests.RequestException as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in image retrieval: {str(e)}")
            raise

def get_tools(qdrant_client):
    return [ImageUploadTool(qdrant_client), ImageRetrievalTool(qdrant_client)]
