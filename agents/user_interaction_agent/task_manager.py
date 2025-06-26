# =============================================================================
# agents/user_interaction_agent/task_manager.py
# =============================================================================
# 🎯 Purpose:
# This file connects your OpenAI-powered UserInteractionAgent to the task-handling system.
# It inherits from InMemoryTaskManager to:
# - Receive a task from the user
# - Extract the user message
# - Ask the agent to respond politely
# - Save and return the agent's answer
# - Maintain session history
# =============================================================================


# -----------------------------------------------------------------------------
# 📚 Imports
# -----------------------------------------------------------------------------

import logging  # For logging important info and debug messages

# 🔁 In-memory task system from server
from server.task_manager import InMemoryTaskManager

# 🤖 Polite OpenAI-based assistant agent
from agents.user_interaction_agent.agent import UserInteractionAgent

# 📦 Data models
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, Task, TextPart, TaskStatus, TaskState


# -----------------------------------------------------------------------------
# 🪵 Logger setup
# -----------------------------------------------------------------------------
# This allows us to print logs like:
# INFO:agents.user_interaction_agent.task_manager:Handling task: 12345
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# AgentTaskManager
# -----------------------------------------------------------------------------

class AgentTaskManager(InMemoryTaskManager):
    """
    🧠 Connects the polite user interaction agent to the task system.

    - Inherits from InMemoryTaskManager
    - Handles incoming tasks via `on_send_task`
    - Maintains session history by sessionId
    """

    def __init__(self, agent: UserInteractionAgent):
        super().__init__()      # Parent constructor
        self.agent = agent      # Store the user interaction agent instance

    # -------------------------------------------------------------------------
    # 🔍 Extract the user's input string from the task request
    # -------------------------------------------------------------------------
    def _get_user_query(self, request: SendTaskRequest) -> str:
        """
        Extracts the user's message text from the request.

        Args:
            request (SendTaskRequest): Incoming user task

        Returns:
            str: The user's input text
        """
        return request.params.message.parts[0].text

    # -------------------------------------------------------------------------
    # 🧠 Main task execution logic
    # -------------------------------------------------------------------------
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Core logic to process an incoming task and respond politely.

        Steps:
        1. Save or update task
        2. Extract user message
        3. Call the polite agent to respond
        4. Store agent message in session history
        5. Update and return the completed task
        """

        logger.info(f"Handling task: {request.params.id}")

        # Step 1: Store the task in memory
        task = await self.upsert_task(request.params)

        # Step 2: Get user's message
        query = self._get_user_query(request)
        session_id = request.params.sessionId

        # Step 3: Log this input to session history
        self.agent.store_message(session_id, f"User: {query}")

        # Step 4: Get polite response from agent using the invoke method
        response_text = await self.agent.invoke(query, session_id)

        # Step 5: Store agent response in session
        self.agent.store_message(session_id, f"Agent: {response_text}")

        # Step 6: Convert to Message format
        agent_message = Message(
            role="agent",
            parts=[TextPart(text=response_text)]
        )

        # Step 7: Complete the task and add to history
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)

        # Step 8: Return updated task
        return SendTaskResponse(id=request.id, result=task)
