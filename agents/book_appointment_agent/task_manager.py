# =============================================================================
# agents/book_appointment_agent/task_manager.py
# =============================================================================
# Purpose:
# Connects BookAppointmentAgent to A2A task system
# =============================================================================

import logging
from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TextPart, TaskStatus, TaskState

logger = logging.getLogger(__name__)

class AgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    def _get_user_query(self, req: SendTaskRequest):
        return req.params.message.parts[0].text

    async def on_send_task(self, req: SendTaskRequest) -> SendTaskResponse:
        logger.info(f"Booking task: {req.params.id}")
        task = await self.upsert_task(req.params)
        query = self._get_user_query(req)
        sid = req.params.sessionId

        response_text = self.agent.book(query, sid)

        msg = Message(role="agent", parts=[TextPart(text=response_text)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(msg)

        return SendTaskResponse(id=req.id, result=task)
