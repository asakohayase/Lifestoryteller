import logging
import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from crew import FamilyBookCrew
from qdrant_client import QdrantClient
from db import (
    connect_to_mongo,
    close_mongo_connection,
    get_raw_photos,
    save_image,
    save_album,
    get_recent_photos,
    get_albums,
    upload_file_to_s3,
)

from middleware import add_middleware
from contextlib import asynccontextmanager

# app = FastAPI()
qdrant_client = QdrantClient("localhost", port=6333)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    crew = FamilyBookCrew("album_job", qdrant_client)
    crew.setup_crew(theme_input=request.theme)
    result = crew.kickoff()
    # Save album to MongoDB
    album_id = await save_album(
        result["album_name"], result["description"], result["image_ids"]
    )

    return {"albumId": album_id, **result}


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


@app.get("/debug/raw-photos")
async def get_raw_photos_route(limit: int = 10):
    photos = await get_raw_photos(limit)
    return JSONResponse(content={"photos": photos})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
