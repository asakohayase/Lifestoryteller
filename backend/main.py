import logging
import os
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
)

from middleware import add_middleware

app = FastAPI()
qdrant_client = QdrantClient("localhost", port=6333)

add_middleware(app)

# MongoDB events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)


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
