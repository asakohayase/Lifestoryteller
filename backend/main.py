import json
import logging
from typing import List
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from tools import ensure_qdrant_collection
from crew import FamilyBookCrew
from qdrant_client import QdrantClient
from db import (
    connect_to_mongo,
    close_mongo_connection,
    delete_multiple_albums,
    delete_multiple_photos,
    generate_album_with_presigned_urls,
    get_album_by_id,
    save_image,
    get_recent_photos,
    get_albums,
    upload_file_to_s3,
)
from crewai.crews.crew_output import CrewOutput

from middleware import add_middleware
from contextlib import asynccontextmanager

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
    ensure_qdrant_collection()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()


app = FastAPI(lifespan=lifespan)

add_middleware(app)

class BulkDeletePhotosRequest(BaseModel):
    photo_ids: List[str]

class BulkDeleteAlbumsRequest(BaseModel):
    album_ids: List[str]


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Save the uploaded file
    contents = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)

    # Generate a single UUID for both Qdrant and MongoDB
    image_id = str(uuid.uuid4())

    # Generate S3 object name and upload to S3
    s3_object_name = f"{image_id}-{file.filename}"
    s3_url = upload_file_to_s3(file_path, s3_object_name)

    if s3_url:
        metadata = {
            "image_id": image_id,
            "original_filename": file.filename,
            "s3_url": s3_url,
            "s3_object_name": s3_object_name,
        }

        # Save metadata to MongoDB
        mongo_result = await save_image(image_id, file_path, metadata)
        if not mongo_result:
            print("Failed to save image metadata to MongoDB")
            return {"error": "Failed to save image metadata"}

        # Process with FamilyBookCrew
        crew = FamilyBookCrew("upload_job", qdrant_client)
        crew.setup_crew(image_data=file_path, image_id=image_id)
        crew_result = crew.kickoff()

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

        if isinstance(result, CrewOutput):
            album_data = parse_string_to_dict(result.raw)
        elif isinstance(result, dict):
            album_data = result
        elif isinstance(result, str):
            album_data = parse_string_to_dict(result)
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            raise ValueError("Unexpected result format from album generation")
        if not isinstance(album_data, dict):
            raise ValueError("Invalid album data format: not a dictionary")

        required_keys = ["album_name", "description", "image_ids"]
        missing_keys = [key for key in required_keys if key not in album_data]
        if missing_keys:
            raise ValueError(f"Invalid album data format: missing keys {missing_keys}")

        # Generate album with presigned URLs
        album_with_urls = await generate_album_with_presigned_urls(album_data)

        return album_with_urls
    except Exception as e:
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
    try:
        albums = await get_albums()
        return {"albums": json.loads(json.dumps(albums, default=str))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/albums/{album_id}")
async def get_album(album_id: str):
    logging.debug(f"Received request for album ID: {album_id}")
    try:
        album = await get_album_by_id(album_id)
        if album is None:
            raise HTTPException(status_code=404, detail="Album not found")
        return album
    except Exception as e:
        logging.error(f"Error processing request for album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.delete("/photos/{image_id}")
# async def delete_photo_route(image_id: str):
#     result = await delete_multiple_photos([image_id])
#     if result["successful"]:
#         return {"message": f"Photo {image_id} deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Photo not found or could not be deleted")

# @app.delete("/albums/{album_id}")
# async def delete_album_route(album_id: str):
#     result = await delete_multiple_albums([album_id])
#     if result["successful"]:
#         return {"message": f"Album {album_id} deleted successfully"}
#     else:
#         raise HTTPException(status_code=404, detail="Album not found or could not be deleted")

@app.post("/photos/bulk-delete")
async def bulk_delete_photos(request: BulkDeletePhotosRequest):
    try:   
        result = await delete_multiple_photos(request.photo_ids)
        return {
            "message": f"Deleted {len(result['successful'])} photos successfully",
            "successful": result['successful'],
            "failed": result['failed']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/albums/bulk-delete")
async def bulk_delete_albums(request: BulkDeleteAlbumsRequest):
    try:
        result = await delete_multiple_albums(request.album_ids)
        return {
        "message": f"Deleted {len(result['successful'])} albums successfully",
        "successful": result["successful"],
        "failed": result["failed"]
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.post("/admin/clear-all-data")
# async def clear_all_data():
#     await clear_all_images()
#     clear_qdrant_collection("family_book_images")
#     return {"message": "All data has been cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
