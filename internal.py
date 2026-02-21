from fastapi import APIRouter, Header, HTTPException
from event_queue import EVENT_QUEUE
import os

router = APIRouter()

INTERNAL_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET")


@router.get("/internal/events")
async def get_events(x_internal_secret: str = Header(None)):
    if x_internal_secret != INTERNAL_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    events = EVENT_QUEUE.copy()
    EVENT_QUEUE.clear()
    return events