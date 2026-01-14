# twitch/medals.py

_stream_active = False  # chat-process state ONLY

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

# =========================
# STREAM LIFECYCLE (CHAT SIDE)
# =========================

def reset_medals():
    for key in medals:
        medals[key] = None
    global _stream_active
    _stream_active = True
    print("🟢 Stream LIVE — medals enabled & reset")


def end_stream():
    global _stream_active
    _stream_active = False
    for key in medals:
        medals[key] = None
    print("🔴 Stream OFFLINE — medals disabled & reset")

# =========================
# HANDLE MEDALS
# =========================

async def handle_medal(message, content: str) -> bool:
    word = content.lower().strip()
    if word.startswith("!"):
        word = word[1:]

    if word not in medals:
        return False

    if not _stream_active:
        await message.channel.send(
            "🔴 Stream is offline. Medals are disabled."
        )
        return True

    user = message.author.name

    if medals[word] is not None:
        await message.channel.send(
            f"{MEDAL_EMOTES[word]} {word.upper()} already claimed by @{medals[word]}!"
        )
        return True

    if user in medals.values():
        await message.channel.send(
            f"@{user} you already claimed a medal 😅"
        )
        return True

    medals[word] = user
    await message.channel.send(
        f"{MEDAL_EMOTES[word]} @{user} {MEDAL_TEXT[word]}"
    )
    return True
