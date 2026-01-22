import asyncio
from api import get_user_id

async def main():
    user_id = await get_user_id("itsfrosea")
    print("BROADCASTER USER ID:", user_id)

asyncio.run(main())
