# doctor_recommendation_agent/task_manager.py

from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TextPart, TaskStatus, TaskState
import logging

logger = logging.getLogger(__name__)

class AgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.awaiting_selection = {}  # session_id -> True/False

    def _get_user_query(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        logger.info(f"Processing task: {request.params.id}")

        task = await self.upsert_task(request.params)
        query = self._get_user_query(request)
        session_id = request.params.sessionId

        # Check if waiting for a follow-up selection
        if self.awaiting_selection.get(session_id, False):
            response = self.agent.get_doctor_details_from_selection(query, session_id)
            self.awaiting_selection[session_id] = False
        else:
            response = self.agent.get_recommendation(query, session_id)
            if "Please reply with the number" in response:
                self.awaiting_selection[session_id] = True

        # Format response
        agent_message = Message(role="agent", parts=[TextPart(text=response)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(agent_message)

        return SendTaskResponse(id=request.id, result=task)
