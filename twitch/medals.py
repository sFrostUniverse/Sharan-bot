# twitch/medals.py

from twitch.db import db

# =========================
# 🏁 CURRENT STREAM MEDALS
# =========================
medals = {
    "first": None,
    "second": None,
    "third": None,
}

MEDAL_EMOTES = {
    "first": "🥇",
    "second": "🥈",
    "third": "🥉",
}

MEDAL_TEXT = {
    "first": "got FIRST place! GG 🎉",
    "second": "got SECOND place! Nice!",
    "third": "got THIRD place! Clap clap 👏",
}

MEDAL_MAP = {
    "first": "gold",
    "second": "silver",
    "third": "bronze",
}

# =========================
# 🧹 MANUAL RESET (PER STREAM)
# =========================
def reset_medals():
    for key in medals:
        medals[key] = None
    print("♻️ Medals reset manually")

# =========================
# 🏅 HANDLE MEDAL CLAIM
# =========================
async def handle_medal(message, content: str) -> bool:
    word = content.lower().strip()
    if word.startswith("!"):
        word = word[1:]

    if word not in medals:
        return False

    user = message.author.name

    # Medal already claimed this stream
    if medals[word] is not None:
        await message.channel.send(
            f"{MEDAL_EMOTES[word]} {word.upper()} already claimed by @{medals[word]}!"
        )
        return True

    # User already claimed a medal this stream
    if user in medals.values():
        await message.channel.send(
            f"@{user} you already claimed a medal 😅"
        )
        return True

    # Assign medal for this stream
    medals[word] = user

    # Persist medal in DB (lifetime stats)
    db.add_medal(user, MEDAL_MAP[word])

    await message.channel.send(
        f"{MEDAL_EMOTES[word]} @{user} {MEDAL_TEXT[word]}"
    )
    return True

# =========================
# 📊 READ USER MEDALS (DB)
# =========================
def get_user_medals(username: str) -> dict:
    """
    Lifetime medal counts from database.
    """
    return db.get_medals(username)