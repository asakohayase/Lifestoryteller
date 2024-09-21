from crewai import Agent
from langchain_openai import ChatOpenAI

from backend.tools import ImageRetrievalTool, ImageUploadTool


class FamilyBookAgents:
    def __init__(self, qdrant_client):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
        self.image_upload_tool = ImageUploadTool(qdrant_client)
        self.image_retrieval_tool = ImageRetrievalTool(qdrant_client)

    def image_upload_agent(self) -> Agent:
        return Agent(
            role="Image Upload Specialist",
            goal="Process and upload family photos efficiently and accurately.",
            backstory="You are an expert in digital image processing and database management. Your role is to ensure that all family photos are properly processed and securely stored in the database.",
            llm=self.llm,
            tools=[self.image_upload_tool],
            verbose=True,
            allow_delegation=False,
        )

    def album_creation_agent(self) -> Agent:
        return Agent(
            role="Album Creation Specialist",
            goal="Create personalized photo albums based on user descriptions, selecting the most relevant and meaningful images.",
            backstory="You are an AI with a keen eye for visual storytelling and a deep understanding of human emotions. Your expertise lies in interpreting user descriptions and curating photo collections that capture the essence of their memories.",
            llm=self.llm,
            tools=[self.image_retrieval_tool],
            verbose=True,
            allow_delegation=False,
        )

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
    #        allow_delegation=False,
    #     )
