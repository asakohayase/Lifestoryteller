import logging
import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from crew import FamilyBookCrew
from qdrant_client import QdrantClient

from middleware import add_middleware

app = FastAPI()
qdrant_client = QdrantClient("localhost", port=6333)

add_middleware(app)


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

    # Save the uploaded file temporarily
    temp_file_path = os.path.join(os.getcwd(), f"temp_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"Temporary file saved: {temp_file_path}")
        logger.info(f"File size: {len(content)} bytes")

        crew = FamilyBookCrew("upload_job", qdrant_client)
        # Pass only the filename to setup_crew
        crew.setup_crew(image_data=temp_file_path)
        result = crew.kickoff()

        logger.info(f"Upload processed. Result: {result}")
        return {"imageId": result}

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Temporary file removed: {temp_file_path}")


class AlbumRequest(BaseModel):
    theme: str


@app.post("/generate-album")
async def generate_album(request: AlbumRequest):
    crew = FamilyBookCrew("album_job", qdrant_client)
    crew.setup_crew(theme_input=request.theme)
    result = crew.kickoff()
    return result
