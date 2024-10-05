import logging
import os
from typing import Any, List
import uuid
from PIL import Image
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Batch
from langchain.tools import BaseTool
import torch
from transformers import CLIPProcessor, CLIPModel
from qdrant_client.http import models


logger = logging.getLogger(__name__)

# Qdrant setup
qdrant_client = QdrantClient("localhost", port=6333)
collection_name = "family_book_images"

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

    def _run(self, filename: str) -> str:
        try:
            # Load the image file
            image_path = os.path.join("dummy", filename)
            with Image.open(image_path) as image:
                # Process the image
                inputs = self.processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_embedding = (
                        self.model.get_image_features(**inputs).numpy().tolist()
                    )

            # Generate a unique ID for the image
            image_id = str(uuid.uuid4())

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
    text_query: str = Field(..., description="Text description for image retrieval")


class ImageRetrievalTool(BaseTool):
    name: str = "image_retrieval"
    description: str = "Retrieves similar images based on text descriptions"
    args_schema: type[BaseModel] = ImageRetrievalInput
    qdrant_client: QdrantClient = Field(
        description="Qdrant client for vector operations"
    )
    model: Any = Field(default=None, description="CLIP model for text processing")
    processor: Any = Field(
        default=None, description="CLIP processor for text preprocessing"
    )

    def __init__(self, qdrant_client):
        super().__init__()
        self.qdrant_client = qdrant_client
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _run(self, text_query: str) -> List[str]:
        try:
            inputs = self.processor(
                text=[text_query], return_tensors="pt", padding=True
            )

            with torch.no_grad():
                text_embedding = self.model.get_text_features(**inputs).numpy().tolist()

            search_results = self.qdrant_client.search(
                collection_name="family_book_images",
                query_vector=text_embedding[0],
                limit=10,
            )

            return [result.payload["image_id"] for result in search_results]
        except Exception as e:
            logger.error(f"Error retrieving images: {str(e)}", exc_info=True)
            return []


def get_tools(qdrant_client):
    return [ImageUploadTool(qdrant_client), ImageRetrievalTool(qdrant_client)]
