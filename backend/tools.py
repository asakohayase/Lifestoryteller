from PIL import Image
import io
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Qdrant setup
qdrant_client = QdrantClient("localhost", port=6333)
collection_name = "family_book_images"

# Ensure the collection exists
try:
    qdrant_client.get_collection(collection_name)
except:
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=256, distance=Distance.COSINE),
    )


class ImageAnalysisTool:
    name: str = "image_analysis"
    description: str = (
        "Extracts metadata and creates a simple feature vector for an image"
    )

    def analyze_image(self, image_data: bytes) -> dict:
        img = Image.open(io.BytesIO(image_data))
        exif_data = img._getexif() if hasattr(img, "_getexif") else None
        img_gray = img.convert("L").resize((16, 16))
        feature_vector = np.array(img_gray).flatten() / 255.0

        return {
            "width": img.width,
            "height": img.height,
            "exif_data": exif_data,
            "feature_vector": feature_vector.tolist(),
        }


class VectorStoreTool:
    name: str = "vector_store"
    description: str = "Stores image vectors for similarity search"

    def store_vector(self, image_id: str, vector: list[float]) -> str:
        qdrant_client.upsert(
            collection_name=collection_name, points=[{"id": image_id, "vector": vector}]
        )
        return f"Vector stored for image {image_id}"

    def search_similar(self, query_vector: list[float], limit: int = 10) -> list[str]:
        search_result = qdrant_client.search(
            collection_name=collection_name, query_vector=query_vector, limit=limit
        )
        return [hit.id for hit in search_result]


class DatabaseTool:
    name: str = "database"
    description: str = "Stores and retrieves image metadata"

    def store_image_metadata(self, metadata: dict) -> str:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[{"id": metadata["id"], "payload": metadata}],
        )
        return metadata["id"]

    def get_image_metadata(self, image_id: str) -> dict:
        result = qdrant_client.retrieve(collection_name=collection_name, ids=[image_id])
        return result[0].payload if result else None


def get_tools():
    return [ImageAnalysisTool(), VectorStoreTool(), DatabaseTool()]
