import json

from typing import Any, Dict, List, Optional
import uuid
from fastapi import BackgroundTasks, FastAPI, HTTPException,  UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils.log_config import setup_logger
from tools import ensure_qdrant_collection
from crew import FamilyBookCrew
from qdrant_client import QdrantClient
from db import (
    connect_to_mongo,
    close_mongo_connection,
    create_video,
    delete_multiple_albums,
    delete_multiple_photos,
    generate_album_with_presigned_urls,
    generate_presigned_url,
    get_album_by_id,
    get_all_albums,
    get_all_photos,
    get_recent_albums,
    save_image,
    get_recent_photos,
    upload_file_to_s3,
)
from crewai.crews.crew_output import CrewOutput

from middleware import add_middleware
from contextlib import asynccontextmanager
from qdrant_client.http.models import ScrollRequest


qdrant_client = QdrantClient("localhost", port=6333)

logger = setup_logger(__name__)


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
async def generate_album(image: Optional[UploadFile] = File(None), theme: Optional[str] = Form(None)):  
    try:
        if not image and not theme:
            logger.error("Neither image nor theme provided")
            raise HTTPException(status_code=400, detail="Either image or theme must be provided")

        uploaded_image_path = None
        if image:
            # Save the uploaded file
            contents = await image.read()
            file_path = f"/tmp/{image.filename}"
            with open(file_path, "wb") as f:
                f.write(contents)

            # Generate a single UUID for S3
            image_id = str(uuid.uuid4())

            # Generate S3 object name and upload to S3
            s3_object_name = f"generated-album/{image_id}-{image.filename}"
            s3_url = upload_file_to_s3(file_path, s3_object_name)

            if not s3_url:
                logger.error("Failed to upload to S3")
                raise HTTPException(status_code=500, detail="Failed to upload image to S3")

            uploaded_image_path = s3_url
            logger.info(f"Image uploaded to S3: {uploaded_image_path}")

        crew = FamilyBookCrew("album_job", qdrant_client)

        if uploaded_image_path:
            logger.info(f"Processing image-based album generation: {uploaded_image_path}")
            crew.setup_crew(uploaded_image_path=uploaded_image_path)
        else:
            logger.info(f"Processing theme-based album generation: {theme}")
            crew.setup_crew(theme_input=theme)
        
        result = crew.kickoff()
        logger.info(f"Crew result type: {type(result)}")
        logger.info(f"Crew result: {result}")

        if isinstance(result, CrewOutput):
            try:
                album_data = json.loads(result.raw)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error: {str(json_error)}")
                logger.error(f"Raw result: {result.raw}")
                # Attempt to clean and parse the JSON
                cleaned_result = result.raw.replace("'", '"').strip()
                try:
                    album_data = json.loads(cleaned_result)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse crew result as JSON: {result.raw}")
        elif isinstance(result, str):
            try:
                album_data = json.loads(result)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error: {str(json_error)}")
                logger.error(f"Raw result: {result}")
                # Attempt to clean and parse the JSON
                cleaned_result = result.replace("'", '"').strip()
                try:
                    album_data = json.loads(cleaned_result)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to parse crew result as JSON: {result}")
        elif isinstance(result, dict):
            album_data = result
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            raise ValueError(f"Unexpected result format from album generation: {result}")

        # Validate album_data
        required_keys = ["album_name", "description", "image_ids"]
        if not all(key in album_data for key in required_keys):
            missing_keys = [key for key in required_keys if key not in album_data]
            raise ValueError(f"Invalid album data format: missing keys {missing_keys}")

        # Generate album with presigned URLs
        album_with_urls = await generate_album_with_presigned_urls(album_data)

        return JSONResponse(content=album_with_urls)
    except Exception as e:
        logger.error(f"Error generating album: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/all-photos")
async def get_all_photos_route(skip: int = 0, limit: int = 100):
    photos = await get_all_photos(skip, limit)
    return {"photos": photos}

@app.get("/recent-photos")
async def get_recent_photos_route(limit: int = 4):
    try:
        photos = await get_recent_photos(limit)
        return {"photos": photos}
    except Exception as e:
        print(f"Error fetching recent photos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/all-albums")
async def get_all_albums_route(skip: int = 0, limit: int = 100):
    try:
        albums = await get_all_albums(skip, limit)
        for album in albums:
            if 'images' not in album or not album['images']:
                logger.warning(f"Album {album['id']} has no images")
        return {"albums": albums}
    except Exception as e:
        print(f"Error fetching all albums: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-albums")
async def get_recent_albums_route(limit: int = 4):
    try:
        albums = await get_recent_albums(limit)
        return {"albums": json.loads(json.dumps(albums, default=str))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/albums/{album_id}")
async def get_album(album_id: str):
    logger.debug(f"Received request for album ID: {album_id}")
    try:
        album = await get_album_by_id(album_id)
        if album is None:
            raise HTTPException(status_code=404, detail="Album not found")
        return album
    except Exception as e:
        logger.error(f"Error processing request for album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate-video/{album_id}")
async def generate_video(album_id: str, background_tasks: BackgroundTasks):
    album = await get_album_by_id(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    background_tasks.add_task(create_video, album)
    return {"message": "Video generation started", "album_id": album_id}
    
@app.get("/download-video/{album_id}")
async def get_video_download_url(album_id: str):
    try:
        album = await get_album_by_id(album_id)
        if not album or not album.get("video_url"):
            raise HTTPException(status_code=404, detail="Video not found")

        # Extract the S3 key from the stored URL
        s3_key = album["video_url"].split("/")[-1].split("?")[0]
        
        # Generate a new presigned URL for downloading
        download_url = generate_presigned_url(s3_key, expiration=3600, as_attachment=True)
        
        return {"download_url": download_url}
    except Exception as e:
        logger.error(f"Error generating download URL for album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    

@app.delete("/photos/{image_id}")
async def delete_photo_route(image_id: str):
    result = await delete_multiple_photos([image_id])
    if result["successful"]:
        return {"message": f"Photo {image_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Photo not found or could not be deleted")

@app.delete("/albums/{album_id}")
async def delete_album_route(album_id: str):
    result = await delete_multiple_albums([album_id])
    if result["successful"]:
        return {"message": f"Album {album_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Album not found or could not be deleted")

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

# Clear all data from Qdrant, MongoDB, and S3
# @app.post("/admin/clear-all-data")
# async def clear_all_data():
#     await clear_all_images()
#     clear_qdrant_collection("family_book_images")
#     return {"message": "All data has been cleared"}

# Retrieve data stored in Qdrant
@app.get("/qdrant-data")
async def get_all_qdrant_data() -> List[Dict[str, Any]]:
    try:
        qdrant_client = QdrantClient("localhost", port=6333)
        
        all_data = []
        offset = None
        limit = 100  # Number of records to fetch per request
        
        while True:
            results = qdrant_client.scroll(
                collection_name="family_book_images",
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=True  # Explicitly request vectors
            )
            
            if not results or not results[0]:
                break
            
            points, next_page_offset = results
            
            for point in points:
                vector_info = "Not available"
                if point.vector:
                    vector_info = f"First 5 elements: {point.vector[:5]}, Length: {len(point.vector)}"
                else:
                    vector_info = "Vector is null"
                
                all_data.append({
                    "id": point.id,
                    "payload": point.payload,
                    "vector_info": vector_info
                })
            
            if next_page_offset is None:
                break
            
            offset = next_page_offset

        return all_data if all_data else {"message": "No data found in the 'family_book_images' collection."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data from Qdrant: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
