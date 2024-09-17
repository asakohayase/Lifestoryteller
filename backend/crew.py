import logging

from backend.agents import FamilyBookAgents

from crewai import Crew


from backend.tasks import FamilyBookTasks
from backend.utils.job_manager import append_event

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


class FamilyBookCrew:
    def __init__(self, job_id, qdrant_client):
        self.job_id = job_id
        self.qdrant_client = qdrant_client
        self.agents = FamilyBookAgents(qdrant_client)
        self.tasks = FamilyBookTasks(
            job_id=self.job_id, qdrant_client=self.qdrant_client
        )

    def setup_crew(self, image_data: bytes = None, theme_input: str = None):
        image_analysis_agent = self.agents.image_analysis_agent()
        album_creation_agent = self.agents.album_creation_agent()

        crew_tasks = []
        agents = []

        if image_data:
            image_analysis_agent = self.agents.image_analysis_agent()
            analyze_image_task = self.tasks.analyze_image_task(image_analysis_agent)
            crew_tasks.append(analyze_image_task)
            agents.append(image_analysis_agent)

        if theme_input:
            album_creation_agent = self.agents.album_creation_agent()
            create_album_task = self.tasks.create_album_task(
                album_creation_agent, theme_input
            )
            crew_tasks.append(create_album_task)
            agents.append(album_creation_agent)

        self.crew = Crew(
            agents=agents,
            tasks=crew_tasks,
            verbose=True,
        )

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
