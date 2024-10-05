import json
import logging
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from crew import FamilyBookCrew
from qdrant_client import QdrantClient
from db import (
    connect_to_mongo,
    close_mongo_connection,
    save_image,
    save_album,
    get_recent_photos,
    get_albums,
    upload_file_to_s3,
)
from crewai.crews.crew_output import CrewOutput

from middleware import add_middleware
from contextlib import asynccontextmanager

# app = FastAPI()
qdrant_client = QdrantClient("localhost", port=6333)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_string_to_dict(s: str) -> dict:
    try:
        # First, try to parse it as JSON
        return json.loads(s)
    except json.JSONDecodeError:
        # If JSON parsing fails, use a custom parsing method
        # Remove leading/trailing whitespace and newlines
        s = s.strip()
        # Remove the outer curly braces if present
        s = s.strip("{}")
        # Split the string into key-value pairs
        pairs = [pair.split(":", 1) for pair in s.split('",')]
        # Convert to dictionary
        result = {}
        for key, value in pairs:
            key = key.strip().strip('"')
            value = value.strip().strip('"')
            if value.startswith("[") and value.endswith("]"):
                # Handle list values
                value = [v.strip().strip('"') for v in value[1:-1].split(",")]
            result[key] = value
        return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)

add_middleware(app)


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")

    # Save the uploaded file
    contents = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info(f"File saved: {file_path}")

    # Generate S3 object name and upload to S3
    s3_object_name = f"{uuid.uuid4()}-{file.filename}"
    s3_url = upload_file_to_s3(file_path, s3_object_name)

    if s3_url:
        metadata = {
            "original_filename": file.filename,
            "s3_url": s3_url,
            "s3_object_name": s3_object_name,
        }

        # Process with FamilyBookCrew
        crew = FamilyBookCrew("upload_job", qdrant_client)
        crew.setup_crew(image_data=file_path)
        crew_result = crew.kickoff()

        # Save image metadata to MongoDB
        image_id = await save_image(file_path, metadata)

        logger.info(
            f"Upload processed. Crew Result: {crew_result}, Image ID: {image_id}"
        )
        return {"image_id": image_id, "s3_url": s3_url, "crew_result": crew_result}
    else:
        logger.error("Failed to upload to S3")
        return {"error": "Failed to upload to S3"}


class AlbumRequest(BaseModel):
    theme: str


@app.post("/generate-album")
async def generate_album(request: AlbumRequest):
    try:
        crew = FamilyBookCrew("album_job", qdrant_client)
        crew.setup_crew(theme_input=request.theme)
        result = crew.kickoff()

        logger.debug(f"Raw result type: {type(result)}")
        logger.debug(f"Raw result content: {result}")

        if isinstance(result, CrewOutput):
            logger.debug(f"CrewOutput raw type: {type(result.raw)}")
            logger.debug(f"CrewOutput raw content: {result.raw}")
            album_data = parse_string_to_dict(result.raw)
        elif isinstance(result, dict):
            album_data = result
        elif isinstance(result, str):
            album_data = parse_string_to_dict(result)
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            raise ValueError("Unexpected result format from album generation")

        logger.debug(f"Album data type after processing: {type(album_data)}")
        logger.debug(f"Album data content after processing: {album_data}")

        # Ensure album_data is a dictionary and has all required keys
        if not isinstance(album_data, dict):
            logger.error(f"Album data is not a dictionary: {album_data}")
            raise ValueError("Invalid album data format: not a dictionary")

        required_keys = ["album_name", "description", "image_ids"]
        missing_keys = [key for key in required_keys if key not in album_data]
        if missing_keys:
            logger.error(f"Missing keys in album data: {missing_keys}")
            raise ValueError(f"Invalid album data format: missing keys {missing_keys}")

        album_id = await save_album(
            album_data["album_name"], album_data["description"], album_data["image_ids"]
        )
        logger.info(f"Album saved successfully with ID: {album_id}")
        return {"albumId": album_id, **album_data}
    except Exception as e:
        logger.exception(f"Error in generate_album: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recent-photos")
async def get_recent_photos_route(limit: int = 8):
    try:
        photos = await get_recent_photos(limit)
        return {"photos": photos}
    except Exception as e:
        print(f"Error fetching recent photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/albums")
async def get_albums_route():
    albums = await get_albums()
    return {"albums": albums}


# @app.post("/admin/clear-all-data")
# async def clear_all_data():
#     await clear_all_images()
#     clear_qdrant_collection("family_book_images")
#     return {"message": "All data has been cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
