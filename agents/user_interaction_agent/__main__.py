# =============================================================================
# agents/user_interaction_agent/__main__.py
# =============================================================================
# Purpose:
# This is the main script that starts your UserInteractionAgent server.
# It:
# - Declares the agent’s capabilities and skills
# - Sets up the A2A server with a task manager and agent
# - Starts listening on a specified host and port
#
# This script can be run directly from the command line:
#     python -m agents.user_interaction_agent
# =============================================================================

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

# A2A Server framework
from server.server import A2AServer

# Agent metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Task manager and polite user interaction agent
from agents.user_interaction_agent.task_manager import AgentTaskManager
from agents.user_interaction_agent.agent import UserInteractionAgent

# Command-line interface and logging
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
@click.option("--port", default=10005, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the UserInteractionAgent server.
    Run via: `python -m agents.user_interaction_agent --host 0.0.0.0 --port 12345`
    """

    # Define agent capabilities (no streaming needed for now)
    capabilities = AgentCapabilities(streaming=False)

    # Define what this agent is good at
    skill = AgentSkill(
        id="polite_user_interaction",
        name="Polite User Interaction",
        description="Interacts politely and respectfully with users, answering general queries.",
        tags=["conversation", "polite", "chat"],
        examples=["Hello, how are you?", "Can you assist me?", "Tell me something nice"]
    )

    # Construct the agent card (metadata)
    agent_card = AgentCard(
        name="UserInteractionAgent",
        description="An assistant agent that communicates with users in a polite and helpful manner.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=UserInteractionAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=UserInteractionAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill]
    )

    # Start the A2A server with this agent
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=UserInteractionAgent())
    )

    server.start()


# -----------------------------------------------------------------------------
# Only runs when executed directly via command line
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
