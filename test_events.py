from fastapi import APIRouter
from event_queue import EVENT_QUEUE

router = APIRouter(prefix="/test")

@router.get("/follow")
async def test_follow():

    EVENT_QUEUE.append({
        "type": "channel.follow",
        "event": {
            "broadcaster_user_login": "itsfrosea",
            "user_name": "test_user"
        }
    })

    return {"queued": "follow event"}