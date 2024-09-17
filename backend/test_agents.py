import os
import sys

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from crew import FamilyBookCrew

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))


def check_api_key():
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )


def setup_qdrant():
    client = QdrantClient("localhost", port=6333)
    collection_name = "family_book_images"
    try:
        client.get_collection(collection_name)
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )
    return client


def load_image_from_dummy_folder(filename):
    dummy_folder = "dummy"
    image_path = os.path.join(dummy_folder, filename)
    with open(image_path, "rb") as image_file:
        return image_file.read()


def test_image_analysis_agent(qdrant_client):
    try:
        print(f"Testing image analysis with qdrant_client: {qdrant_client}")
        image_data = load_image_from_dummy_folder("chako.jpeg")
        crew = FamilyBookCrew("test_job_id", qdrant_client)
        crew.setup_crew(image_data=image_data)
        result = crew.kickoff()
        print("Image Analysis Result:", result)
    except Exception as e:
        print(f"Error in image analysis test: {e}")
        import traceback

        traceback.print_exc()


def test_album_creation_agent(qdrant_client):
    try:
        print(f"Testing album creation with qdrant_client: {qdrant_client}")
        crew = FamilyBookCrew("test_job_id", qdrant_client)
        crew.setup_crew(theme_input="Create an album of dog's photos")
        result = crew.kickoff()
        print("Album Creation Result:", result)
    except Exception as e:
        print(f"Error in album creation test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_api_key()
    qdrant_client = setup_qdrant()
    test_image_analysis_agent(qdrant_client)
    test_album_creation_agent(qdrant_client)
