from crewai import Task, Agent
from textwrap import dedent


from job_manager import append_event
from utils.log_config import setup_logger


class FamilyBookTasks:

    def __init__(self, job_id):
        self.job_id = job_id
        self.logger = setup_logger(__name__)

    def append_event_callback(self, task_output):
        self.logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    def analyze_image_task(self, agent: Agent, image_data: bytes):
        return Task(
            description=dedent(
                f"""
                Analyze the provided image data. Extract key information including:
                1. Objects and people present in the image
                2. The setting or background
                3. Any notable actions or events occurring
                4. Estimated time period or date of the photo
                5. Any text visible in the image
                6. Overall mood or atmosphere of the image
                
                Provide a detailed analysis that can be used for generating a description and for categorizing the image.
            """
            ),
            agent=agent,
            expected_output=dedent(
                """
                {
                    "objects": ["list of identified objects"],
                    "people": ["list of identified people or types of people"],
                    "setting": "description of the setting",
                    "actions": ["list of notable actions or events"],
                    "time_period": "estimated time period or date",
                    "text": "any visible text in the image",
                    "mood": "overall mood or atmosphere",
                    "additional_notes": "any other relevant observations"
                }
                """
            ),
            callback=self.append_event_callback,
            context={"image_data": image_data},
            output_json=True,
        )

    def generate_description_task(
        self, agent: Agent, image_analysis: dict, image_metadata: dict
    ):
        return Task(
            description=dedent(
                f"""
                Generate a detailed and engaging description for a family photo based on the provided image analysis and metadata.
                
                Image Analysis:
                {image_analysis}
                
                Image Metadata:
                {image_metadata}
                
                Your task is to:
                1. Create a vivid, narrative description of the scene captured in the photo.
                2. Highlight key elements such as people, objects, setting, and apparent relationships or activities.
                3. Infer and describe the mood or emotional context of the photo.
                4. If possible, relate the photo to potential family history or significant events.
                5. Keep the description between 100-150 words.
            """
            ),
            agent=agent,
            expected_output=dedent(
                """
                {
                    "description": "The generated description of the photo",
                    "key_elements": ["List of key elements mentioned in the description"],
                    "inferred_mood": "The mood or emotional context inferred from the photo",
                    "potential_significance": "Any potential historical or familial significance of the photo"
                }
                """
            ),
            callback=self.append_event_callback,
            context={
                "image_analysis": image_analysis,
                "image_metadata": image_metadata,
            },
            output_json=True,
        )

    def create_album_task(self, agent: Agent, user_input: str, image_metadata: list):
        return Task(
            description=dedent(
                f"""
                Create an album based on the user's natural language input: "{user_input}"
                Use the provided image metadata to select relevant images for the album.
                Consider the theme, time period, people, and other relevant factors mentioned in the user input.
            """
            ),
            agent=agent,
            expected_output=dedent(
                """
                {
                    "album_name": "Generated album name",
                    "description": "Brief description of the album",
                    "image_ids": ["list of selected image IDs"],
                    "theme": "Identified theme of the album"
                }
                """
            ),
            callback=self.append_event_callback,
            context={"user_input": user_input, "image_metadata": image_metadata},
            output_json=True,
        )
