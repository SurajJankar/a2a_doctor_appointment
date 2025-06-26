# =============================================================================
# agents/doctor_recommendation_agent/__main__.py
# =============================================================================
# Purpose:
# This is the main script that starts your DoctorRecommendationAgent server.
# It:
# - Declares the agent’s capabilities and skills
# - Sets up the A2A server with a task manager and agent
# - Starts listening on a specified host and port
#
# This script can be run directly from the command line:
#     python -m agents.doctor_recommendation_agent
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# A2A Server framework
from server.server import A2AServer

# Agent metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Task manager and recommendation agent
from agents.doctor_recommendation_agent.task_manager import AgentTaskManager
from agents.doctor_recommendation_agent.agent import DoctorRecommendationAgent

# CLI and logging
import click
import logging


# -----------------------------------------------------------------------------
# Setup logging to print info to the console
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Main Entry Function – Configurable via CLI
# -----------------------------------------------------------------------------

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10006, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the DoctorRecommendationAgent server.
    Run via: `python -m agents.doctor_recommendation_agent --host 0.0.0.0 --port 12345`
    """

    # Define capabilities (streaming not required)
    capabilities = AgentCapabilities(streaming=False)

    # Define the agent skill
    skill = AgentSkill(
        id="doctor_recommendation",
        name="Doctor Recommendation",
        description="Recommends a doctor based on symptoms and available days.",
        tags=["healthcare", "doctor", "recommendation", "hospital"],
        examples=[
            "I have chest pain.",
            "Which doctor is available on Monday?",
            "I have a skin allergy and want to visit today."
        ]
    )

    # Create agent metadata
    agent_card = AgentCard(
        name="DoctorRecommendationAgent",
        description="Recommends a doctor based on user symptoms and provides availability and location info.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=DoctorRecommendationAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=DoctorRecommendationAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )

    # Start the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=DoctorRecommendationAgent())
    )

    server.start()


# -----------------------------------------------------------------------------
# Only runs when executed directly via command line
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
