from datetime import datetime
from typing import Callable
from langchain_openai import ChatOpenAI
from agents import FamilyBookAgents
from backend import tasks

from crewai import Crew

from backend.job_manager import append_event


class FamilyBookCrew:
    def __init__(self, job_id):
        self.job_id = job_id
        self.crew = None
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")

    def setup_crew(self):
        agents = FamilyBookAgents()
        # tasks =FamilyBookTasks(job_id=self.job_id)

        # manager_agent = agents.manager_agent()
        image_analysis_agent = agents.image_analysis_agent()
        # description_generation_agent = agents.description_generation_agent
        album_creation_agent = agents.album_creation_agent()

        analyze_image_task = tasks.analyze_image_task()
        generate_description_task = tasks.generate_description_task()
        create_album_task = tasks.create_album_task()

        self.crew = Crew(
            agents=[
                image_analysis_agent,
                album_creation_agent,
                # description_generation_agent,
            ],
            tasks=[analyze_image_task, generate_description_task, create_album_task],
            verbose=2,
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
