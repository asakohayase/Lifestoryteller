from agents import FamilyBookAgents

from crewai import Crew


from tasks import FamilyBookTasks
from utils.job_manager import append_event


class FamilyBookCrew:
    def __init__(self, job_id, qdrant_client):
        self.job_id = job_id
        self.qdrant_client = qdrant_client
        self.agents = FamilyBookAgents(qdrant_client)
        self.tasks = FamilyBookTasks(
            job_id=self.job_id, qdrant_client=self.qdrant_client
        )

    def setup_crew(self, image_data=None, theme_input=None):
        if image_data:
            image_upload_agent = self.agents.image_upload_agent()
            upload_image_task = self.tasks.upload_image_task(
                image_upload_agent, image_data
            )
            self.crew = Crew(
                agents=[image_upload_agent], tasks=[upload_image_task], verbose=True
            )
        elif theme_input:
            album_creation_agent = self.agents.album_creation_agent()
            create_album_task = self.tasks.create_album_task(
                album_creation_agent, theme_input
            )
            self.crew = Crew(
                agents=[album_creation_agent], tasks=[create_album_task], verbose=True
            )
        else:
            raise ValueError("Either image_data or theme_input must be provided")

    def kickoff(self):
        if not self.crew:
            return "Crew not set up"

        append_event(self.job_id, "Task Started")
        try:
            results = self.crew.kickoff()
            append_event(self.job_id, "Task Complete")
            return results
        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return str(e)
