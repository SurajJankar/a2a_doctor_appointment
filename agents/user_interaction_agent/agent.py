# =============================================================================
# agents/user_interaction_agent/agent.py
# =============================================================================
# Purpose:
# - Acts as a hospital counter assistant
# - Responds politely to patients with clear and supportive information
# - Maintains session history
# =============================================================================

from autogen import AssistantAgent
from models.agent import AgentCard, AgentCapabilities, AgentSkill
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# In-memory session store
SESSION_STORE = {}

class UserInteractionAgent:
    SUPPORTED_CONTENT_TYPES = ["text/markdown", "text/plain"]

    def __init__(self):
        self.agent = self._create_agent()

    def _create_agent(self):
        config = {
            "llm_config": {
                "config_list": [
                    {
                        "model": "gpt-4",
                        "api_key": os.getenv("OPENAI_API_KEY")
                    }
                ],
                "temperature": 0.3
            }
        }

        return AssistantAgent(
            name="HospitalCounterAgent",
            system_message=(
                "You are a polite and professional hospital counter assistant. "
                "You greet patients warmly, guide them to the right department, "
                "answer queries about doctor availability, timings, and help them "
                "understand next steps. If you don't know something, kindly let them know."
            ),
            **config
        )

    async def invoke(self, query: str, session_id: str) -> str:
        """
        Generate a response to the user query using the AssistantAgent.
        
        Args:
            query (str): The user's message
            session_id (str): Session identifier for tracking
            
        Returns:
            str: The agent's response
        """
        # Create a message in the format expected by autogen
        message = {
            "role": "user",
            "content": query
        }
        
        # Use the async generate reply method
        response = await self.agent.a_generate_reply(messages=[message])
        
        # Return the response as string
        return str(response) if response else "I apologize, but I couldn't generate a response at the moment."

    def get_agent_card(self, host: str, port: int) -> AgentCard:
        return AgentCard(
            name="HospitalCounterAgent",
            description="A hospital front desk assistant that helps patients with directions, appointments, and general inquiries.",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=self.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=self.SUPPORTED_CONTENT_TYPES,
            capabilities=AgentCapabilities(streaming=False),
            skills=[
                AgentSkill(
                    id="hospital_desk_help",
                    name="Hospital Counter Help",
                    description="Assists patients at a hospital counter with polite conversation and helpful info.",
                    tags=["healthcare", "reception", "assistant"],
                    examples=[
                        "Where is the cardiology department?",
                        "Is Dr. Mehta available today?",
                        "How can I book an appointment?"
                    ]
                )
            ]
        )

    def store_message(self, session_id: str, message: str):
        """Store message in session."""
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = []
        SESSION_STORE[session_id].append(message)

    def get_session_history(self, session_id: str):
        """Get history for a session."""
        return SESSION_STORE.get(session_id, [])
