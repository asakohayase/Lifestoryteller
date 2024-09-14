from typing import List
from crewai import Agent
from langchain_openai import ChatOpenAI


class FamilyBookAgents:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")

    # def manager_agent(self) -> Agent:
    #     return Agent(
    #         role="Family Book Project Manager",
    #         goal=f"""
    #             Oversee the creation of a comprehensive and engaging family book.
    #             Coordinate between image analysis and information gathering to create a cohesive narrative.
    #             """,
    #         backstory="""You are an experienced project manager with a keen eye for detail and a passion for
    #         preserving family histories. Your expertise lies in organizing information and creating compelling
    #         narratives from various data sources.""",
    #         llm=self.llm,
    #         tools=[],
    #         verbose=True,
    #         allow_delegation=True,
    #     )

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

    # def description_generation_agent(self) -> Agent:
    #     return Agent(
    #         role="Description Generation Specialist",
    #         goal="""
    #         Generate detailed, engaging descriptions for family photos based on image analysis results.
    #         Capture the essence of each image, including people, objects, settings, and potential emotional significance.
    #     """,
    #         backstory="""
    #         You are a skilled writer with a talent for bringing images to life through words.
    #         Your expertise lies in crafting compelling narratives from visual information,
    #         helping to preserve and enhance family memories. You have a keen eye for detail
    #         and a deep understanding of human emotions and relationships.
    #     """,
    #         llm=self.llm,
    #         tools=[],  # You may want to add specific tools for description generation if needed
    #         verbose=True,
    #         allow_delegation=True,
    #     )

    def album_creation_agent(self) -> Agent:
        return Agent(
            role="Album Creation Specialist",
            goal=f"""The goal of the Album Creation Specialist is to create personalized albums based on user input. 
                The agent should understand the user's natural language descriptions and use vector search 
                to gather a maximum of 10 highly relevant images that align with the input. The agent’s goal is 
                to deliver a visually coherent, custom-tailored album, ensuring that the selected images reflect 
                the user's preferences and emotional tone. The agent should aim for accuracy, diversity, and creativity 
                in the image selection process.
                """,
            backstory="""The Album Creation Specialist was designed by a team of digital media and artificial intelligence experts 
            to help users effortlessly curate personal memories and experiences. Initially developed to assist in 
            professional photography projects, the agent’s ability to interpret human language and convert it into 
            aesthetically pleasing visual collections has evolved over time. It leverages cutting-edge natural 
            language processing and image vector search technologies to ensure that every album is a unique reflection 
            of the user’s vision. Whether it’s a wedding, a vacation, or a personal portfolio, the Album Creation Specialist 
            is dedicated to creating albums that resonate on a personal and artistic level.""",
            llm=self.llm,
            tools=[],
            verbose=True,
            allow_delegation=True,
        )
