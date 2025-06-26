# =============================================================================
# agents/book_appointment_agent/__main__.py
# =============================================================================
# Purpose:
# This is the main script that starts your BookAppointmentAgent server.
# It:
# - Declares the agent’s capabilities and skills
# - Sets up the A2A server with a task manager and agent
# - Starts listening on a specified host and port
#
# This script can be run directly:
#     python -m agents.book_appointment_agent
# =============================================================================

from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.book_appointment_agent.task_manager import AgentTaskManager
from agents.book_appointment_agent.agent import BookAppointmentAgent
import click, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10007, help="Port number for the server")
def main(host, port):
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="book_appointment",
        name="Book Appointment",
        description="Books an appointment with a doctor based on ID and date",
        tags=["appointment", "book", "doctor"],
        examples=["Book an appointment with doc003 on 2025-07-05", "I want doc006 tomorrow"]
    )
    agent_card = AgentCard(
        name="BookAppointmentAgent",
        description="Books appointments with doctors based on user input",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=BookAppointmentAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=BookAppointmentAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=BookAppointmentAgent())
    )
    server.start()

if __name__ == "__main__":
    main()
