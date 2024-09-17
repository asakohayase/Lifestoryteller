import base64
from typing import Any, Dict, List, Union
from PIL import Image
import io
from pydantic import Field
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, ScoredPoint, Record
from langchain.tools import BaseTool
import torch
from transformers import CLIPProcessor, CLIPModel
from qdrant_client.http import models


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


class ImageAnalysisTool(BaseTool):
    name: str = "image_analysis"
    description: str = (
        "Extracts metadata and creates a simple feature vector for an image"
    )
    qdrant_client: QdrantClient = Field(
        description="Qdrant client for vector operations"
    )
    model: Any = Field(default=None, description="CLIP model for image analysis")
    processor: Any = Field(
        default=None, description="CLIP processor for image preprocessing"
    )

    def __init__(self, qdrant_client):
        super().__init__()
        self.qdrant_client = qdrant_client
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _run(self, encoded_image: str):
        try:
            image_data = base64.b64decode(encoded_image)
            image = Image.open(io.BytesIO(image_data))

            # Process the image using the CLIP processor
            inputs = self.processor(images=image, return_tensors="pt")

            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)

            image_embedding = image_features.squeeze().numpy()

            image_id = f"img_{hash(image_data)}"

            self.qdrant_client.upsert(
                collection_name="family_book_images",
                points=[
                    {
                        "id": image_id,
                        "vector": image_embedding.tolist(),
                        "payload": {"image_id": image_id},
                    }
                ],
            )

            return f"Image analyzed and stored with ID: {image_id}"
        except Exception as e:
            return f"Error analyzing image: {str(e)}"


class ThemeBasedImageSearchTool(BaseTool):
    name: str = "vector_store"
    description: str = "Searches for images based on a theme"
    qdrant_client: QdrantClient = Field(
        description="Qdrant client for vector operations"
    )
    model: Any = Field(default=None, description="CLIP model for text encoding")
    processor: Any = Field(
        default=None, description="CLIP processor for text preprocessing"
    )

    def __init__(self, qdrant_client):
        super().__init__()
        self.qdrant_client = qdrant_client
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _run(self, theme: str) -> List[Dict[str, Any]]:
        inputs = self.processor(text=[theme], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        theme_vector = text_features.squeeze().numpy().tolist()

        similar_images: List[ScoredPoint] = self.qdrant_client.search(
            collection_name="family_book_images",
            query_vector=theme_vector,
            limit=10,
        )

        return [
            {
                "image_id": str(hit.id),
                "score": float(hit.score),
                "payload": dict(hit.payload) if hit.payload else None,
            }
            for hit in similar_images
        ]


class DatabaseTool(BaseTool):
    name: str = "database"
    description: str = "Stores, retrieves, and searches image metadata"
    qdrant_client: QdrantClient = Field(
        description="Qdrant client for database operations"
    )

    def __init__(self, qdrant_client: QdrantClient):
        super().__init__()
        self.qdrant_client = qdrant_client

    def _run(
        self, action: str, data: dict
    ) -> Union[str, Dict[str, Any], List[Dict[str, Any]]]:
        if action == "store":
            return self.store_image_metadata(data)
        elif action == "retrieve":
            return self.get_image_metadata(data["id"])
        elif action == "search":
            return self.search_image_metadata(data["query"])
        else:
            raise ValueError("Invalid action. Use 'store', 'retrieve', or 'search'.")

    def store_image_metadata(self, metadata: Dict[str, Any]) -> str:
        self.qdrant_client.upsert(
            collection_name="family_book_images",
            points=[models.PointStruct(id=metadata["id"], payload=metadata)],
        )
        return f"Stored metadata for image {metadata['id']}"

    def get_image_metadata(self, image_id: str) -> Dict[str, Any]:
        result: List[Record] = self.qdrant_client.retrieve(
            collection_name="family_book_images", ids=[image_id]
        )
        return result[0].payload if result else {}

    def search_image_metadata(self, query: str) -> List[Dict[str, Any]]:
        results: List[ScoredPoint] = self.qdrant_client.search(
            collection_name="family_book_images",
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.description", match=models.MatchText(text=query)
                    )
                ]
            ),
            limit=10,
        )
        return [point.payload for point in results]


def get_tools(qdrant_client):
    return [
        ImageAnalysisTool(qdrant_client),
        ThemeBasedImageSearchTool(qdrant_client),
        DatabaseTool(qdrant_client),
    ]
