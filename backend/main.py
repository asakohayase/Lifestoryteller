import logging
import os
import uuid
from fastapi import FastAPI, UploadFile, File
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

from middleware import add_middleware
from contextlib import asynccontextmanager

# app = FastAPI()
qdrant_client = QdrantClient("localhost", port=6333)

# add_middleware(app)

# MongoDB events
# app.add_event_handler("startup", connect_to_mongo)
# app.add_event_handler("shutdown", close_mongo_connection)


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
    contents = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)

    s3_object_name = f"{uuid.uuid4()}-{file.filename}"
    s3_url = upload_file_to_s3(file_path, s3_object_name)

    if s3_url:
        metadata = {
            "original_filename": file.filename,
            "s3_url": s3_url,
            "s3_object_name": s3_object_name,
        }
        image_id = await save_image(file.filename, metadata)
        return {"image_id": image_id, "s3_url": s3_url}
    else:
        return {"error": "Failed to upload to S3"}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Files in current directory: {os.listdir()}")
    logger.info(
        f"Files in 'temp' directory: {os.listdir('temp') if os.path.exists('temp') else 'temp directory does not exist'}"
    )

    # Save the uploaded file
    file_path = os.path.join("uploads", file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    logger.info(f"File saved: {file_path}")

    crew = FamilyBookCrew("upload_job", qdrant_client)
    # Pass only the filename to setup_crew
    crew.setup_crew(image_data=file_path)
    result = crew.kickoff()

    # Save image metadata to MongoDB
    image_id = await save_image(file_path, {"original_filename": file.filename})

    logger.info(f"Upload processed. Result: {result}")
    return {"imageId": result}


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

    # return result


@app.get("/recent-photos")
async def get_recent_photos_route(limit: int = 10):
    photos = await get_recent_photos(limit)
    return {"photos": photos}


@app.get("/albums")
async def get_albums_route():
    albums = await get_albums()
    return {"albums": albums}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
