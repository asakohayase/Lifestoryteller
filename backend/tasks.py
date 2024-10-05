import logging
from crewai import Task, Agent
from textwrap import dedent

from utils.job_manager import append_event
from utils.log_config import setup_logger

from tools import ImageRetrievalTool, ImageUploadTool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FamilyBookTasks:
    def __init__(self, job_id, qdrant_client):
        self.job_id = job_id
        self.qdrant_client = qdrant_client
        self.logger = setup_logger(__name__)

    def append_event_callback(self, task_output):
        self.logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output)

    def upload_image_task(self, agent: Agent, filename: str):
        return Task(
            description=dedent(
                f"""
                Process and upload the image file: {filename}
                Use the ImageUploadTool to process and store the image.
                """
            ),
            agent=agent,
            expected_output="The ID of the uploaded image.",
            tools=[ImageUploadTool(self.qdrant_client)],
            async_execution=False,
            callback=self.append_event_callback,
        )

    def create_album_task(self, agent: Agent, theme_input: str):
        return Task(
            description=dedent(
                f"""
                Create an album based on the user's natural language input: "{theme_input}"
                Use the ImageRetrievalTool to find similar images based on the theme.
                Select a maximum of 10 relevant images for the album.
                If fewer than 10 relevant images are found, do not attempt to fill the remaining spots.
                """
            ),
            agent=agent,
            expected_output=dedent(
                """
                {
                    "album_name": "Generated album name (Maximum 7 words)",
                    "description": "Brief description of the album (Maximum 50 words)",
                    "image_ids": ["list of selected image IDs"],
                    "theme": "Identified theme of the album"
                }
                """
            ),
            tools=[ImageRetrievalTool(self.qdrant_client)],
            async_execution=False,
            callback=self.append_event_callback,
        )
