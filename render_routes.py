from fastapi import APIRouter
from event_queue import EVENT_QUEUE

router = APIRouter()


@router.post("/command/add")
async def add_command(data: dict):

    EVENT_QUEUE.append({
        "type": "command.add",
        "event": data
    })

    return {"success": True}