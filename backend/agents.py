from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI


class FamilyBookAgents:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")

    def manager_agent(self) -> Agent:
        return Agent(
            role="Family Book Project Manager",
            goal=f"""
                Oversee the creation of a comprehensive and engaging family book.
                Coordinate between image analysis and information gathering to create a cohesive narrative.
                """,
            backstory="""You are an experienced project manager with a keen eye for detail and a passion for 
            preserving family histories. Your expertise lies in organizing information and creating compelling 
            narratives from various data sources.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=True,
        )

    def image_analysis_agent(self) -> Agent:
        return Agent(
            role="Image Analysis Specialist",
            goal=f"""
                Analyze family photos to extract relevant information such as people, objects, locations, and estimated time periods.
                Provide detailed descriptions and potential context for each image.
                """,
            backstory="""You are an AI expert specializing in computer vision and image analysis. 
            Your skills allow you to extract intricate details from photos, recognizing faces, 
            objects, and even estimating the time period based on visual cues.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=True,
        )

    def search_agent(self) -> Agent:
        search = SerpAPIWrapper()
        return Agent(
            role="Family History Researcher",
            goal=f"""
                Research and gather additional information related to the family's history, including historical context, 
                genealogical data, and relevant world events.
                """,
            backstory="""You are a seasoned genealogist and historical researcher with a knack for uncovering 
            fascinating details about family histories. Your vast knowledge of historical events and ability to 
            connect seemingly unrelated information makes you invaluable in creating rich, contextual family narratives.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=True,
        )
