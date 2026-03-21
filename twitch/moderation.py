import re
import time
from typing import Dict

# =========================
# 🚨 MODERATION CONFIG
# =========================
PARAGRAPH_LENGTH = 200
WARNING_COOLDOWN = 600  # seconds

LINK_REGEX = re.compile(
    r"(https?://|www\.|\.com|\.io|\.xyz|\.art)",
    re.IGNORECASE
)

# =========================
# 🧠 STATE
# =========================
first_message_seen: Dict[str, bool] = {}
last_warning_time: Dict[str, float] = {}


async def handle_first_message_moderation(bot, message) -> bool:
    """
    Returns True if moderation action was taken.
    """

    user = message.author.name
    content = message.content.strip()
    lower = content.lower()

    # Only check first message
    if first_message_seen.get(user):
        return False

    first_message_seen[user] = True

    is_link = bool(LINK_REGEX.search(lower))
    is_paragraph = len(content) >= PARAGRAPH_LENGTH

    if not (is_link or is_paragraph):
        return False

    now = time.time()
    last = last_warning_time.get(user, 0)

    if now - last < WARNING_COOLDOWN:
        return True

    await message.channel.send(
        f"⚠️ Hey @{user}, please keep first messages short and avoid links. Thanks 💜"
    )

    last_warning_time[user] = now

    print(
        f"[MODERATION] user={user} "
        f"reason={'link' if is_link else 'paragraph'} "
        f"length={len(content)}"
    )

    return True