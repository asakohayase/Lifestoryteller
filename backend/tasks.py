from crewai import Task, Agent
from textwrap import dedent


from job_manager import append_event
from utils.log_config import setup_logger


class CompanyResearchTasks:

    def __init__(self, job_id):
        self.job_id = job_id
        self.logger = setup_logger(__name__)

    def append_event_callback(self, task_output):
        self.logger.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    # def template_research(self, agent: Agent, tasks: list[Task]):
    #     return Task(
    #         description=dedent(f"""

    #             """),
    #         agent=agent,
    #         expected_output=dedent(
    #             """"""),
    #         callback=self.append_event_callback,
    #         context=tasks,
    #         output_json=
    #     )
