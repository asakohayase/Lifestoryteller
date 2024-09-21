import os
import sys
import base64
from typing import List, Dict, Any, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http.models import models
from crew import FamilyBookCrew

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def setup_qdrant() -> QdrantClient:
    client = QdrantClient("localhost", port=6333)
    collection_name = "family_book_images"
    try:
        collection_info = client.get_collection(collection_name)
        if (
            collection_info.config.params.vectors.size != 512
            or not collection_info.config.params.on_disk_payload
        ):
            client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=512, distance=models.Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(memmap_threshold=10000),
                on_disk_payload=True,
            )
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=512, distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(memmap_threshold=10000),
            on_disk_payload=True,
        )
    return client


def load_image_from_dummy_folder(filename: str) -> bytes:
    dummy_folder = "dummy"
    image_path = os.path.join(dummy_folder, filename)
    with open(image_path, "rb") as image_file:
        return image_file.read()


def load_all_images_from_dummy_folder() -> List[Tuple[str, str]]:
    dummy_folder = "dummy"
    images = []
    for filename in os.listdir(dummy_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            image_data = load_image_from_dummy_folder(filename)
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            images.append((filename, encoded_image))
    return images


def list_uploaded_images(
    qdrant_client: QdrantClient, collection_name: str = "family_book_images"
) -> List[Dict[str, Any]]:
    uploaded_images = []
    offset = None
    while True:
        response = qdrant_client.scroll(
            collection_name=collection_name, limit=100, offset=offset
        )
        for point in response[0]:
            if point.payload:
                image_info = {"id": point.id, "payload": point.payload}
                uploaded_images.append(image_info)
        if len(response[0]) < 100:
            break
        offset = response[1]
    return uploaded_images


def check_api_key() -> None:
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )


def test_image_upload(qdrant_client: QdrantClient) -> None:
    try:
        print(f"Testing image upload with qdrant_client: {qdrant_client}")
        dummy_folder = "dummy"
        crew = FamilyBookCrew("test_job_id", qdrant_client)

        for filename in os.listdir(dummy_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                print(f"Uploading image: {filename}")
                try:
                    crew.setup_crew(image_data=filename)
                    result = crew.kickoff()
                    print(f"Image Upload Result for {filename}:", result)
                except Exception as e:
                    print(f"Error uploading image {filename}: {e}")
                    import traceback

                    traceback.print_exc()

    except Exception as e:
        print(f"Error in image upload test: {e}")
        import traceback

        traceback.print_exc()


def test_album_creation(qdrant_client: QdrantClient) -> None:
    try:
        print(f"Testing album creation with qdrant_client: {qdrant_client}")
        crew = FamilyBookCrew("test_job_id", qdrant_client)
        crew.setup_crew(theme_input="Create an album of Japanese food photos")
        result = crew.kickoff()
        print("Album Creation Result:", result)
    except Exception as e:
        print(f"Error in album creation test: {e}")
        import traceback

        traceback.print_exc()


def test_list_uploaded_images(qdrant_client: QdrantClient) -> None:
    try:
        print("Listing all uploaded images:")
        uploaded_images: List[Dict[str, Any]] = list_uploaded_images(qdrant_client)
        for img in uploaded_images:
            print(f"ID: {img['id']}, Payload: {img['payload']}")
    except Exception as e:
        print(f"Error listing uploaded images: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_api_key()
    qdrant_client: QdrantClient = setup_qdrant()

    test_image_upload(qdrant_client)
    test_album_creation(qdrant_client)
    test_list_uploaded_images(qdrant_client)
